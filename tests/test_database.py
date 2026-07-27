"""
Unit tests for DatabaseManager module.
"""

from pathlib import Path
from app.database import DatabaseManager


def test_database_manager_init(tmp_path: Path):
    db_file = tmp_path / "test_app.db"
    db_mgr = DatabaseManager(db_path=db_file)

    assert db_file.exists()

    # Log activity
    db_mgr.log_activity("INFO", "TEST", "Test message", "Details")
    activities = db_mgr.get_recent_activities(limit=10)

    assert len(activities) == 1
    assert activities[0]["level"] == "INFO"
    assert activities[0]["category"] == "TEST"
    assert activities[0]["message"] == "Test message"
