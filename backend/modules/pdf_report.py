from fpdf import FPDF
from datetime import datetime

def generate_pdf_report(name, passport_number, risk_score, is_match, is_live, save_path="report.pdf"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Document Verification Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Passport Number: {passport_number}", ln=True)
    pdf.cell(0, 10, f"Face Match: {'YES' if is_match else 'NO'}", ln=True)
    pdf.cell(0, 10, f"Liveness Check: {'PASSED' if is_live else 'FAILED'}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)

    if risk_score < 30:
        status = "LOW RISK - Likely Genuine"
    elif risk_score < 70:
        status = "MEDIUM RISK - Needs Review"
    else:
        status = "HIGH RISK - Likely Fake"

    pdf.cell(0, 10, f"Risk Score: {risk_score}/100", ln=True)
    pdf.cell(0, 10, f"Status: {status}", ln=True)

    pdf.output(save_path)
    return save_path


if __name__ == "__main__":
    path = generate_pdf_report("John Doe", "P1234567", 25, True, True)
    print(f"Report saved at {path}")