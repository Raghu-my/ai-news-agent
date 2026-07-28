# database.py
# PostgreSQL State Tracker with fallback support for local testing

import os
import uuid
import datetime
from typing import List, Dict, Any, Optional

# Database connection URL from environment variable
# e.g., postgresql://user:password@localhost:5432/ainews
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if psycopg2 or sqlite3 should be used
USE_POSTGRES = bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3

DB_FILE = os.getenv("SQLITE_DB_PATH", "ai_news_tracker.db")


def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Initialize the videos tracking table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS videos (
            id VARCHAR(36) PRIMARY KEY,
            topic TEXT NOT NULL,
            script TEXT,
            audio_gcs_uri TEXT,
            video_gcs_uri TEXT,
            status VARCHAR(50) NOT NULL,
            youtube_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    else:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            script TEXT,
            audio_gcs_uri TEXT,
            video_gcs_uri TEXT,
            status TEXT NOT NULL,
            youtube_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("[DB Init] Videos tracking database initialized successfully.")


def create_video_record(topic: str, script: Optional[str] = None) -> str:
    """Create a new video tracking record and return its UUID."""
    video_id = str(uuid.uuid4())
    status = "SCRIPTED" if script else "PENDING"
    now = datetime.datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute(
            """
            INSERT INTO videos (id, topic, script, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (video_id, topic, script, status, now)
        )
    else:
        cursor.execute(
            """
            INSERT INTO videos (id, topic, script, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (video_id, topic, script, status, now)
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[DB Record] Created video record: {video_id} (Status: {status})")
    return video_id


def update_video_status(
    video_id: str,
    status: str,
    script: Optional[str] = None,
    audio_gcs_uri: Optional[str] = None,
    video_gcs_uri: Optional[str] = None,
    youtube_url: Optional[str] = None
):
    """Update video record fields and status."""
    conn = get_connection()
    cursor = conn.cursor()

    fields = ["status = %s" if USE_POSTGRES else "status = ?"]
    params = [status]

    if script is not None:
        fields.append("script = %s" if USE_POSTGRES else "script = ?")
        params.append(script)
    if audio_gcs_uri is not None:
        fields.append("audio_gcs_uri = %s" if USE_POSTGRES else "audio_gcs_uri = ?")
        params.append(audio_gcs_uri)
    if video_gcs_uri is not None:
        fields.append("video_gcs_uri = %s" if USE_POSTGRES else "video_gcs_uri = ?")
        params.append(video_gcs_uri)
    if youtube_url is not None:
        fields.append("youtube_url = %s" if USE_POSTGRES else "youtube_url = ?")
        params.append(youtube_url)

    params.append(video_id)

    sql_query = f"UPDATE videos SET {', '.join(fields)} WHERE id = {'%s' if USE_POSTGRES else '?'}"
    cursor.execute(sql_query, params)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[DB Record] Updated video {video_id} -> Status: {status}")


def get_pending_videos() -> List[Dict[str, Any]]:
    """Retrieve all pending or non-published video records."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_POSTGRES:
        cursor.execute("SELECT * FROM videos WHERE status != 'PUBLISHED' ORDER BY created_at ASC")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
    else:
        cursor.execute("SELECT * FROM videos WHERE status != 'PUBLISHED' ORDER BY created_at ASC")
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]

    cursor.close()
    conn.close()
    return result


# Initialize database schema on module import
init_db()
