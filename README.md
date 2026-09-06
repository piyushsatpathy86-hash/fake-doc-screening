# KAVACHAI — AI-Based Fake Identity & Document Screening System

**SIH PS 26188** — Ministry of Home Affairs, Sashastra Seema Bal (SSB)

An end-to-end prototype that screens identity documents (passport, visa, Aadhaar, driving licence) for forgery, validates extracted fields, confirms the presenter's identity via face match + liveness check, scores overall risk, and logs every result on a tamper-evident blockchain ledger.

## Team

| Member | Role |
|--------|------|
| **Piyush Satpathy** | **Team Lead — OCR, Tamper Detection, QR Code, Blockchain, Risk Scoring, Hash Verification, SAHARA, Splash, Theme, Voice/Sound, Gauge, PWA, Redesign, Integration, Deployment, Frontend/Backend across all modules** |
| Rudra Pratap Jayasingh | Assisted in OCR, Validation, Document Type Detection |
| Sairashmi Thatoi | Assisted in Face Verification, Liveness, PDF Report, Frontend Styling |
| Saismruti Patara | Assisted in Tamper Detection (ELA), Noise Analysis |
| Sampatirao Devyani | Assisted in Frontend, QR Code, CSV Export, Testing, README |
| Rutumbhara | Data Collection, Presentation, Demo Script |

> **Note:** Piyush Satpathy, as Team Lead, was the primary developer across the entire stack — from backend AI modules (OCR, tamper, QR, risk, blockchain) to frontend UI/UX (SAHARA, splash, dark mode, gauge) and deployment. Team members contributed in supporting roles.

## Features

### Core AI Modules
- **OCR / MRZ Extraction** — PassportEye for MRZ parsing, Tesseract OCR fallback with regex
- **Field Validation** — type-aware checks (passport/aadhaar/DL/visa), expiry, format, blacklist
- **Document Type Detection** — filename-aware + OCR keyword + aspect ratio
- **Tamper Detection** — Error Level Analysis (ELA) with heatmap visualization
- **Hash-Based Verification** — verified document registry (SHA256) to catch modified files
- **Noise Analysis** — sensor noise consistency for splice detection
- **Face Verification** — DeepFace (VGG-Face) with similarity score
- **Liveness Check** — Haar cascade eye/face detection
- **Risk Scoring** — weighted multi-signal fusion (LOW/MEDIUM/HIGH)

### Security & Audit
- **Blockchain Audit Trail** — SHA256-linked blocks, tamper-evident
- **Document Hash Registry** — pre-computed verified document hashes
- **PDF Report + QR Code** — per screening for officer review
- **CSV Export** — complete records export

### Frontend & UX
- **SAHARA Assistant** — floating movable AI help assistant (app-specific Q&A)
- **Splash Screen** — animated shield logo reveal with skip button
- **Dark/Light Mode** — theme toggle with localStorage persistence
- **Voice Alert + Sound** — HIGH risk par voice warning aur beep
- **Animated Risk Gauge** — SVG circular gauge with color coding
- **Dashboard** — total screened, risk distribution, recent records
- **QR Verify Page** — passport/document number se lookup
- **Offline-First PWA** — Service Worker + Manifest
- **Mobile Responsive** — phone/tablet optimized
- **Bilingual UI** — English/Hindi support

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python FastAPI, Uvicorn |
| **Database** | SQLite (`records.db`) |
| **OCR** | PassportEye + Tesseract |
| **Image Processing** | OpenCV, PIL, scikit-image |
| **Face Recognition** | DeepFace (VGG-Face) |
| **Blockchain** | SHA256 in-memory chain |
| **PDF** | ReportLab |
| **QR** | qrcode library |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **PWA** | Service Worker + Web App Manifest |
| **Voice** | Web Speech API |
| **Sound** | Web Audio API |

