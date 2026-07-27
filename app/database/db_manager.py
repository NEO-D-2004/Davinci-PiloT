"""
SQLite Database Manager module.
Manages SQLite database initialization, migrations, session logging, and command history storage.
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from app.services.logger_service import app_logger


class DatabaseManager:
    """Manages SQLite database operations for DaVinci PiloT."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            db_dir = Path(__file__).resolve().parent.parent / "database"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "app.db"
        
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new SQLite database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # App Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        end_time DATETIME,
                        app_version TEXT NOT NULL
                    )
                """)

                # Activity Log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        level TEXT NOT NULL,
                        category TEXT NOT NULL,
                        message TEXT NOT NULL,
                        details TEXT
                    )
                """)

                # Command History table (for AI and Resolve actions)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        command_type TEXT NOT NULL,
                        prompt TEXT,
                        action_taken TEXT,
                        status TEXT NOT NULL,
                        error_message TEXT
                    )
                """)

                conn.commit()
                app_logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            app_logger.error(f"Failed to initialize SQLite database: {e}")
            raise

    def log_activity(self, level: str, category: str, message: str, details: str = "") -> None:
        """Log an activity entry into database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO activity_logs (level, category, message, details) VALUES (?, ?, ?, ?)",
                    (level, category, message, details),
                )
                conn.commit()
        except Exception as e:
            app_logger.error(f"Failed to insert activity log to DB: {e}")

    def get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent activity logs."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            app_logger.error(f"Failed to query recent activities: {e}")
            return []


# Global singleton database manager
db_manager = DatabaseManager()
