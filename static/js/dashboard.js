// static/js/dashboard.js (VERSI UPDATE — GANTI file dashboard.js lamamu dengan ini)
// Menampilkan: metrik utama, confusion matrix, tabel prediksi + filter,
// kurva K, komparasi KNN vs WKNN, explainable AI (tetangga), donut sentimen,
// dan top keywords per sentimen.

let fullPredictionRows = []; // dipakai untuk filter tabel

document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("lastResult");
  const mode = sessionStorage.getItem("lastMode");
  if (!raw) return;

  const data = JSON.parse(raw);
  const result = data.result;

  if (mode === "training" && result.metrics) {
    document.getElementById("metricAccuracy").textContent = (result.metrics.accuracy * 100).toFixed(2) + "%";
    document.getElementById("metricPrecision").textContent = (result.metrics.precision * 100).toFixed(2) + "%";
    document.getElementById("metricRecall").textContent = (result.metrics.recall * 100).toFixed(2) + "%";
    document.getElementById("metricF1").textContent = (result.metrics.f1_score * 100).toFixed(2) + "%";

    renderConfusionMatrix(result.confusion_matrix);

    fullPredictionRows = result.prediction_table || [];
    renderPredictionTable(fullPredictionRows);
    setupFilterButtons();

    if (result.k_curve_chart) renderKCurve(result.k_curve_chart);
    if (result.comparison_chart) renderComparisonChart(result.comparison_chart);
    if (result.class_balance_before) renderSentimentDonut(result.class_balance_before);
    if (result.top_keywords) renderTopKeywords(result.top_keywords);
  } else if (result.rows) {
    // Mode 1 (batch)
    fullPredictionRows = result.rows.map((r) => ({
      raw_text: r.raw_text,
      actual: "-",
      predicted: r.prediction,
      confidence: r.confidence_score,
    }));
    renderPredictionTable(fullPredictionRows);
    setupFilterButtons();
  } else if (result.prediction) {
    // Mode 1 (manual single text) -> render Explainable AI table
    fullPredictionRows = [
      { raw_text: result.raw_text, actual: "-", predicted: result.prediction, confidence: result.confidence_score },
    ];
    renderPredictionTable(fullPredictionRows);
    if (result.neighbors) renderNeighborTable(result.neighbors);
  }
});

function renderConfusionMatrix(cm) {
  if (!cm) return;
  const ctx = document.getElementById("confusionChart");
  const labels = cm.labels;
  const matrix = cm.matrix;

  const datasets = labels.map((label, i) => ({
    label: `Aktual: ${label}`,
    data: matrix[i],
    backgroundColor: i === 0 ? "#dc3545" : "#198754",
  }));

  new Chart(ctx, {
    type: "bar",
    data: { labels: labels.map((l) => `Prediksi: ${l}`), datasets },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Confusion Matrix" } },
      scales: { y: { beginAtZero: true, title: { display: true, text: "Jumlah Data" } } },
    },
  });
}

function renderKCurve(kCurve) {
  const ctx = document.getElementById("kCurveChart");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: kCurve.k_values.map((k) => `K=${k}`),
      datasets: [
        {
          label: "Akurasi WKNN",
          data: kCurve.accuracies.map((a) => (a * 100).toFixed(2)),
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13,110,253,0.15)",
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      scales: { y: { title: { display: true, text: "Akurasi (%)" } } },
    },
  });
}

function renderComparisonChart(comparison) {
  const ctx = document.getElementById("comparisonChart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: comparison.labels,
      datasets: [
        { label: "KNN Standar", data: comparison.knn.map((v) => (v * 100).toFixed(2)), backgroundColor: "#6c757d" },
        { label: "WKNN", data: comparison.wknn.map((v) => (v * 100).toFixed(2)), backgroundColor: "#0d6efd" },
      ],
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true, title: { display: true, text: "Persentase (%)" } } },
    },
  });
}

function renderSentimentDonut(classBalance) {
  const ctx = document.getElementById("sentimentDonutChart");
  const labels = Object.keys(classBalance);
  const values = Object.values(classBalance);
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: labels.map((l) => (l.toLowerCase().includes("neg") ? "#dc3545" : "#198754")) }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } },
  });
}

function renderTopKeywords(topKeywords) {
  Object.entries(topKeywords).forEach(([label, words]) => {
    const isNegative = label.toLowerCase().includes("neg");
    const canvasId = isNegative ? "negativeKeywordsChart" : "positiveKeywordsChart";
    const ctx = document.getElementById(canvasId);
    if (!ctx || !words || words.length === 0) return;

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: words.map((w) => w.word),
        datasets: [
          {
            label: `Skor TF-IDF (${label})`,
            data: words.map((w) => w.score),
            backgroundColor: isNegative ? "#dc3545" : "#198754",
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { display: false } },
      },
    });
  });
}

function renderNeighborTable(neighbors) {
  const tbody = document.getElementById("neighborTableBody");
  if (!neighbors || neighbors.length === 0) return;
  tbody.innerHTML = neighbors
    .map(
      (n, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(n.label)}</td>
      <td>${n.distance}</td>
      <td>${n.weight}</td>
    </tr>`
    )
    .join("");
}

function renderPredictionTable(rows) {
  const tbody = document.getElementById("predictionTableBody");
  if (!rows || rows.length === 0) return;
  tbody.innerHTML = rows
    .map(
      (row) => `
    <tr>
      <td>${escapeHtml(row.raw_text)}</td>
      <td>${escapeHtml(String(row.actual))}</td>
      <td>${escapeHtml(String(row.predicted))}</td>
      <td>${row.confidence != null ? row.confidence + "%" : "-"}</td>
    </tr>`
    )
    .join("");
}

function setupFilterButtons() {
  const buttons = document.querySelectorAll("[data-filter]");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.dataset.filter;
      const filtered =
        filter === "all" ? fullPredictionRows : fullPredictionRows.filter((r) => r.predicted === filter);
      renderPredictionTable(filtered);
    });
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
