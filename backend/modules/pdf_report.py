"""
modules/pdf_report.py
Generates a one-page PDF summary of a screening result using reportlab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


def generate_pdf_report(result_dict: dict, output_path: str = "screening_report.pdf") -> str:
    """
    Build a PDF report from a screening result dict (the same shape
    returned by the /upload endpoint) and save it to `output_path`.
    Returns the output path.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=2 * cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Document Screening Report", styles["Title"]))
    elements.append(Paragraph("Sashastra Seema Bal (SSB) - SIH PS 26188", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    fields = result_dict.get("fields", {}) or {}
    summary_rows = [
        ["Field", "Value"],
        ["Name", str(fields.get("name", "N/A"))],
        ["Passport Number", str(fields.get("passport_number", "N/A"))],
        ["Document Type", str(result_dict.get("document_type", "N/A"))],
        ["Date of Birth", str(fields.get("date_of_birth", "N/A"))],
        ["Date of Expiry", str(fields.get("date_of_expiry", "N/A"))],
        ["Tamper Score", str(result_dict.get("tamper_score", "N/A"))],
        ["Noise Score", str(result_dict.get("noise_score", "N/A"))],
        ["Face Match", str(result_dict.get("face_match", "N/A"))],
        ["Similarity", str(result_dict.get("similarity", "N/A"))],
        ["Liveness Passed", str(result_dict.get("liveness_passed", "N/A"))],
        ["Risk Score", str(result_dict.get("risk_score", "N/A"))],
        ["Risk Level", str(result_dict.get("risk_level", "N/A"))],
        ["Blockchain Hash", str(result_dict.get("blockchain_hash", "N/A"))[:40]],
    ]

    table = Table(summary_rows, colWidths=[6 * cm, 9 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(table)

    elements.append(Spacer(1, 0.5 * cm))
    errors = result_dict.get("errors", [])
    if errors:
        elements.append(Paragraph("Validation Errors:", styles["Heading3"]))
        for err in errors:
            elements.append(Paragraph(f"- {err}", styles["Normal"]))
    else:
        elements.append(Paragraph("No validation errors found.", styles["Normal"]))

    doc.build(elements)
    return output_path


if __name__ == "__main__":
    sample_result = {
        "fields": {"name": "John Doe", "passport_number": "A1234567"},
        "document_type": "passport",
        "tamper_score": 0.12,
        "noise_score": 0.08,
        "face_match": True,
        "similarity": 0.91,
        "liveness_passed": True,
        "risk_score": 25.5,
        "risk_level": "LOW",
        "blockchain_hash": "abcd1234efgh5678",
        "errors": [],
    }
    print(generate_pdf_report(sample_result, "sample_report.pdf"))