from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import sys
import os

sys.path.append(os.path.dirname(__file__))

from modules.ocr import extract_fields
from modules.validation import validate_document
from modules.tamper import detect_tampering
from modules.face import verify_face
from modules.risk import calculate_risk

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(doc: UploadFile = File(...), live: UploadFile = File(...)):
    doc_bytes = await doc.read()
    live_bytes = await live.read()
    
    doc_img = cv2.imdecode(np.frombuffer(doc_bytes, np.uint8), cv2.IMREAD_COLOR)
    live_img = cv2.imdecode(np.frombuffer(live_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Save temp files
    doc_path = "temp_doc.jpg"
    live_path = "temp_live.jpg"
    cv2.imwrite(doc_path, doc_img)
    cv2.imwrite(live_path, live_img)
    
    # Process
    fields = extract_fields(doc_path)
    errors = validate_document(fields)
    tamper_score, heatmap_img = detect_tampering(doc_path)
    face_match, similarity = verify_face(doc_path, live_path)
    risk_score, risk_level = calculate_risk(errors, tamper_score, face_match)
    
    # Heatmap to base64
    _, buffer = cv2.imencode('.jpg', heatmap_img)
    heatmap_b64 = base64.b64encode(buffer).decode()
    
    # Cleanup
    if os.path.exists(doc_path): os.remove(doc_path)
    if os.path.exists(live_path): os.remove(live_path)
    
    return {
        "fields": fields,
        "errors": errors,
        "tamper_score": tamper_score,
        "heatmap": heatmap_b64,
        "face_match": face_match,
        "similarity": similarity,
        "risk_score": risk_score,
        "risk_level": risk_level
    }

@app.get("/health")
async def health():
    return {"status": "ok"}