// static/js/dashboard.js
// Ambil hasil dari sessionStorage, tampilkan 4 kartu metrik, confusion matrix
// (Chart.js), dan tabel hasil prediksi akhir.

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
    renderPredictionTable(result.prediction_table, true);
  } else if (result.rows) {
    // Mode 1 (batch): tidak ada label aktual, cuma prediksi
    renderPredictionTable(
      result.rows.map((r) => ({ raw_text: r.raw_text, actual: "-", predicted: r.prediction })),
      false
    );
  } else if (result.prediction) {
    // Mode 1 (manual single text)
    renderPredictionTable(
      [{ raw_text: result.raw_text, actual: "-", predicted: result.prediction }],
      false
    );
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

function renderPredictionTable(rows, showActual) {
  const tbody = document.getElementById("predictionTableBody");
  if (!rows || rows.length === 0) return;

  tbody.innerHTML = rows
    .map(
      (row) => `
    <tr>
      <td>${escapeHtml(row.raw_text)}</td>
      <td>${escapeHtml(String(row.actual))}</td>
      <td>${escapeHtml(String(row.predicted))}</td>
    </tr>`
    )
    .join("");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
