from .database import get_connection


def get_active_session():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT km_inicio, iniciada_en
            FROM sesion_activa
            WHERE id = 1
        """)

        row = cursor.fetchone()

    if not row:
        return None

    return {"km_inicio": row[0], "iniciada_en": row[1]}


def create_active_session(km_inicio, iniciada_en):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sesion_activa (id, km_inicio, iniciada_en)
            VALUES (1, ?, ?)
        """,
            (km_inicio, iniciada_en),
        )

        conn.commit()


def update_active_session(km_inicio, iniciada_en):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sesion_activa
            SET km_inicio = ?, iniciada_en = ?
            WHERE id = 1
        """,
            (km_inicio, iniciada_en),
        )

        conn.commit()


def get_top_sessions(limit=10):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, nombre, km, creado_en
            FROM sesiones
            WHERE km > 0
            ORDER BY km DESC, creado_en DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()

    return [
        {"id": row[0], "nombre": row[1], "km": row[2], "creado_en": row[3]}
        for row in rows
    ]


def get_never_drawn_session():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, nombre, km, foto, creado_en
            FROM sesiones
            WHERE ultimo_sorteo IS NULL
              AND km > 0
            ORDER BY RANDOM()
            LIMIT 1
        """)

        row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "nombre": row[1],
        "km": row[2],
        "foto": row[3],
        "creado_en": row[4],
    }


def get_least_recently_drawn_sessions(limit=5):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, nombre, km, foto, creado_en
            FROM sesiones
            WHERE km > 0
            ORDER BY datetime(ultimo_sorteo) ASC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "nombre": row[1],
            "km": row[2],
            "foto": row[3],
            "creado_en": row[4],
        }
        for row in rows
    ]


def mark_session_as_drawn(session_id, timestamp):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sesiones
            SET ultimo_sorteo = ?
            WHERE id = ?
        """,
            (timestamp, session_id),
        )

        conn.commit()
