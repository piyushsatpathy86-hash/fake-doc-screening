"""
alert.py
Sends (mock) alerts when a screening result is high risk.
Replace the mock functions with real email/SMS providers
(e.g. SMTP, Twilio, SNS) in production.
"""

from datetime import datetime

HIGH_RISK_THRESHOLD = 60


def send_email_alert(passport_number: str, risk_score: float):
    print("=" * 50)
    print("[MOCK EMAIL] To: security-team@ssb.gov.in")
    print(f"Subject: HIGH RISK ALERT - Passport {passport_number}")
    print(
        f"Body: Document with passport number '{passport_number}' "
        f"was flagged HIGH RISK (score: {risk_score}) at {datetime.now()}."
    )
    print("=" * 50)


def send_sms_alert(passport_number: str, risk_score: float):
    print("=" * 50)
    print("[MOCK SMS] To: +91-9999999999")
    print(f"ALERT: Passport {passport_number} flagged HIGH RISK (score: {risk_score}).")
    print("=" * 50)


def send_alert(risk_score: float, passport_number: str = "UNKNOWN"):
    """
    Called after risk scoring. Sends mock email + SMS alerts when
    risk_score exceeds HIGH_RISK_THRESHOLD. Returns True if an alert
    was sent, False otherwise.
    """
    if risk_score > HIGH_RISK_THRESHOLD:
        print(f"[ALERT] HIGH RISK detected for passport {passport_number} "
              f"(score={risk_score}). Sending notifications...")
        send_email_alert(passport_number, risk_score)
        send_sms_alert(passport_number, risk_score)
        return True

    print(f"[INFO] Risk score {risk_score} for passport {passport_number} "
          f"is within acceptable range. No alert sent.")
    return False


if __name__ == "__main__":
    send_alert(75, "A1234567")
    send_alert(30, "B7654321")