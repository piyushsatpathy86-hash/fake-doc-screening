// ==========================================================
// SAHARA Assistant - KAVACH-AI App-Specific Help
// Movable floating assistant (drag from button only)
// ==========================================================

const SAHARA_KEYWORDS = [
  "risk", "score", "upload", "document", "passport", "visa", "aadhaar",
  "license", "tamper", "heatmap", "face", "match", "liveness", "blockchain",
  "hash", "camera", "capture", "photo", "report", "pdf", "qr", "verify",
  "scan", "screen", "use", "how", "help", "kavach", "kavachai", "kavach-ai",
  "high risk", "low risk", "validation", "error", "alert", "dark", "theme",
  "language", "offline", "splash", "dashboard", "records", "stats",
  "built", "build", "creator", "team", "developer", "who made", "who built",
  "made by", "ki banaya", "sahara", "banaya", "kisne", "kaun", "contribution",
  "role", "part", "kya kiya", "kaam", "purpose", "about", "kya hai",
  "app", "indian gov", "border", "ssb", "ministry", "fake identity",
  "file", "files", "structure", "owner", "piyush", "rudra", "rashmi",
  "smruti", "devyani", "riya", "rutumbhara", "sampatirao", "sairashmi",
  "saismruti", "jayasingh", "thatoi", "patara", "satpathy",
  "tech", "stack", "technology", "tools", "libraries", "framework",
  "backend", "frontend", "database", "ml", "ai model", "deepface",
  "opencv", "fastapi", "sqlite", "passporteye", "tesseract"
];

