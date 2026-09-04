// static/js/upload.js
// Logika Halaman 1: toggle mode, drag-and-drop CSV, slider K, submit ke backend.

const modeToggle = document.getElementById("modeToggle");
const modeLabel = document.getElementById("modeLabel");
const kSliderCard = document.getElementById("kSliderCard");
const kSlider = document.getElementById("kSlider");
const kValue = document.getElementById("kValue");
const fileInput = document.getElementById("fileInput");
const dropArea = document.getElementById("dropArea");
const manualText = document.getElementById("manualText");
const submitBtn = document.getElementById("submitBtn");
const statusMsg = document.getElementById("statusMsg");

let selectedFile = null;

modeToggle.addEventListener("change", () => {
  const isTrainingMode = modeToggle.checked;
  modeLabel.textContent = isTrainingMode
    ? "Mode 2: Latih Dataset Saya (Custom Training)"
    : "Mode 1: Gunakan Model Bawaan (Pre-Trained)";
  kSliderCard.style.display = isTrainingMode ? "block" : "none";
});

kSlider.addEventListener("input", () => {
  kValue.textContent = kSlider.value;
});

["dragover", "dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, (e) => e.preventDefault());
});
dropArea.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) {
    selectedFile = file;
    statusMsg.innerHTML = `<span class="text-success">File terpilih: ${file.name}</span>`;
  }
});
fileInput.addEventListener("change", (e) => {
  selectedFile = e.target.files[0];
});

submitBtn.addEventListener("click", async () => {
  const isTrainingMode = modeToggle.checked;
  const text = manualText.value.trim();

  if (!selectedFile && !text) {
    statusMsg.innerHTML = `<span class="text-danger">Unggah CSV atau isi teks manual terlebih dahulu.</span>`;
    return;
  }

  const formData = new FormData();
  if (selectedFile) formData.append("file", selectedFile);
  if (text) formData.append("manual_text", text);
  if (isTrainingMode) formData.append("k", kSlider.value);

  const endpoint = isTrainingMode ? "/api/train" : "/api/predict";
  statusMsg.innerHTML = `<span class="text-muted">Memproses...</span>`;

  try {
    const res = await fetch(endpoint, { method: "POST", body: formData });
    const data = await res.json();

    if (data.status !== "ok") {
      statusMsg.innerHTML = `<span class="text-danger">${data.message}</span>`;
      return;
    }

    sessionStorage.setItem("lastResult", JSON.stringify(data));
    sessionStorage.setItem("lastMode", isTrainingMode ? "training" : "predict");

    statusMsg.innerHTML = `<span class="text-success">Berhasil diproses! Mengarahkan ke halaman Preprocessing...</span>`;
    setTimeout(() => (window.location.href = "/preprocessing"), 800);
  } catch (err) {
    statusMsg.innerHTML = `<span class="text-danger">Terjadi kesalahan: ${err.message}</span>`;
  }
});
