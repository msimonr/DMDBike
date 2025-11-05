# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
import os
import uuid
from datetime import datetime, UTC
from PIL import Image, ImageOps


DB_PATH = "bici.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")

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

@app.route("/stats")
def stats():
    km = get_km_actual()
    return jsonify({"km": round(km, 6)})

@app.route("/upload", methods=["POST"])
def upload():
    token = request.form.get("token")
    
    #evita reenvios
    if not token or token == session.get("last_token"):
        return redirect(url_for("upload_pictures"))
    
    session['last_token'] = token
    
    nombre = request.form.get("nombre") or ""
    km_str = request.form.get("km_individual")
    if km_str:
        try:
            km_actual = float(km_str)
        except ValueError:
            km_actual = 0.1
    else:
        km_actual = 0.1
    
    file = request.files.get("foto")
    filename = None

    if file and file.filename:
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        filename = f"{ts}.webp" #Webp para tamanio reducido
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # abrir con Pillow, max tamanio manteniendo aspect ratio.
        img = Image.open(file.stream)
        
        img = ImageOps.exif_transpose(img)
        
        img.thumbnail((1024, 1024))
        # guardar comprimido
        img.save(save_path, "WEBP", quality=70, method=6)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sesiones (nombre, km, foto, creado_en)
        VALUES (?, ?, ?, ?);
    """, (nombre, km_actual, filename, datetime.now(UTC).isoformat()))
    conn.commit()
    conn.close()
    return redirect(url_for("upload_pictures"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