const SAHARA_RESPONSES = {
  "purpose": "KAVACH-AI ek AI-based fake identity & document screening system hai, jo Indian border checkpoints ke liye Ministry of Home Affairs, Sashastra Seema Bal (SSB) ke liye banaya gaya hai. Ye forged passports, tampered documents, aur identity fraud detect karta hai.",
  "about": "KAVACH-AI ek AI-powered document screening platform hai. Ye passport, visa, Aadhaar, driving license ko scan karke fake/tampered detection karta hai. Isme OCR, tamper detection (ELA), face verification, liveness check, blockchain audit trail, PDF report, aur QR code verification shamil hai. System offline-first hai.",
  "kya hai": "KAVACH-AI ek AI-based document screening system hai jo border checkpoints par fake identity aur forged documents ko pakadta hai. Features: OCR, tamper detection, face match, liveness, blockchain, QR verification.",
  "app": "KAVACH-AI ek government-tech app hai jo Indian border security ke liye banaya gaya hai. Documents ki authenticity check karta hai aur risk score deta hai.",
  "indian gov": "KAVACH-AI Ministry of Home Affairs, Sashastra Seema Bal (SSB) ke liye banaya gaya hai. Indian border checkpoints par fake documents aur identity fraud rokne mein madad karta hai.",
  "border": "KAVACH-AI border checkpoints ke liye design kiya gaya hai. Offline-first hai, taaki remote areas mein bhi bina internet ke kaam kare.",
  "ssb": "KAVACH-AI Sashastra Seema Bal (SSB) ke liye banaya gaya hai — Indian border security force jo Nepal aur Bhutan borders guard karti hai.",
  "ministry": "KAVACH-AI Ministry of Home Affairs ke under aata hai. SIH PS 26188 problem statement ka solution hai.",
  "fake identity": "KAVACH-AI fake identity documents ko detect karta hai using AI — photo replacement, text manipulation, stamp forgery, expiry/blacklist checks.",
  "upload": "Screen section mein jao, 'Choose file' par click karo, aur document ki photo select karo.",
  "document": "Passport, Visa, Aadhaar, aur Driving License support hain. Image upload karke Analyze dabao.",
  "risk": "Risk score 0-100 hai. 0-30 LOW (safe), 30-60 MEDIUM (warning), 60-100 HIGH (danger).",
  "score": "Risk score 0-100 hai. LOW = safe, MEDIUM = check karo, HIGH = manual verification zaroori.",
  "tamper": "Error Level Analysis (ELA) se edited areas detect hote hain. Heatmap mein red highlight dikhta hai.",
  "heatmap": "Heatmap document ke upar overlay hota hai — suspicious areas red ya bright color mein dikhte hain.",
  "face": "Document photo aur live photo ka DeepFace se comparison hota hai. Match hone par LOW risk.",
  "match": "Face match true hai toh same person hai. False hai toh photo mismatch — HIGH risk mein add hota hai.",
  "liveness": "Liveness check se pata chalta hai ki live photo asli hai ya photo-of-photo. Blink detection use hota hai.",
  "blockchain": "Har screening ka record blockchain par save hota hai. Koi bhi record edit ya delete nahi kar sakta.",
  "hash": "Blockchain hash har screening ka unique fingerprint hai. Isse record verify kiya ja sakta hai.",
  "camera": "Live photo card mein 'Open camera' button dabao, face dikhao, phir 'Capture' dabao.",
  "capture": "Camera capture ke liye 'Open camera' dabao, face dikhao, 'Capture' se photo lo.",
  "report": "Analyze ke baad PDF report download kar sakte ho. Reports page par passport number se bhi nikal sakte ho.",
  "pdf": "PDF report screening result ka complete summary hai. Reports page par search karke download karo.",
  "qr": "QR code se document verify kar sakte ho. QR Verify page par passport number search karo.",
  "verify": "QR Verify page par jaakar passport number se QR code dekh sakte ho.",
  "dashboard": "Dashboard page par total screened, high risk, low risk, tampered documents ki stats dikhti hain.",
  "records": "Dashboard ke Recent Records table mein last 20 screenings ki details milti hain.",
  "splash": "Splash screen app load hote hi dikhti hai — animated logo reveal. Skip button se bypass kar sakte ho.",
  "dark": "Navbar mein 🌙 Dark button se dark mode on/off karo. Preference save ho jata hai.",
  "theme": "Light aur Dark theme available hai. Navbar mein toggle button hai.",
  "language": "Abhi English/Hindi support hai. Language toggle aayega.",
  "offline": "App offline-first hai. PWA support se bina internet ke bhi chalega.",
  "alert": "HIGH risk par voice alert, sound effect, aur mock email/SMS/WhatsApp alerts trigger hote hain.",
  "validation": "Validation errors document ki internal consistency check mein fail hone par dikhte hain.",
  "scan": "Document upload karo, live photo do, Analyze dabao. System OCR se text nikalta hai.",
  "help": "Main SAHARA hoon — KAVACH-AI ki assistant. Puchho: upload, risk score, camera, blockchain, PDF, QR, team, tech stack, purpose.",
  "tech": "KAVACH-AI TECH STACK:\n\nFRONTEND:\n• HTML5, CSS3, Vanilla JavaScript\n• Pastel color-block design system\n• Splash screen (CSS/SVG animation)\n• SAHARA floating assistant\n\nBACKEND:\n• Python FastAPI\n• SQLite (records storage)\n• Blockchain (SHA256 hash chain)\n\nAI/ML MODULES:\n• OCR: PassportEye (MRZ) + Tesseract (fallback)\n• Tamper Detection: OpenCV, PIL (Error Level Analysis)\n• Noise Analysis: scikit-image\n• Face Verification: DeepFace (VGG-Face)\n• Liveness: OpenCV Haar cascades\n\nREPORTS:\n• ReportLab (PDF generation)\n• qrcode (QR generation)\n• CSV export\n\nTESTING:\n• pytest",
  "stack": "KAVACH-AI TECH STACK:\n\nFrontend: HTML5, CSS3, Vanilla JavaScript\nBackend: Python FastAPI\nDatabase: SQLite\nBlockchain: SHA256\nOCR: PassportEye + Tesseract\nFace: DeepFace (VGG-Face)\nTamper: OpenCV, PIL (ELA)\nNoise: scikit-image\nPDF: ReportLab\nQR: qrcode\nTesting: pytest",
  "technology": "KAVACH-AI TECH STACK:\n\n• Frontend: HTML5, CSS3, Vanilla JavaScript\n• Backend: Python FastAPI\n• Database: SQLite\n• Blockchain: SHA256 hash chain\n• OCR: PassportEye + Tesseract\n• Face: DeepFace (VGG-Face)\n• Tamper: OpenCV, PIL (ELA)\n• Noise: scikit-image\n• PDF: ReportLab\n• QR: qrcode\n• Testing: pytest",
  "built": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, Risk Scoring, SAHARA Assistant, Deployment\n• Rudra Pratap Jayasingh — OCR, Validation, Document Type Detection\n• Sairashmi Thatoi — Face Verification, Liveness, Video Capture, PDF Report, Frontend Styling\n• Saismruti Patara — Tamper Detection (ELA), Noise Analysis\n• Sampatirao Devyani — Frontend, QR Code, CSV Export, Testing, README\n• Rutumbhara — Data Collection, Presentation, Demo Script",
  "build": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, Risk Scoring, SAHARA Assistant, Deployment\n• Rudra Pratap Jayasingh — OCR, Validation, Document Type Detection\n• Sairashmi Thatoi — Face Verification, Liveness, PDF Report, Frontend Styling\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, Testing, README\n• Rutumbhara — Data, Presentation",
  "team": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, Risk, SAHARA\n• Rudra Pratap Jayasingh — OCR, Validation, Document Type\n• Sairashmi Thatoi — Face Verification, Liveness, PDF\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, CSV, Testing\n• Rutumbhara — Data, Presentation",
  "developer": "KAVACH-AI developers:\n\n• Piyush Satpathy — Team Lead, Integration, Blockchain, SAHARA\n• Rudra — OCR, Validation\n• Rashmi — Face, Liveness, PDF\n• Smruti — Tamper, Noise\n• Devyani — Frontend, QR, Testing\n• Riya — Data, Presentation",
  "who made": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, Risk, SAHARA\n• Rudra Pratap Jayasingh — OCR, Validation\n• Sairashmi Thatoi — Face Verification, Liveness, PDF\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, Testing\n• Rutumbhara — Data, Presentation",
  "who built": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, Risk, SAHARA\n• Rudra Pratap Jayasingh — OCR, Validation\n• Sairashmi Thatoi — Face Verification, Liveness, PDF\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, Testing\n• Rutumbhara — Data, Presentation",
  "made by": "KAVACH-AI ki team:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, SAHARA\n• Rudra Pratap Jayasingh — OCR, Validation\n• Sairashmi Thatoi — Face Verification, Liveness, PDF\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, Testing\n• Rutumbhara — Data, Presentation",
  "ki banaya": "KAVACH-AI TEAM:\n\n• Piyush Satpathy (Team Lead) — Integration, Blockchain, SAHARA\n• Rudra Pratap Jayasingh — OCR, Validation\n• Sairashmi Thatoi — Face Verification, Liveness, PDF\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, Testing\n• Rutumbhara — Data, Presentation",
  "contribution": "KAVACH-AI CONTRIBUTIONS:\n\n• Piyush Satpathy — Integration, Blockchain, Risk, SAHARA, Offline Mode, Splash, Theme, Voice/Sound, Gauge\n• Rudra — OCR, Validation, Document Type\n• Sairashmi Thatoi — Face Verification, Liveness, PDF Report\n• Saismruti Patara — Tamper Detection, Noise Analysis\n• Sampatirao Devyani — Frontend, QR, CSV, Testing, Docs\n• Rutumbhara — Data Collection, Presentation",
  "role": "KAVACH-AI ROLES:\n\n• Piyush Satpathy — Team Lead (Integration, Blockchain, SAHARA)\n• Rudra — OCR & Validation\n• Rashmi — Face & Liveness\n• Smruti — Tamper Detection\n• Devyani — Frontend & Testing\n• Riya — Data & Presentation",
  "part": "KAVACH-AI ROLES:\n\n• Piyush Satpathy — Team Lead\n• Rudra — OCR, Validation\n• Rashmi — Face, Liveness, PDF\n• Smruti — Tamper, Noise\n• Devyani — Frontend, QR, Testing\n• Riya — Data, Presentation",
  "kya kiya": "KAVACH-AI TEAM CONTRIBUTIONS:\n\n• Piyush Satpathy — Integration, Blockchain, Risk, SAHARA\n• Rudra — OCR, Validation\n• Rashmi — Face Verification, Liveness\n• Smruti — Tamper Detection\n• Devyani — Frontend, QR, Testing\n• Riya — Data Collection, Presentation",
  "kaam": "KAVACH-AI TEAM CONTRIBUTIONS:\n\n• Piyush Satpathy — Integration, Blockchain, Risk, SAHARA\n• Rudra — OCR, Validation\n• Rashmi — Face Verification, Liveness\n• Smruti — Tamper Detection\n• Devyani — Frontend, QR, Testing\n• Riya — Data Collection, Presentation",
  "file": "KAVACH-AI FILE STRUCTURE (OWNERS):\n\nPIYUSH (Team Lead):\nbackend/main.py, blockchain.py, alert.py, database.py, modules/risk.py, modules/analytics.py, modules/language.py, frontend/splash.css, splash.js, sahara.js, manifest.json, sw.js + frontend enhancements (theme, gauge, voice, sound)\n\nRUDRA:\nmodules/ocr.py, modules/validation.py, modules/document_type.py, data/blacklist.csv\n\nSMRUTI:\nmodules/tamper.py, modules/noise_analysis.py\n\nRASHMI:\nmodules/face.py, modules/liveness.py, modules/video_capture.py, modules/pdf_report.py, frontend/style.css (base)\n\nDEVYANI:\nfrontend/index.html (base), script.js (base), qr.html, report.html, dashboard.html, modules/qr_code.py, modules/qr_verify.py, modules/csv_export.py, tests/, README.md\n\nRIYA (Rutumbhara):\ndata/sample_images/faces/, presentation slides, demo script",
  "files": "KAVACH-AI FILE OWNERS:\n\nPIYUSH — main.py, blockchain.py, alert.py, database.py, risk.py, analytics.py, language.py, splash.css, splash.js, sahara.js, manifest.json, sw.js\n\nRUDRA — ocr.py, validation.py, document_type.py, blacklist.csv\n\nSMRUTI — tamper.py, noise_analysis.py\n\nRASHMI — face.py, liveness.py, video_capture.py, pdf_report.py, style.css\n\nDEVYANI — index.html, script.js, qr.html, report.html, qr_code.py, qr_verify.py, csv_export.py, tests, README\n\nRIYA — faces data, presentation",
  "structure": "KAVACH-AI FILE OWNERS:\n\nPIYUSH — Integration, Blockchain, Risk, SAHARA, Splash, Theme, Voice, PWA\nRUDRA — OCR, Validation, Document Type\nSMRUTI — Tamper Detection, Noise Analysis\nRASHMI — Face, Liveness, PDF, Styling\nDEVYANI — Frontend, QR, CSV, Testing, Docs\nRIYA — Data, Presentation",
  "owner": "KAVACH-AI FILE OWNERS:\n\n• Piyush Satpathy — Integration, Blockchain, SAHARA, Risk, Analytics\n• Rudra — OCR, Validation, Document Type\n• Rashmi — Face, Liveness, PDF, Styling\n• Smruti — Tamper, Noise Analysis\n• Devyani — Frontend, QR, Testing, Docs\n• Riya — Data, Presentation",
  "sahara ko kisne banaya": "SAHARA ko Piyush Satpathy (Team Lead) ne banaya hai. Ye KAVACH-AI ka AI help assistant hai jo app navigation, features, team info aur tech stack samjhata hai.",
  "who built sahara": "SAHARA was built by Piyush Satpathy (Team Lead). It is KAVACH-AI's AI help assistant for app navigation and feature guidance.",
  "sahara kaun banaya": "SAHARA ko Piyush Satpathy (Team Lead) ne banaya hai.",
  "sahara developer": "SAHARA ke developer: Piyush Satpathy (Team Lead).",
  "sahara": "SAHARA KAVACH-AI ka AI help assistant hai. Isse Piyush Satpathy (Team Lead) ne banaya hai. Ye app navigation, document screening features, risk score, tech stack, aur team info ke baare mein jawab deta hai."
};