## Project Structure
.
├── backend/
│ ├── main.py # FastAPI app - orchestrates the full pipeline
│ ├── blockchain.py # SHA256 blockchain ledger
│ ├── alert.py # High-risk alert notifications (mock)
│ ├── database.py # SQLite storage
│ ├── requirements.txt
│ └── modules/
│ ├── ocr.py # MRZ / OCR field extraction
│ ├── validation.py # Field + blacklist validation
│ ├── document_type.py # Document type classifier
│ ├── tamper.py # Tamper detection
│ ├── noise_analysis.py # Sensor noise consistency check
│ ├── face.py # DeepFace face verification
│ ├── liveness.py # Basic liveness check
│ ├── video_capture.py # Webcam frame capture (prototype)
│ ├── pdf_report.py # PDF report generation
│ ├── qr_code.py # QR code generation
│ ├── qr_verify.py # QR code verification
│ ├── csv_export.py # CSV export of records
│ ├── risk.py # Weighted risk scoring
│ ├── analytics.py # Dashboard statistics
│ └── language.py # English / Hindi translations
├── frontend/
│ ├── index.html # Main screening page
│ ├── dashboard.html # Analytics dashboard
│ ├── qr.html # QR verification page
│ ├── report.html # PDF report preview page
│ ├── splash.css # Splash screen animation styles
│ ├── splash.js # Splash animation controller
│ ├── sahara.js # SAHARA Assistant
│ ├── manifest.json # PWA manifest
│ ├── sw.js # Service Worker (offline cache)
│ ├── style.css
│ └── script.js
├── tests/
│ ├── test_pipeline.py # End-to-end pipeline smoke test
│ └── test_accuracy.py # TPR / FPR accuracy metrics
├── data/
│ ├── blacklist.csv # Blacklisted passport numbers
│ └── sample_images/ # Test document images
├── verified_hashes.json # Verified document hash registry
├── README.md
├── .gitignore
└── LICENSE

## Setup

### 1. Backend

```bash
cd fake-doc-screening
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r backend/requirements.txt'''

You'll also need Tesseract OCR installed on your system:

Windows: Download from UB Mannheim Tesseract

Ubuntu/Debian: sudo apt install tesseract-ocr

macOS: brew install tesseract

2. Generate Verified Hashes
bash'''
python -c "
import os, hashlib, json

folder = 'data/sample_images'
verified = {}

for f in os.listdir(folder):
    low = f.lower()
    if low.endswith(('.jpg', '.jpeg', '.png')):
        if any(x in low for x in ['tampered', 'face', 'piyush', 'driving licence']):
            continue
        path = os.path.join(folder, f)
        with open(path, 'rb') as fp:
            h = hashlib.sha256(fp.read()).hexdigest()
        verified[f] = h

with open('verified_hashes.json', 'w') as fp:
    json.dump(verified, fp, indent=2)

print(f'Saved {len(verified)} verified document hashes')
"'
3. Run the Backend
bash'''
cd fake-doc-screening
venv\Scripts\activate
python backend/main.py'''
API available at http://localhost:8000. Interactive docs: http://localhost:8000/docs

4. Run the Frontend
bash'''
cd fake-doc-screening/frontend
python -m http.server 5500'''
Visit: http://localhost:5500/index.html

Make sure BACKEND_URL in frontend/script.js is http://localhost:8000.

5. Run Tests
bash'''
cd fake-doc-screening/tests
python test_pipeline.py
python test_accuracy.py'''
API Endpoints
Method	Endpoint	Description
GET	/health	Health check
POST	/upload	Upload doc + live image, run full pipeline
GET	/records	Get all past screening records
GET	/stats	Get dashboard statistics
GET	/blockchain/verify	Verify the blockchain ledger integrity
GET	/export/csv	Export all records to CSV
Limitations (Prototype)
Tamper detection is heuristic (hash-based + color-based); production needs multi-signal forensic analysis

Synthetic data used for testing

Mock email/SMS/WhatsApp alerts

In-memory blockchain (resets on restart)

No authentication/authorization

CORS allows all origins

Production Roadmap
Multi-signal tamper detection (ELA, copy-move, noise inconsistency, metadata, ManTraNet)

Government API integration (UIDAI, Passport Seva, NCRB)

Persistent blockchain storage

Real alert system (SendGrid, Twilio, WhatsApp Business)

JWT authentication + role-based access

Docker + Kubernetes deployment

Edge deployment (Jetson Nano/Intel NUC) for border checkpoints

License
MIT License — see LICENSE