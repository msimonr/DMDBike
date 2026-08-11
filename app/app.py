# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime, UTC
from PIL import Image, ImageOps
from app.config import Config
from app.repositories.state_repository import get_current_km
from app.services.session_service import (
    get_or_refresh_session,
    get_top_sessions,
    get_random_session,
)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


# Crear carpeta de uploads si no existe
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/status")
def status():
    return jsonify({"ok": True})


@app.route("/sync")
def sync_view():
    return render_template("sync.html")


@app.route("/sync_time", methods=["POST"])
def sync_time():
    data = request.get_json()
    hora = data.get("hora")
    try:
        return jsonify({"ok": True, "msg": f"Hora del sistema actualizada a {hora}"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/top_10")
def get_top_10():
    top10 = get_top_sessions()
    return jsonify({"ok": True, "top10": top10})


@app.route("/reset_session", methods=["POST"])
def reset_session():
    km_actual = get_current_km()
    conn = sqlite3.connect(app.config["DB_PATH"])
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE sesion_activa
        SET km_inicio = ?, iniciada_en = ?
        WHERE id = 1;
    """,
        (km_actual, datetime.now(UTC).isoformat()),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("upload_pictures"))


@app.route("/random_session")
def random_session():
    selected_session = get_random_session()

    if selected_session is None:
        return jsonify({"ok": False})

    return jsonify(
        {
            "ok": True,
            "id": selected_session["id"],
            "nombre": selected_session["nombre"],
            "km": selected_session["km"],
            "foto": (
                url_for("static", filename=f"uploads/{selected_session['foto']}")
                if selected_session["foto"]
                else None
            ),
            "creado_en": selected_session["creado_en"],
        }
    )


@app.route("/")
def index():
    km = get_current_km()
    return render_template("index.html", km=km)


@app.route("/pictures")
def upload_pictures():
    token = str(uuid.uuid4())
    session["form_token"] = token
    return render_template("pictures.html", token=token)


@app.route("/pictures_manual")
def upload_manual():
    token = str(uuid.uuid4())
    session["form_token"] = token
    return render_template("manual.html", token=token)


@app.route("/stats")
def stats():
    km = get_current_km()
    km_sesion = km - (get_or_refresh_session()["km_inicio"])
    km_sesion = km_sesion if km_sesion > 0 else 0.0
    return jsonify({"km": round(km, 6), "km_sesion": round(km_sesion, 6)})


@app.route("/upload", methods=["POST"])
def upload():
    token = request.form.get("token")

    # evita reenvios
    if not token or token == session.get("last_token"):
        return redirect(url_for("upload_pictures"))

    session["last_token"] = token

    # Traer sesion de pedaleo y km totales actuales
    ses_bike = get_or_refresh_session(False)
    km_total = get_current_km()

    km_individual = km_total - ses_bike["km_inicio"]
    if km_individual < 0:
        km_individual = 0.0

    nombre = request.form.get("nombre") or ""

    file = request.files.get("foto")
    filename = None

    if file and file.filename:
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        filename = f"{ts}.webp"  # Webp para tamanio reducido
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # abrir con Pillow, max tamanio manteniendo aspect ratio.
        img = Image.open(file.stream)

        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((1024, 1024))

        # guardar comprimido
        img.save(save_path, "WEBP", quality=70, method=6)

    conn = sqlite3.connect(app.config["DB_PATH"])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sesiones (nombre, km, foto, creado_en)
        VALUES (?, ?, ?, ?);
    """,
        (nombre, km_individual, filename, datetime.now(UTC).isoformat()),
    )

    cur.execute(
        """
        UPDATE sesion_activa
        SET km_inicio = ?, iniciada_en = ?
        WHERE id = 1;
    """,
        (km_total, datetime.now(UTC).isoformat()),
    )

    conn.commit()
    conn.close()

    return redirect(url_for("upload_pictures"))


@app.route("/insertar_manual", methods=["POST"])
def insertar_manual():
    nombre = request.form.get("nombre") or ""
    km_str = request.form.get("km")

    try:
        km_val = float(km_str)
    except ValueError:
        km_val = 0.1

    file = request.files.get("foto")
    filename = None

    if file and file.filename:
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        filename = f"{ts}.webp"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        img = Image.open(file.stream)
        # corregir vertical de celular
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # limitar tamaño
        img.thumbnail((1024, 1024))
        # guardar comprimido
        img.save(save_path, "WEBP", quality=70, method=6)

    conn = sqlite3.connect(app.config["DB_PATH"])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sesiones (nombre, km, foto, creado_en)
        VALUES (?, ?, ?, ?);
    """,
        (nombre, km_val, filename, datetime.now(UTC).isoformat()),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("upload_pictures"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
