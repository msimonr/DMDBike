# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
import os
import uuid
from datetime import datetime, UTC
from PIL import Image, ImageOps


DB_PATH = "bici.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
MAX_MINUTOS_SESION = 30


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "14NOV2025MFMF"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_km_actual():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT km FROM estado WHERE id = 1;")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0

def get_or_refresh_sesion(refresh=True): # Si no hay sesion la crea, si hay la devuelve y si esta vencida y habilitado el refresh la refresca.
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT km_inicio, iniciada_en FROM sesion_activa WHERE id = 1;")
    row = cur.fetchone()
    
    now = datetime.now(UTC)
    km_actual = get_km_actual()
    
    if not row:
        # No hay sesion aun.
        cur.execute("""
            INSERT INTO sesion_activa (id, km_inicio, iniciada_en)
            VALUES (1, ?, ?)                    
    """,(km_actual, now.isoformat()))
        conn.commit()
        conn.close()
        return {"km_inicio": km_actual, "iniciada_en": now.isoformat()}
    
    km_inicio, iniciada_en = row
    inicio_dt = datetime.fromisoformat(iniciada_en)
    mins = (now - inicio_dt).total_seconds() / 60.0
    if (refresh and mins > MAX_MINUTOS_SESION):
        cur.execute("""
            UPDATE sesion_activa
            SET  km_inicio = ?, iniciada_en = ?
            WHERE id = 1;
        """, (km_actual, now.isoformat()))
        
        conn.commit()
        conn.close()
        return {"km_inicio": km_actual, "iniciada_en": now.isoformat()}
    conn.close()
    return {"km_inicio": km_inicio, "iniciada_en": iniciada_en, "minutos": mins}

@app.route("/top_10")
def get_top_10():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    #Get top 10
    cur.execute("""
        SELECT id, nombre, km, creado_en
        FROM sesiones
        WHERE km > 0
        ORDER BY km DESC, creado_en DESC
        LIMIT 10;
    """)
    
    top_rows = cur.fetchall()
    conn.close()
    
    top10 = []
    for tid, tnombre, tkm, tcreado in top_rows:
        top10.append({
            "id": tid,
            "nombre": tnombre,
            "km": tkm,
            "creado_en": tcreado,
        })
        
    return jsonify({"ok": True, "top10": top10})

#:: Routes ::
@app.route("/reset_session", methods=["POST"])
def reset_session():
    km_actual = get_km_actual()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE sesion_activa
        SET km_inicio = ?, iniciada_en = ?
        WHERE id = 1;
    """, (km_actual, datetime.now(UTC).isoformat()))
    conn.commit()
    conn.close()
    return redirect(url_for("upload_pictures"))


@app.route("/random_session")
def random_session():
    #Conexion
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT MIN(veces_sorteada) FROM sesiones;")
    row = cur.fetchone()
    
    if not row or row[0] is None:
        conn.close()
        return jsonify({"ok": False})
    
    
    min_veces = row[0]
    
    # Sorteo 
    cur.execute("""
        SELECT id, nombre, km, foto, creado_en
        FROM sesiones
        WHERE veces_sorteada = ?
        ORDER BY RANDOM()
        LIMIT 1;
    """, (min_veces,))
    
    sesion = cur.fetchone()
    
    if not sesion:
        conn.close()
        return jsonify({"ok": False})
    
    sesion_id, nombre, km, foto, creado_en = sesion
    
    # Actualizar sorteado
    cur.execute("""
                UPDATE sesiones
                SET veces_sorteada = veces_sorteada + 1
                WHERE id = ?;
                """, (sesion_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "ok": True,
        "id": sesion_id,
        "nombre": nombre,
        "km": km,
        "foto": url_for('static', filename=f"uploads/{foto}") if foto else None,
        "creado_en": creado_en
    })
    
    


@app.route("/")
def index():
    km = get_km_actual()
    return render_template("index.html", km=km)

@app.route("/pictures")
def upload_pictures():
    token = str(uuid.uuid4())
    session['form_token'] = token
    return render_template("pictures.html", token=token)

@app.route("/pictures_manual")
def upload_manual():
    token = str(uuid.uuid4())
    session['form_token'] = token
    return render_template("manual.html", token=token)

@app.route("/stats")
def stats():
    km = get_km_actual()
    km_sesion = km - (get_or_refresh_sesion()['km_inicio'])
    km_sesion = km_sesion if km_sesion > 0 else 0.0
    return jsonify({"km": round(km, 6), "km_sesion": round(km_sesion, 6)})

@app.route("/upload", methods=["POST"])
def upload():
    token = request.form.get("token")
    #evita reenvios
    if not token or token == session.get("last_token"):
        return redirect(url_for("upload_pictures"))
    
    session['last_token'] = token
    
    #Traer sesion de pedaleo y km totales actuales
    ses_bike = get_or_refresh_sesion(False)
    km_total = get_km_actual()
    
    #Calcular delta
    km_individual = km_total - ses_bike['km_inicio']
    if (km_individual < 0):
        km_individual = 0.0
    
    nombre = request.form.get("nombre") or ""
     
    file = request.files.get("foto")
    filename = None

    if file and file.filename:
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        filename = f"{ts}.webp" #Webp para tamanio reducido
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # abrir con Pillow, max tamanio manteniendo aspect ratio.
        img = Image.open(file.stream)
        
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((1024, 1024))
        # guardar comprimido
        img.save(save_path, "WEBP", quality=70, method=6)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sesiones (nombre, km, foto, creado_en)
        VALUES (?, ?, ?, ?);
    """, (nombre, km_individual, filename, datetime.now(UTC).isoformat()))
    
    cur.execute("""
        UPDATE sesion_activa
        SET km_inicio = ?, iniciada_en = ?
        WHERE id = 1;
    """, (km_total, datetime.now(UTC).isoformat()))
    
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
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        img = Image.open(file.stream)
        # corregir vertical de celular
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # limitar tamaño
        img.thumbnail((1024, 1024))
        # guardar comprimido
        img.save(save_path, "WEBP", quality=70, method=6)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sesiones (nombre, km, foto, creado_en)
        VALUES (?, ?, ?, ?);
    """, (nombre, km_val, filename, datetime.now(UTC).isoformat()))
    conn.commit()
    conn.close()

    return redirect(url_for("upload_pictures"))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
