"""
database.py
SQLite storage ("records.db") for every document screening result.
"""

import sqlite3
import json
from datetime import datetime

DB_NAME = "records.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Create the records table if it doesn't already exist."""
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
    """Insert one screening record (dict) into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO records
        (passport_number, name, document_type, fields, errors, tamper_score,
         noise_score, face_match, similarity, liveness_passed,
         risk_score, risk_level, blockchain_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.get("passport_number", "UNKNOWN"),
            record.get("name", "UNKNOWN"),
            record.get("document_type", "unknown"),
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
    """Return all records as a list of dicts, most recent first."""
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
        records.append(record)

    return records


def get_stats():
    """Return aggregate counts used by the analytics/dashboard endpoints."""
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


# Make sure the table exists as soon as this module is imported
create_table()


if __name__ == "__main__":
    save_record(
        {
            "passport_number": "A1234567",
            "name": "John Doe",
            "document_type": "passport",
            "fields": {"dob": "1990-01-01"},
            "errors": [],
            "tamper_score": 0.2,
            "noise_score": 0.1,
            "face_match": {"match": True, "similarity": 0.92},
            "similarity": 0.92,
            "liveness_passed": True,
            "risk_score": 35,
            "risk_level": "LOW",
            "blockchain_hash": "abc123",
        }
    )
    print(get_records())
    print(get_stats())