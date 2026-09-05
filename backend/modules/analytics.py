"""
modules/analytics.py
Aggregated statistics for the dashboard, built on top of database.py.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_stats, get_records  # noqa: E402


def get_dashboard_stats():
    """
    Returns a summary dict:
      - total_screened
      - high_risk_count
      - low_risk_count
      - tampered_count
    """
    stats = get_stats()
    return {
        "total_screened": stats.get("total_screened", 0),
        "high_risk_count": stats.get("high_risk_count", 0),
        "medium_risk_count": stats.get("medium_risk_count", 0),
        "low_risk_count": stats.get("low_risk_count", 0),
        "tampered_count": stats.get("tampered_count", 0),
    }


def get_recent_activity(limit: int = 10):
    """Return the most recent N screening records."""
    records = get_records()
    return records[:limit]


if __name__ == "__main__":
    print(get_dashboard_stats())
    print(get_recent_activity(5))