"""
modules/csv_export.py
Exports a list of screening records (as returned by database.get_records())
to a CSV file, for use in Excel/reporting.
"""

import csv


FIELDNAMES = [
    "id",
    "passport_number",
    "name",
    "document_type",
    "tamper_score",
    "noise_score",
    "similarity",
    "liveness_passed",
    "risk_score",
    "risk_level",
    "blockchain_hash",
    "created_at",
]


def export_to_csv(records: list, output_path: str = "records_export.csv") -> str:
    """
    Write `records` (list of dicts) to a CSV file at `output_path`.
    Only the columns in FIELDNAMES are written; extra dict keys
    (like nested `fields`/`errors`) are skipped to keep the CSV flat.
    Returns the output path.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    return output_path


if __name__ == "__main__":
    sample_records = [
        {
            "id": 1,
            "passport_number": "A1234567",
            "name": "John Doe",
            "document_type": "passport",
            "tamper_score": 0.12,
            "noise_score": 0.08,
            "similarity": 0.91,
            "liveness_passed": True,
            "risk_score": 25.5,
            "risk_level": "LOW",
            "blockchain_hash": "abcd1234",
            "created_at": "2026-01-01 10:00:00",
        }
    ]
    print(export_to_csv(sample_records, "sample_export.csv"))