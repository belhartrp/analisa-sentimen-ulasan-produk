// static/js/upload.js (VERSI REDESIGN — GANTI file upload.js lamamu dengan ini)
// Perubahan: mode dipilih lewat 2 kartu (bukan toggle switch tunggal),
// ditambah file-chip preview, dan textarea manual selalu tampil.

const modeOption1 = document.getElementById("modeOption1");
const modeOption2 = document.getElementById("modeOption2");
const modeRadios = document.querySelectorAll('input[name="modeRadio"]');
const kSliderCard = document.getElementById("kSliderCard");
const kSlider = document.getElementById("kSlider");
const kValue = document.getElementById("kValue");
const fileInput = document.getElementById("fileInput");
const dropArea = document.getElementById("dropArea");
const fileChipWrapper = document.getElementById("fileChipWrapper");
const fileChipName = document.getElementById("fileChipName");
const fileChipSize = document.getElementById("fileChipSize");
const fileChipRemove = document.getElementById("fileChipRemove");
const formatHint = document.getElementById("formatHint");
const manualText = document.getElementById("manualText");
const submitBtn = document.getElementById("submitBtn");
const submitBtnText = document.getElementById("submitBtnText");
const submitBtnIcon = document.getElementById("submitBtnIcon");
const statusMsg = document.getElementById("statusMsg");

let selectedFile = null;

function isTrainingMode() {
  return document.querySelector('input[name="modeRadio"]:checked').value === "train";
}

function updateModeUI() {
  const training = isTrainingMode();
  modeOption1.classList.toggle("is-selected", !training);
  modeOption2.classList.toggle("is-selected", training);
  kSliderCard.style.display = training ? "block" : "none";
  formatHint.textContent = training
    ? "Format CSV (Mode 2): wajib 2 kolom (teks, label berisi Positif/Negatif) · Encoding UTF-8"
    : "Format CSV (Mode 1): cukup 1 kolom teks ulasan (label opsional) · Encoding UTF-8";
}

modeRadios.forEach((radio) => radio.addEventListener("change", updateModeUI));
modeOption1.addEventListener("click", () => { modeOption1.querySelector("input").checked = true; updateModeUI(); });
modeOption2.addEventListener("click", () => { modeOption2.querySelector("input").checked = true; updateModeUI(); });

kSlider.addEventListener("input", () => { kValue.textContent = kSlider.value; });

function showFileChip(file) {
  fileChipWrapper.classList.remove("d-none");
  fileChipName.textContent = file.name;
  fileChipSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + " MB";
}

fileChipRemove.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  fileChipWrapper.classList.add("d-none");
});

["dragover", "dragenter"].forEach((eventName) => {
  dropArea.addEventListener(eventName, (e) => { e.preventDefault(); dropArea.classList.add("dragover"); });
});
["dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, (e) => { e.preventDefault(); dropArea.classList.remove("dragover"); });
});
dropArea.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) { selectedFile = file; showFileChip(file); }
});
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) { selectedFile = file; showFileChip(file); }
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtnText.textContent = isLoading ? "Memproses..." : "Proses & Lanjutkan";
  submitBtnIcon.className = isLoading ? "bi bi-arrow-repeat ms-1 spin" : "bi bi-arrow-right ms-1";
}

submitBtn.addEventListener("click", async () => {
  const training = isTrainingMode();
  const text = manualText.value.trim();

  if (!selectedFile && !text) {
    statusMsg.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-circle me-1"></i>Unggah CSV atau isi teks manual terlebih dahulu.</span>`;
    return;
  }

  const formData = new FormData();
  if (selectedFile) formData.append("file", selectedFile);
  if (text) formData.append("manual_text", text);
  if (training) formData.append("k", kSlider.value);

  const endpoint = training ? "/api/train" : "/api/predict";
  setLoading(true);
  statusMsg.innerHTML = `<span class="text-muted"><i class="bi bi-arrow-repeat me-1"></i>Memproses data...</span>`;

  try {
    const res = await fetch(endpoint, { method: "POST", body: formData });
    const data = await res.json();

    if (data.status !== "ok") {
      setLoading(false);
      statusMsg.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle me-1"></i>${data.message}</span>`;
      return;
    }

    sessionStorage.setItem("lastResult", JSON.stringify(data));
    sessionStorage.setItem("lastMode", training ? "training" : "predict");

    statusMsg.innerHTML = `<span class="text-success"><i class="bi bi-check-circle me-1"></i>Berhasil! Mengarahkan ke halaman Preprocessing...</span>`;
    setTimeout(() => (window.location.href = "/preprocessing"), 700);
  } catch (err) {
    setLoading(false);
    statusMsg.innerHTML = `<span class="text-danger">Terjadi kesalahan: ${err.message}</span>`;
  }
});
