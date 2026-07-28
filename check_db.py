# check_db.py
# Database connectivity test helper for run_diagnostics.ps1

import database

try:
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM videos")
    count = cursor.fetchone()[0]
    print(f"DB_OK: {count}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"DB_ERR: {e}")
