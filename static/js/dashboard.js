// static/js/dashboard.js (VERSI FINAL — GANTI file dashboard.js lamamu dengan ini)

const PRED_ROWS_PER_PAGE = 5;
let fullPredictionRows = [];
let filteredPredictionRows = [];
let predictionPage = 1;

document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("lastResult");
  const mode = sessionStorage.getItem("lastMode");
  if (!raw) return;

  const data = JSON.parse(raw);
  const result = data.result;

  if (mode === "training" && result.metrics) {
    unlockAcademicSection();

    document.getElementById("metricAccuracy").textContent = (result.metrics.accuracy * 100).toFixed(2) + "%";
    document.getElementById("metricPrecision").textContent = (result.metrics.precision * 100).toFixed(2) + "%";
    document.getElementById("metricRecall").textContent = (result.metrics.recall * 100).toFixed(2) + "%";
    document.getElementById("metricF1").textContent = (result.metrics.f1_score * 100).toFixed(2) + "%";

    renderConfusionMatrix(result.confusion_matrix);

    fullPredictionRows = result.prediction_table || [];
    filteredPredictionRows = fullPredictionRows;
    renderPredictionPage(1);
    setupFilterButtons();

    if (result.k_curve_chart) renderKCurve(result.k_curve_chart);
    if (result.comparison_chart) renderComparisonChart(result.comparison_chart);
    if (result.class_balance_before) renderSentimentDonut(result.class_balance_before);
    if (result.top_keywords) renderTopKeywords(result.top_keywords);
  } else {
    lockAcademicSection();

    if (result.rows) {
      fullPredictionRows = result.rows.map((r) => ({
        raw_text: r.raw_text, actual: "-", predicted: r.prediction, confidence: r.confidence_score,
      }));
    } else if (result.prediction) {
      fullPredictionRows = [{ raw_text: result.raw_text, actual: "-", predicted: result.prediction, confidence: result.confidence_score }];
      if (result.neighbors) renderNeighborTable(result.neighbors);
    }
    filteredPredictionRows = fullPredictionRows;
    renderPredictionPage(1);
    setupFilterButtons();
  }
});

function isNegativeLabel(label) {
  const s = String(label).toLowerCase();
  return s.includes("neg") || s === "0.0" || s === "0";
}

function lockAcademicSection() {
  document.getElementById("mode1Notice").classList.remove("d-none");
  document.getElementById("academicSection").classList.add("section-locked");
}

function unlockAcademicSection() {
  document.getElementById("mode1Notice").classList.add("d-none");
  document.getElementById("academicSection").classList.remove("section-locked");
}

function renderConfusionMatrix(cm) {
  if (!cm) return;
  const ctx = document.getElementById("confusionChart");
  const labels = cm.labels;
  const matrix = cm.matrix;
  const datasets = labels.map((label, i) => ({
    label: `Aktual: ${label}`,
    data: matrix[i],
    backgroundColor: isNegativeLabel(label) ? "#e5484d" : "#1cb15a",
    borderRadius: 6,
  }));
  new Chart(ctx, {
    type: "bar",
    data: { labels: labels.map((l) => `Prediksi: ${l}`), datasets },
    options: { responsive: true, scales: { y: { beginAtZero: true } } },
  });
}

function renderKCurve(kCurve) {
  const ctx = document.getElementById("kCurveChart");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: kCurve.k_values.map((k) => `K=${k}`),
      datasets: [{
        label: "Akurasi WKNN",
        data: kCurve.accuracies.map((a) => (a * 100).toFixed(2)),
        borderColor: "#1cb15a",
        backgroundColor: "rgba(28,177,90,0.12)",
        fill: true, tension: 0.35,
      }],
    },
    options: { responsive: true, scales: { y: { title: { display: true, text: "Akurasi (%)" } } } },
  });
}

function renderComparisonChart(comparison) {
  const ctx = document.getElementById("comparisonChart");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: comparison.labels,
      datasets: [
        { label: "KNN Standar", data: comparison.knn.map((v) => (v * 100).toFixed(2)), backgroundColor: "#c7d1cb", borderRadius: 6 },
        { label: "WKNN", data: comparison.wknn.map((v) => (v * 100).toFixed(2)), backgroundColor: "#1cb15a", borderRadius: 6 },
      ],
    },
    options: { responsive: true, scales: { y: { beginAtZero: true, title: { display: true, text: "Persentase (%)" } } } },
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
      datasets: [{ data: values, backgroundColor: labels.map((l) => (isNegativeLabel(l) ? "#e5484d" : "#1cb15a")), borderWidth: 0 }],
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, cutout: "65%" },
  });
}

