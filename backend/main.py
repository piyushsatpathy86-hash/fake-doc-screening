"""
main.py
FastAPI application for the AI-Based Fake Identity & Document
Screening System (SIH PS 26188).

Pipeline: OCR -> validation -> document type -> tamper detection ->
noise analysis -> face match -> liveness -> risk scoring ->
blockchain logging -> SQLite storage -> PDF report + QR code.
"""

import os
import base64
import shutil

import cv2
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Local modules
from modules import ocr
from modules import validation
from modules import document_type
from modules import tamper
from modules import noise_analysis
from modules import face
from modules import liveness
from modules import pdf_report
from modules import qr_code
from modules import csv_export
from modules import risk
from modules import analytics
from modules import language

import blockchain
import database
import alert

app = FastAPI(title="AI Document Screening System - SIH PS 26188")

# ---- CORS: allow all origins (tighten this for production) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
REPORTS_DIR = "reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Serve generated PDFs/QR codes/heatmaps so the frontend can load them directly
app.mount("/files", StaticFiles(directory=REPORTS_DIR), name="files")


def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return destination


def image_to_base64(image) -> str:
    """Encode an OpenCV (numpy) image as a base64 JPEG string."""
    if image is None:
        return None
    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    return analytics.get_dashboard_stats()


@app.get("/records")
def records():
    return database.get_records()


@app.get("/blockchain/verify")
def verify_blockchain():
    return {"valid": blockchain.blockchain.verify_chain()}


@app.get("/export/csv")
def export_csv():
    output_path = os.path.join(REPORTS_DIR, "records_export.csv")
    csv_export.export_to_csv(database.get_records(), output_path)
    return {"csv_path": f"/files/{os.path.basename(output_path)}"}


@app.post("/upload")
async def upload_documents(
    doc_image: UploadFile = File(..., description="Photo of the ID/passport document"),
    live_image: UploadFile = File(..., description="Live selfie photo of the person"),
):
    """
    Main screening endpoint. Runs the full detection pipeline and
    returns a complete JSON report.
    """

    # ---- 1. Save uploaded files ----
    doc_path = os.path.join(UPLOAD_DIR, f"doc_{doc_image.filename}")
    live_path = os.path.join(UPLOAD_DIR, f"live_{live_image.filename}")
    save_upload_file(doc_image, doc_path)
    save_upload_file(live_image, live_path)

    # ---- 2. OCR ----
    fields = ocr.extract_fields(doc_path)

    # ---- 3. Validation ----
    validation_errors = validation.validate_document(fields)

    # ---- 4. Document type detection ----
    doc_type = document_type.detect_document_type(doc_path)

    # ---- 5. Tamper detection (ELA) ----
    tamper_score, heatmap_image = tamper.detect_tampering(doc_path, output_dir=UPLOAD_DIR)
    heatmap_base64 = image_to_base64(heatmap_image)

    # ---- 6. Noise analysis ----
    noise_score = noise_analysis.analyze_noise(doc_path)

    # ---- 7. Face match ----
    face_match, similarity = face.verify_face(doc_path, live_path)

    # ---- 8. Liveness check ----
    liveness_passed = liveness.check_liveness(live_path)

    # ---- 9. Risk scoring ----
    risk_result = risk.calculate_risk(
        validation_errors=validation_errors,
        tamper_score=tamper_score,
        face_match=face_match,
        liveness_passed=liveness_passed,
    )

    # ---- 10. Blockchain logging ----
    block_data = {
        "passport_number": fields.get("passport_number", "UNKNOWN"),
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
    }
    new_block = blockchain.blockchain.add_block(block_data)

    # ---- 11. Build the full result dict ----
    result = {
        "fields": fields,
        "errors": validation_errors,
        "document_type": doc_type,
        "tamper_score": tamper_score,
        "noise_score": noise_score,
        "heatmap": heatmap_base64,
        "face_match": face_match,
        "similarity": similarity,
        "liveness_passed": liveness_passed,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "risk_breakdown": risk_result["breakdown"],
        "blockchain_hash": new_block.hash,
    }

    # ---- 12. Generate PDF report + QR code ----
    passport_number = fields.get("passport_number", "UNKNOWN") or "UNKNOWN"
    safe_id = str(passport_number).replace(" ", "_")

    pdf_path = os.path.join(REPORTS_DIR, f"report_{safe_id}.pdf")
    pdf_report.generate_pdf_report(result, pdf_path)

    qr_path = os.path.join(REPORTS_DIR, f"qr_{safe_id}.png")
    qr_code.generate_qr(
        {
            "passport_number": passport_number,
            "risk_level": risk_result["risk_level"],
            "blockchain_hash": new_block.hash,
        },
        qr_path,
    )

    result["pdf_report"] = f"/files/{os.path.basename(pdf_path)}"
    result["qr_code"] = f"/files/{os.path.basename(qr_path)}"

    # ---- 13. Save to SQLite ----
    record = {
        "passport_number": passport_number,
        "name": fields.get("name", "UNKNOWN"),
        "document_type": doc_type,
        "fields": fields,
        "errors": validation_errors,
        "tamper_score": tamper_score,
        "noise_score": noise_score,
        "face_match": {"match": face_match, "similarity": similarity},
        "similarity": similarity,
        "liveness_passed": liveness_passed,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "blockchain_hash": new_block.hash,
    }
    database.save_record(record)

    # ---- 14. Trigger alert if high risk ----
    alert.send_alert(risk_score=risk_result["risk_score"], passport_number=passport_number)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)