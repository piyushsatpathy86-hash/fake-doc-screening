import sqlite3
import json
from datetime import datetime

DB_NAME = "records.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passport_number TEXT,
            name TEXT,
            document_type TEXT,
            fields TEXT,
            errors TEXT,
            tamper_score REAL,
            noise_score REAL,
            face_match TEXT,
            similarity REAL,
            liveness_passed INTEGER,
            risk_score REAL,
            risk_level TEXT,
            blockchain_hash TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def save_record(record: dict):
    conn = get_connection()
    cursor = conn.cursor()

    # Document number by type
    doc_type = record.get("document_type", "unknown")
    fields_data = record.get("fields", {})

    if doc_type == "passport":
        doc_number = fields_data.get("passport_number") or "UNKNOWN"
    elif doc_type == "aadhaar":
        doc_number = fields_data.get("aadhaar_number") or fields_data.get("passport_number") or "UNKNOWN"
    elif doc_type == "driving_license":
        doc_number = fields_data.get("dl_number") or fields_data.get("passport_number") or "UNKNOWN"
    elif doc_type == "visa":
        doc_number = fields_data.get("visa_number") or fields_data.get("passport_number") or "UNKNOWN"
    else:
        doc_number = fields_data.get("passport_number") or "UNKNOWN"

    # Name fix: remove "Passport No" or invalid tokens
    name = record.get("name") or fields_data.get("name") or "UNKNOWN"
    if name in ("Passport No", "Passport Number", "UNKNOWN", ""):
        name = None

    cursor.execute(
        """
        INSERT INTO records
        (passport_number, name, document_type, fields, errors, tamper_score,
         noise_score, face_match, similarity, liveness_passed,
         risk_score, risk_level, blockchain_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc_number,
            name,
            doc_type,
            json.dumps(record.get("fields", {})),
            json.dumps(record.get("errors", [])),
            record.get("tamper_score", 0),
            record.get("noise_score", 0),
            json.dumps(record.get("face_match", {})),
            record.get("similarity", 0),
            int(bool(record.get("liveness_passed", False))),
            record.get("risk_score", 0),
            record.get("risk_level", "LOW"),
            record.get("blockchain_hash", ""),
            str(datetime.now()),
        ),
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    records = []
    for row in rows:
        record = dict(row)
        record["fields"] = json.loads(record["fields"] or "{}")
        record["errors"] = json.loads(record["errors"] or "[]")
        record["face_match"] = json.loads(record["face_match"] or "{}")
        record["liveness_passed"] = bool(record["liveness_passed"])
        # If document type is known, show proper number
        if record.get("document_type") == "aadhaar":
            record["display_number"] = record["fields"].get("aadhaar_number") or record["passport_number"]
        elif record.get("document_type") == "driving_license":
            record["display_number"] = record["fields"].get("dl_number") or record["passport_number"]
        elif record.get("document_type") == "visa":
            record["display_number"] = record["fields"].get("visa_number") or record["passport_number"]
        else:
            record["display_number"] = record["passport_number"]
        records.append(record)

    return records

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM records")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE risk_level = 'HIGH'")
    high_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE risk_level = 'MEDIUM'")
    medium_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE risk_level = 'LOW'")
    low_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE tamper_score > 0.5")
    tampered_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "total_screened": total,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "tampered_count": tampered_count,
    }

create_table()