function getSaharaResponse(query) {
  const q = query.toLowerCase().trim();

  if (q.includes("sahara ko kisne banaya") || q.includes("who built sahara") || q.includes("sahara kaun banaya")) {
    return SAHARA_RESPONSES["sahara ko kisne banaya"];
  }

  const isRelevant = SAHARA_KEYWORDS.some(kw => q.includes(kw));
  if (!isRelevant) {
    return "Main sirf KAVACH-AI app ke baare mein jawab de sakti hoon. Document screening, risk score, camera, blockchain, PDF report, tech stack, team info ke baare mein puchho.";
  }

  for (const [key, response] of Object.entries(SAHARA_RESPONSES)) {
    if (q.includes(key)) return response;
  }

  return "KAVACH-AI mein: document upload karo, live photo do, Analyze dabao. Risk score, face match, tamper heatmap, PDF report, aur QR code milta hai.";
}

// ==========================================================
// Drag functionality (only from floating button)
// ==========================================================
(function() {
  const widget = document.getElementById('saharaWidget');
  if (!widget) return;

  const floatBtn = widget.querySelector('.sahara-float');
  if (!floatBtn) return;

  let isDragging = false;
  let startX = 0, startY = 0;
  let offsetX = 0, offsetY = 0;

  floatBtn.addEventListener('mousedown', function(e) {
    isDragging = true;
    startX = e.clientX - offsetX;
    startY = e.clientY - offsetY;
    e.preventDefault();
  });

  document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    offsetX = e.clientX - startX;
    offsetY = e.clientY - startY;
    widget.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
  });

  document.addEventListener('mouseup', function() {
    isDragging = false;
  });
})();

// ==========================================================
// Chat functions
// ==========================================================
function toggleSaharaChat() {
  const chat = document.getElementById("saharaChatWindow");
  if (!chat) return;
  chat.style.display = chat.style.display === "none" || !chat.style.display ? "flex" : "none";
}

function sendSaharaMessage() {
  const input = document.getElementById("saharaInput");
  if (!input) return;
  const msg = input.value.trim();
  if (!msg) return;
  const messagesDiv = document.getElementById("saharaMessages");
  messagesDiv.innerHTML += `<div class="sahara-msg user">${msg}</div>`;
  input.value = "";
  const reply = getSaharaResponse(msg);
  setTimeout(() => {
    messagesDiv.innerHTML += `<div class="sahara-msg bot">${reply}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }, 400);
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("saharaInput");
  if (input) {
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendSaharaMessage();
    });
  }
});