function renderTopKeywords(topKeywords) {
  Object.entries(topKeywords).forEach(([label, words]) => {
    const isNegative = isNegativeLabel(label);
    const canvasId = isNegative ? "negativeKeywordsChart" : "positiveKeywordsChart";
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (!words || words.length === 0) {
      ctx.parentElement.innerHTML = `<p class="text-muted small text-center py-3">Belum ada data kata kunci untuk kelas ini (kemungkinan data kelas ini terlalu sedikit).</p>`;
      return;
    }
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: words.map((w) => w.word),
        datasets: [{ data: words.map((w) => w.score), backgroundColor: isNegative ? "#e5484d" : "#1cb15a", borderRadius: 4 }],
      },
      options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } } },
    });
  });
}

function renderNeighborTable(neighbors) {
  const tbody = document.getElementById("neighborTableBody");
  if (!neighbors || neighbors.length === 0) return;
  tbody.innerHTML = neighbors
    .map((n, i) => {
      const cls = isNegativeLabel(n.label) ? "text-negative" : "text-positive";
      return `
      <tr>
        <td>${i + 1}</td>
        <td><span class="${cls}">${escapeHtml(String(n.label))}</span></td>
        <td>${n.distance}</td>
        <td>${n.weight}</td>
      </tr>`;
    })
    .join("");
}

function renderPredictionPage(page) {
  predictionPage = page;
  const tbody = document.getElementById("predictionTableBody");
  if (filteredPredictionRows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><i class="bi bi-inbox"></i>Belum ada hasil.</div></td></tr>`;
    document.getElementById("predictionPagination").innerHTML = "";
    return;
  }

  const start = (page - 1) * PRED_ROWS_PER_PAGE;
  const rows = filteredPredictionRows.slice(start, start + PRED_ROWS_PER_PAGE);

  tbody.innerHTML = rows
    .map((row) => {
      const cls = row.predicted === "-" ? "text-neutral" : isNegativeLabel(row.predicted) ? "text-negative" : "text-positive";
      return `
      <tr>
        <td>${escapeHtml(row.raw_text)}</td>
        <td>${escapeHtml(String(row.actual))}</td>
        <td><span class="${cls}">${escapeHtml(String(row.predicted))}</span></td>
        <td>${row.confidence != null ? row.confidence + "%" : "-"}</td>
      </tr>`;
    })
    .join("");

  renderPredictionPagination();
}

function renderPredictionPagination() {
  const container = document.getElementById("predictionPagination");
  const totalPages = Math.ceil(filteredPredictionRows.length / PRED_ROWS_PER_PAGE);
  if (totalPages <= 1) { container.innerHTML = ""; return; }

  let html = `<button class="arrow-btn" ${predictionPage === 1 ? "disabled" : ""} onclick="renderPredictionPage(${predictionPage - 1})"><i class="bi bi-chevron-left"></i></button>`;
  for (let p = 1; p <= totalPages; p++) {
    if (p <= 3 || p === totalPages || Math.abs(p - predictionPage) <= 1) {
      html += `<button class="page-num ${p === predictionPage ? "active" : ""}" onclick="renderPredictionPage(${p})">${p}</button>`;
    } else if (p === 4 && totalPages > 5) {
      html += `<span class="page-dots">...</span>`;
    }
  }
  html += `<button class="arrow-btn" ${predictionPage === totalPages ? "disabled" : ""} onclick="renderPredictionPage(${predictionPage + 1})"><i class="bi bi-chevron-right"></i></button>`;
  container.innerHTML = html;
}

function setupFilterButtons() {
  const buttons = document.querySelectorAll("[data-filter]");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.dataset.filter;
      filteredPredictionRows = filter === "all" ? fullPredictionRows : fullPredictionRows.filter((r) => r.predicted === filter);
      renderPredictionPage(1);
    });
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
