from flask import current_app
from datetime import datetime, UTC
import random

from app.repositories import session_repository
from app.repositories.state_repository import get_current_km


def get_or_refresh_session(refresh=True):
    session = session_repository.get_active_session()

    now = datetime.now(UTC)
    km_actual = get_current_km()

    # No existe una sesión activa todavía
    if session is None:
        now_iso = now.isoformat()

        session_repository.create_active_session(
            km_inicio=km_actual, iniciada_en=now_iso
        )

        return {"km_inicio": km_actual, "iniciada_en": now_iso}

    km_inicio = session["km_inicio"]
    iniciada_en = session["iniciada_en"]

    inicio_dt = datetime.fromisoformat(iniciada_en)

    minutos = (now - inicio_dt).total_seconds() / 60.0

    max_minutos = current_app.config["MAX_MINUTOS_SESION"]

    if refresh and minutos > max_minutos:
        now_iso = now.isoformat()

        session_repository.update_active_session(
            km_inicio=km_actual, iniciada_en=now_iso
        )

        return {"km_inicio": km_actual, "iniciada_en": now_iso}

    return {"km_inicio": km_inicio, "iniciada_en": iniciada_en, "minutos": minutos}


def get_top_sessions():
    return session_repository.get_top_sessions(10)


def get_random_session():
    session = session_repository.get_never_drawn_session()

    if session is None:
        sessions = session_repository.get_least_recently_drawn_sessions(5)

        if not sessions:
            return None

        session = random.choice(sessions)

    session_repository.mark_session_as_drawn(
        session["id"], datetime.now(UTC).isoformat()
    )

    return session
