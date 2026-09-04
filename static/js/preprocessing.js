// static/js/preprocessing.js
// Ambil hasil dari sessionStorage (dikirim dari halaman upload.js),
// lalu tampilkan tabel Raw Text vs Clean Text.

document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("lastResult");
  const mode = sessionStorage.getItem("lastMode");
  const tbody = document.getElementById("previewTableBody");
  const balanceInfo = document.getElementById("balanceInfo");

  if (!raw) return; // biarkan tampil pesan default dari HTML

  const data = JSON.parse(raw);
  const result = data.result;
  let rows = [];

  if (mode === "training") {
    rows = result.preview_rows || [];
    if (result.class_balance_before && result.class_balance_after) {
      balanceInfo.classList.remove("d-none");
      balanceInfo.innerHTML =
        `<strong>Distribusi kelas sebelum undersampling:</strong> ${JSON.stringify(result.class_balance_before)}<br>` +
        `<strong>Distribusi kelas sesudah undersampling:</strong> ${JSON.stringify(result.class_balance_after)}`;
    }
  } else {
    const items = result.rows || [result]; // batch atau single
    rows = items.map((item) => ({
      raw_text: item.raw_text,
      clean_text: item.clean_text,
      label: item.prediction || "-",
    }));
  }

  if (rows.length === 0) return;

  tbody.innerHTML = rows
    .map(
      (row, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(row.raw_text)}</td>
      <td>${escapeHtml(row.clean_text)}</td>
      <td>${escapeHtml(row.label || "-")}</td>
    </tr>`
    )
    .join("");
});

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
