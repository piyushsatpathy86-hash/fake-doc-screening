// ==========================================================
// AI Document Screening System - Frontend logic (Null-safe)
// ==========================================================

const BACKEND_URL = "";

// ---- Safe element getter ----
function getEl(id) {
  return document.getElementById(id);
}

// ---- Element references (safe) ----
const docInput = getEl("docInput");
const liveInput = getEl("liveInput");
const docPreview = getEl("docPreview");
const livePreview = getEl("livePreview");

const video = getEl("video");
const canvas = getEl("canvas");
const startCameraBtn = getEl("startCameraBtn");
const captureBtn = getEl("captureBtn");

const analyzeBtn = getEl("analyzeBtn");
const statusText = getEl("statusText");
const resultsSection = getEl("resultsSection");

let docFile = null;
let liveFile = null;
let cameraStream = null;

// ---- THEME TOGGLE ----
function toggleTheme() {
  const html = document.documentElement;
  const btn = getEl("themeToggle");

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
  const btn = getEl("themeToggle");
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
    oscillator.frequency.value = 880;
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
  const circle = getEl("riskGaugeCircle");
  const text = getEl("riskGaugeText");
  if (!circle || !text) return;

  const maxOffset = 314;
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
if (docInput) {
  docInput.addEventListener("change", (e) => {
    docFile = e.target.files[0];
    if (docFile && docPreview) {
      docPreview.src = URL.createObjectURL(docFile);
    }
  });
}

// ---- Live photo upload preview ----
if (liveInput) {
  liveInput.addEventListener("change", (e) => {
    liveFile = e.target.files[0];
    if (liveFile && livePreview) {
      livePreview.src = URL.createObjectURL(liveFile);
      if (video) video.style.display = "none";
    }
  });
}

// ---- Camera capture ----
if (startCameraBtn) {
  startCameraBtn.addEventListener("click", async () => {
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (video) {
        video.srcObject = cameraStream;
        video.style.display = "block";
      }
      if (livePreview) livePreview.src = "";
      if (captureBtn) captureBtn.disabled = false;
    } catch (err) {
      alert("Could not access camera: " + err.message);
    }
  });
}

if (captureBtn) {
  captureBtn.addEventListener("click", () => {
    if (!canvas || !video) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      liveFile = new File([blob], "live_capture.jpg", { type: "image/jpeg" });
      if (livePreview) livePreview.src = URL.createObjectURL(liveFile);
    }, "image/jpeg");

    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
    }
    if (video) video.style.display = "none";
    if (captureBtn) captureBtn.disabled = true;
  });
}

// ---- Analyze button ----
if (analyzeBtn) {
  analyzeBtn.addEventListener("click", async () => {
    if (!docFile || !liveFile) {
      alert("Please provide both a document image and a live photo.");
      return;
    }

    if (statusText) statusText.textContent = "Processing, please wait...";
    analyzeBtn.disabled = true;
    if (resultsSection) resultsSection.style.display = "none";

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
      if (statusText) statusText.textContent = "Analysis complete.";
    } catch (err) {
      if (statusText) statusText.textContent = "Error: " + err.message;
      alert("Analysis failed: " + err.message);
    } finally {
      analyzeBtn.disabled = false;
    }
  });
}

// ---- Render results in the UI (null-safe) ----
function renderResults(result) {
  if (resultsSection) resultsSection.style.display = "block";

  const riskLevelEl = getEl("riskLevel");
  if (riskLevelEl) {
    riskLevelEl.textContent = result.risk_level || "--";
    riskLevelEl.className = "risk-badge " + (result.risk_level || "");
  }

  voiceAlert(result.risk_level);
  if (result.risk_level === "HIGH") {
    playAlertSound();
  }

  const riskScore = result.risk_score ?? 0;
  const riskScoreEl = getEl("riskScore");
  if (riskScoreEl) riskScoreEl.textContent = riskScore;
  animateRiskGauge(riskScore);

  setText("documentType", result.document_type || "--");
  setText("faceMatch", result.face_match ? "Match" : "No Match");
  setText("similarity", result.similarity ?? "--");
  setText("livenessResult", result.liveness_passed ? "Passed" : "Failed");
  setText("tamperScore", result.tamper_score ?? "--");
  setText("noiseScore", result.noise_score ?? "--");
  setText("blockchainHash", result.blockchain_hash || "--");

  const fieldsEl = getEl("extractedFields");
  if (fieldsEl) {
    fieldsEl.textContent = JSON.stringify(result.fields || {}, null, 2);
  }

  const errorsList = getEl("errorsList");
  if (errorsList) {
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
  }

  const heatmapImage = getEl("heatmapImage");
  if (heatmapImage) {
    if (result.heatmap) {
      heatmapImage.src = "data:image/jpeg;base64," + result.heatmap;
      heatmapImage.style.display = "block";
    } else {
      heatmapImage.style.display = "none";
    }
  }

  const pdfLink = getEl("pdfLink");
  const qrLink = getEl("qrLink");
  if (pdfLink) pdfLink.href = result.pdf_report ? BACKEND_URL + result.pdf_report : "#";
  if (qrLink) qrLink.href = result.qr_code ? BACKEND_URL + result.qr_code : "#";

  if (resultsSection) resultsSection.scrollIntoView({ behavior: "smooth" });
}

function setText(id, value) {
  const el = getEl(id);
  if (el) el.textContent = value;
}