// ==========================================================
// AI Document Screening System - Frontend logic
// ==========================================================

const BACKEND_URL = "http://localhost:8000";

// ---- Element references ----
const docInput = document.getElementById("docInput");
const liveInput = document.getElementById("liveInput");
const docPreview = document.getElementById("docPreview");
const livePreview = document.getElementById("livePreview");

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const startCameraBtn = document.getElementById("startCameraBtn");
const captureBtn = document.getElementById("captureBtn");

const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("statusText");
const resultsSection = document.getElementById("resultsSection");

let docFile = null;
let liveFile = null;
let cameraStream = null;

// ---- THEME TOGGLE ----
function toggleTheme() {
  const html = document.documentElement;
  const btn = document.getElementById("themeToggle");

  if (html.getAttribute("data-theme") === "dark") {
    html.removeAttribute("data-theme");
    if (btn) btn.textContent = "🌙 Dark";
    localStorage.setItem("theme", "light");
  } else {
    html.setAttribute("data-theme", "dark");
    if (btn) btn.textContent = "☀️ Light";
    localStorage.setItem("theme", "dark");
  }
}

function initTheme() {
  const saved = localStorage.getItem("theme");
  const btn = document.getElementById("themeToggle");
  if (saved === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    if (btn) btn.textContent = "☀️ Light";
  }
}

document.addEventListener("DOMContentLoaded", initTheme);

// ---- VOICE ALERT ----
function voiceAlert(level) {
  if (level === "HIGH") {
    try {
      const msg = new SpeechSynthesisUtterance(
        "High Risk Detected. Manual verification required."
      );
      msg.lang = "en-IN";
      msg.rate = 1;
      speechSynthesis.speak(msg);
    } catch (err) {
      console.log("Voice alert not supported");
    }
  }
}

// ---- SOUND EFFECT ----
function playAlertSound() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = "sine";
    oscillator.frequency.value = 880; // Hz
    gainNode.gain.value = 0.3;

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.3);
  } catch (err) {
    console.log("Sound effect not supported");
  }
}

// ---- ANIMATED RISK GAUGE ----
function animateRiskGauge(score) {
  const circle = document.getElementById("riskGaugeCircle");
  const text = document.getElementById("riskGaugeText");
  if (!circle || !text) return;

  const maxOffset = 314; // circumference 2*pi*50 ≈ 314
  const targetOffset = maxOffset - (Math.min(score, 100) / 100) * maxOffset;

  circle.style.transition = "stroke-dashoffset 1.2s ease";
  circle.style.strokeDashoffset = targetOffset;
  text.textContent = Math.round(score);

  if (score < 30) {
    circle.style.stroke = "#2e7d32";
  } else if (score < 60) {
    circle.style.stroke = "#f9a825";
  } else {
    circle.style.stroke = "#c0392b";
  }
}

// ---- Document upload preview ----
docInput.addEventListener("change", (e) => {
  docFile = e.target.files[0];
  if (docFile) {
    docPreview.src = URL.createObjectURL(docFile);
  }
});

// ---- Live photo upload preview ----
liveInput.addEventListener("change", (e) => {
  liveFile = e.target.files[0];
  if (liveFile) {
    livePreview.src = URL.createObjectURL(liveFile);
    video.style.display = "none";
  }
});

// ---- Camera capture ----
startCameraBtn.addEventListener("click", async () => {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = cameraStream;
    video.style.display = "block";
    livePreview.src = "";
    captureBtn.disabled = false;
  } catch (err) {
    alert("Could not access camera: " + err.message);
  }
});

captureBtn.addEventListener("click", () => {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    liveFile = new File([blob], "live_capture.jpg", { type: "image/jpeg" });
    livePreview.src = URL.createObjectURL(liveFile);
  }, "image/jpeg");

  // Stop the camera after capture
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
  }
  video.style.display = "none";
  captureBtn.disabled = true;
});

// ---- Analyze button ----
analyzeBtn.addEventListener("click", async () => {
  if (!docFile || !liveFile) {
    alert("Please provide both a document image and a live photo.");
    return;
  }

  statusText.textContent = "Processing, please wait...";
  analyzeBtn.disabled = true;
  resultsSection.style.display = "none";

  const formData = new FormData();
  formData.append("doc_image", docFile);
  formData.append("live_image", liveFile);

  try {
    const response = await fetch(`${BACKEND_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const result = await response.json();
    renderResults(result);
    statusText.textContent = "Analysis complete.";
  } catch (err) {
    statusText.textContent = "Error: " + err.message;
    alert("Analysis failed: " + err.message);
  } finally {
    analyzeBtn.disabled = false;
  }
});

// ---- Render results in the UI ----
function renderResults(result) {
  resultsSection.style.display = "block";

  const riskLevelEl = document.getElementById("riskLevel");
  riskLevelEl.textContent = result.risk_level || "--";
  riskLevelEl.className = "risk-badge " + (result.risk_level || "");

  // 🔥 VOICE ALERT + SOUND EFFECT
  voiceAlert(result.risk_level);
  if (result.risk_level === "HIGH") {
    playAlertSound();
  }

  const riskScore = result.risk_score ?? 0;
  document.getElementById("riskScore").textContent = riskScore;
  animateRiskGauge(riskScore);

  document.getElementById("documentType").textContent = result.document_type || "--";
  document.getElementById("faceMatch").textContent = result.face_match ? "Match" : "No Match";
  document.getElementById("similarity").textContent = result.similarity ?? "--";
  document.getElementById("livenessResult").textContent = result.liveness_passed
    ? "Passed"
    : "Failed";
  document.getElementById("tamperScore").textContent = result.tamper_score ?? "--";
  document.getElementById("noiseScore").textContent = result.noise_score ?? "--";
  document.getElementById("blockchainHash").textContent = result.blockchain_hash || "--";

  document.getElementById("extractedFields").textContent = JSON.stringify(
    result.fields || {},
    null,
    2
  );

  const errorsList = document.getElementById("errorsList");
  errorsList.innerHTML = "";
  if (result.errors && result.errors.length > 0) {
    result.errors.forEach((err) => {
      const li = document.createElement("li");
      li.textContent = err;
      errorsList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = "No validation errors found.";
    errorsList.appendChild(li);
  }

  const heatmapImage = document.getElementById("heatmapImage");
  if (result.heatmap) {
    heatmapImage.src = "data:image/jpeg;base64," + result.heatmap;
    heatmapImage.style.display = "block";
  } else {
    heatmapImage.style.display = "none";
  }

  const pdfLink = document.getElementById("pdfLink");
  const qrLink = document.getElementById("qrLink");
  pdfLink.href = result.pdf_report ? BACKEND_URL + result.pdf_report : "#";
  qrLink.href = result.qr_code ? BACKEND_URL + result.qr_code : "#";

  resultsSection.scrollIntoView({ behavior: "smooth" });
}