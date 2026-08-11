from .database import get_connection


def get_current_km():
    with get_connection() as conn:
        cursor = conn.execute("SELECT km FROM estado WHERE id = 1")

        row = cursor.fetchone()

    return row[0] if row else 0.0
