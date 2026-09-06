// static/js/preprocessing.js (VERSI FINAL — GANTI file preprocessing.js lamamu dengan ini)

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

    renderBalanceLine("balanceBefore", result.class_balance_before);
    renderBalanceLine("balanceAfter", result.class_balance_after);

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

function isNegativeLabel(label) {
  const s = String(label).toLowerCase();
  return s.includes("neg") || s === "0.0" || s === "0";
}

function renderBalanceLine(containerId, balanceObj) {
  const container = document.getElementById(containerId);
  if (!container || !balanceObj) return;
  container.innerHTML = Object.entries(balanceObj)
    .map(([label, count]) => {
      const cls = isNegativeLabel(label) ? "balance-neg" : "balance-pos";
      return `<span class="${cls} me-3">${escapeHtml(String(label))}: ${count}</span>`;
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
      const cls = label === "-" ? "text-neutral" : isNegativeLabel(label) ? "text-negative" : "text-positive";
      return `
      <tr>
        <td>${start + i + 1}</td>
        <td>${escapeHtml(row.raw_text)}</td>
        <td>${escapeHtml(row.clean_text)}</td>
        <td><span class="${cls}">${escapeHtml(String(label))}</span></td>
      </tr>`;
    })
    .join("");

  renderPagination();
}

function renderPagination() {
  const container = document.getElementById("previewPagination");
  const totalPages = Math.ceil(allPreviewRows.length / ROWS_PER_PAGE);
  if (totalPages <= 1) { container.innerHTML = ""; return; }

  let html = `<button class="arrow-btn" ${currentPage === 1 ? "disabled" : ""} onclick="renderPage(${currentPage - 1})"><i class="bi bi-chevron-left"></i></button>`;

  let pages = [];
  if (totalPages <= 5) {
    pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  } else {
    pages = [1, 2, "...", totalPages - 1, totalPages];
  }
  pages.forEach((p) => {
    if (p === "...") html += `<span class="page-dots">...</span>`;
    else html += `<button class="page-num ${p === currentPage ? "active" : ""}" onclick="renderPage(${p})">${p}</button>`;
  });

  html += `<button class="arrow-btn" ${currentPage === totalPages ? "disabled" : ""} onclick="renderPage(${currentPage + 1})"><i class="bi bi-chevron-right"></i></button>`;
  container.innerHTML = html;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}
