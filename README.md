# AI-Based Fake Identity & Document Screening System

**SIH PS 26188** — Ministry of Home Affairs, Sashastra Seema Bal (SSB)

An end-to-end prototype that screens identity documents (passport, visa,
Aadhaar, driving licence) for forgery, validates extracted fields,
confirms the presenter's identity via face match + liveness check,
scores overall risk, and logs every result on a local tamper-proof
blockchain ledger.

## Features

- **OCR / MRZ extraction** — PassportEye for MRZ documents, OCR fallback for others
- **Field validation** — expiry check, passport number format, blacklist lookup
- **Document type detection** — passport / visa / aadhaar / driving licence
- **Tamper detection** — Error Level Analysis (ELA) with visual heatmap
- **Noise analysis** — sensor noise consistency check for splice detection
- **Face verification** — DeepFace comparison between document photo and live selfie
- **Liveness check** — basic eye/face detection
- **Risk scoring** — weighted combination of all checks (LOW / MEDIUM / HIGH)
- **Blockchain audit trail** — SHA256-linked blocks, tamper-evident
- **PDF report + QR code** — generated per screening for officer review
- **Dashboard** — analytics on total screened, risk distribution, recent records
- **Bilingual UI** — English and Hindi

## Tech Stack

- **Backend:** FastAPI, SQLite, OpenCV, DeepFace, PassportEye, ReportLab, qrcode
- **Frontend:** HTML, CSS, JavaScript (vanilla, no framework)
- **Storage:** SQLite (`records.db`) + local blockchain ledger (in-memory, SHA256)

## Project Structure

```
.
├── backend/
│   ├── main.py                  # FastAPI app - orchestrates the full pipeline
│   ├── blockchain.py            # SHA256 blockchain ledger
│   ├── alert.py                 # High-risk alert notifications (mock)
│   ├── database.py              # SQLite storage
│   ├── requirements.txt
│   └── modules/
│       ├── ocr.py               # MRZ / OCR field extraction
│       ├── validation.py        # Field + blacklist validation
│       ├── document_type.py     # Document type classifier
│       ├── tamper.py            # ELA tamper detection
│       ├── noise_analysis.py    # Sensor noise consistency check
│       ├── face.py              # DeepFace face verification
│       ├── liveness.py          # Basic liveness check
│       ├── video_capture.py     # Webcam frame capture (prototype)
│       ├── pdf_report.py        # PDF report generation
│       ├── qr_code.py           # QR code generation
│       ├── qr_verify.py         # QR code verification
│       ├── csv_export.py        # CSV export of records
│       ├── risk.py              # Weighted risk scoring
│       ├── analytics.py         # Dashboard statistics
│       └── language.py          # English / Hindi translations
├── frontend/
│   ├── index.html               # Main screening page
│   ├── dashboard.html           # Analytics dashboard
│   ├── qr.html                  # QR verification page
│   ├── report.html              # PDF report preview page
│   ├── style.css
│   └── script.js
├── tests/
│   ├── test_pipeline.py         # End-to-end pipeline smoke test
│   └── test_accuracy.py         # TPR / FPR accuracy metrics
├── data/
│   ├── blacklist.csv            # Blacklisted passport numbers
│   └── sample_images/           # Put test document images here
├── README.md
├── .gitignore
└── LICENSE
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

You'll also need **Tesseract OCR** installed on your system for the
OCR fallback and `document_type.py` keyword detection to work:

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

### 2. Run the backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive API docs: `http://localhost:8000/docs`

### 3. Run the frontend

The frontend is plain HTML/CSS/JS, so you can just open it directly,
or serve it with a simple static server:

```bash
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500/index.html`.

> Make sure `BACKEND_URL` in `frontend/script.js` matches where your
> backend is running (default: `http://localhost:8000`).

### 4. Run tests

```bash
cd tests
python test_pipeline.py
python test_accuracy.py
```

Add sample document images to `data/sample_images/` before running
`test_pipeline.py`. For `test_accuracy.py`, fill in the
`LABELED_SAMPLES` list with known genuine/fake examples.

## API Endpoints

| Method | Endpoint            | Description                                  |
|--------|----------------------|-----------------------------------------------|
| GET    | `/health`            | Health check                                  |
| POST   | `/upload`            | Upload doc + live image, run full pipeline    |
| GET    | `/records`           | Get all past screening records                |
| GET    | `/stats`             | Get dashboard statistics                      |
| GET    | `/blockchain/verify` | Verify the blockchain ledger integrity        |
| GET    | `/export/csv`        | Export all records to CSV                     |

## Notes for Production Use

This is a **hackathon-grade prototype**. Before any real deployment:

- Restrict CORS `allow_origins` instead of `"*"`
- Replace the mock email/SMS alerts in `alert.py` with a real provider
- Persist the blockchainss ledger to disk (currently in-memory per run)
- Strengthen liveness detection with multi-frame blink/motion analysis
- Add authentication/authorization to all API endpoints
- Review data retention and privacy compliance for biometric data

## License

MIT License — see [LICENSE](LICENSE).