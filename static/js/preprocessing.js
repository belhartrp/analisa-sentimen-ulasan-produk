// static/js/preprocessing.js (VERSI REDESIGN — GANTI file preprocessing.js lamamu dengan ini)
// Tambahan: ringkasan dataset (kartu statistik) + pagination tabel (5 baris/halaman).

const ROWS_PER_PAGE = 5;
let allPreviewRows = [];
let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("lastResult");
  const mode = sessionStorage.getItem("lastMode");
  if (!raw) return;

  const data = JSON.parse(raw);
  const result = data.result;

  if (mode === "training") {
    document.getElementById("summarySection").classList.remove("d-none");

    const totalBefore = Object.values(result.class_balance_before || {}).reduce((a, b) => a + b, 0);
    const totalAfter = Object.values(result.class_balance_after || {}).reduce((a, b) => a + b, 0);

    document.getElementById("statTotal").textContent = totalBefore;
    document.getElementById("statAfter").textContent = totalAfter;
    document.getElementById("statK").textContent = result.metrics ? result.metrics.k : "-";

    renderBalanceChips("balanceBefore", result.class_balance_before);
    renderBalanceChips("balanceAfter", result.class_balance_after);

    allPreviewRows = result.preview_rows || [];
  } else {
    const items = result.rows || [result];
    allPreviewRows = items.map((item) => ({
      raw_text: item.raw_text,
      clean_text: item.clean_text,
      label: item.prediction || "-",
    }));
  }

  renderPage(1);
});

function renderBalanceChips(containerId, balanceObj) {
  const container = document.getElementById(containerId);
  if (!container || !balanceObj) return;
  container.innerHTML = Object.entries(balanceObj)
    .map(([label, count]) => {
      const isNeg = String(label).toLowerCase().includes("neg") || label === "0.0" || label === "0";
      const cls = isNeg ? "pill-negative" : "pill-positive";
      return `<span class="pill-badge ${cls}">${escapeHtml(String(label))}: ${count}</span>`;
    })
    .join("");
}

function renderPage(page) {
  currentPage = page;
  const tbody = document.getElementById("previewTableBody");
  if (allPreviewRows.length === 0) return;

  const start = (page - 1) * ROWS_PER_PAGE;
  const rows = allPreviewRows.slice(start, start + ROWS_PER_PAGE);

  tbody.innerHTML = rows
    .map((row, i) => {
      const label = row.label ?? "-";
      const isNeg = String(label).toLowerCase().includes("neg") || label === "0.0" || label === "0";
      const pillCls = label === "-" ? "pill-neutral" : isNeg ? "pill-negative" : "pill-positive";
      return `
      <tr>
        <td>${start + i + 1}</td>
        <td>${escapeHtml(row.raw_text)}</td>
        <td>${escapeHtml(row.clean_text)}</td>
        <td><span class="pill-badge ${pillCls}">${escapeHtml(String(label))}</span></td>
      </tr>`;
    })
    .join("");

  renderPagination();
}

function renderPagination() {
  const container = document.getElementById("previewPagination");
  const totalPages = Math.ceil(allPreviewRows.length / ROWS_PER_PAGE);
  if (totalPages <= 1) { container.innerHTML = ""; return; }

  const start = (currentPage - 1) * ROWS_PER_PAGE + 1;
  const end = Math.min(currentPage * ROWS_PER_PAGE, allPreviewRows.length);

  let buttons = `<button ${currentPage === 1 ? "disabled" : ""} onclick="renderPage(${currentPage - 1})"><i class="bi bi-chevron-left"></i></button>`;
  const maxButtons = 5;
  let pages = [];
  if (totalPages <= maxButtons) {
    pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  } else {
    pages = [1, 2, "...", totalPages - 1, totalPages];
  }
  pages.forEach((p) => {
    if (p === "...") { buttons += `<span class="px-1">...</span>`; }
    else { buttons += `<button class="${p === currentPage ? "active" : ""}" onclick="renderPage(${p})">${p}</button>`; }
  });
  buttons += `<button ${currentPage === totalPages ? "disabled" : ""} onclick="renderPage(${currentPage + 1})"><i class="bi bi-chevron-right"></i></button>`;

  container.innerHTML = `
    <div class="page-info">Menampilkan ${start}-${end} dari ${allPreviewRows.length} data</div>
    <div class="page-btns">${buttons}</div>
  `;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
