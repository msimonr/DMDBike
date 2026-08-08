from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import sqlite3
import base64


# ============================================================
# CONFIGURACIÓN
# ============================================================

DB_PATH = "backend/bici.db"

PLANTILLA_PATH = Path("plantilla.png")
UPLOADS_PATH = Path("backend/static/uploads")
OUTPUT_PATH = Path("imagen")

PLANTILLA_W = 868
PLANTILLA_H = 1424

FOTO_W = 768
FOTO_H = 1024


# ============================================================
# FORMATTERS
# ============================================================

def format_fecha(fecha):
    fecha = datetime.fromisoformat(fecha)
    return fecha.strftime("%d/%m/%Y")


def format_km(km):
    if km < 1:
        return f"{round(km * 1000)} m"

    return f"{km:.1f} km"


# ============================================================
# IMAGEN → BASE64
# ============================================================

def imagen_base64(path):

    extension = path.suffix.lower()

    if extension == ".png":
        mime = "image/png"
    elif extension in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif extension == ".webp":
        mime = "image/webp"
    else:
        raise ValueError(f"Formato no soportado: {extension}")

    data = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime};base64,{data}"


# ============================================================
# LEER SQLITE
# ============================================================

conn = sqlite3.connect(DB_PATH)

conn.row_factory = sqlite3.Row

cur = conn.cursor()

cur.execute("""
    SELECT id, nombre, km, foto, creado_en
    FROM sesiones
    WHERE km > 0
    ORDER BY id DESC
""")

sesiones = cur.fetchall()

conn.close()


print(f"Sesiones encontradas: {len(sesiones)}")


# ============================================================
# PREPARAR ARCHIVOS
# ============================================================

plantilla_base64 = imagen_base64(
    PLANTILLA_PATH
)

OUTPUT_PATH.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PLAYWRIGHT
# ============================================================

with sync_playwright() as p:

    browser = p.firefox.launch(
        headless=True
    )

    page = browser.new_page(
        viewport={
            "width": PLANTILLA_W,
            "height": PLANTILLA_H
        },
        device_scale_factor=1
    )


    # ========================================================
    # RECORRER SESIONES
    # ========================================================

    for s in sesiones:

        print(
            f"Procesando ID {s['id']} - "
            f"{s['nombre']}"
        )


        # ----------------------------------------------------
        # Buscar foto
        # ----------------------------------------------------

        foto_path = UPLOADS_PATH / s["foto"]


        if not foto_path.exists():

            print(
                f"  ⚠️ No se encontró: {foto_path}"
            )

            continue


        # ----------------------------------------------------
        # Datos
        # ----------------------------------------------------

        nombre = s["nombre"] or "El/ella"

        km = format_km(
            s["km"]
        )

        fecha = format_fecha(
            s["creado_en"]
        )


        # ----------------------------------------------------
        # Foto
        # ----------------------------------------------------

        foto_base64 = imagen_base64(
            foto_path
        )


        # ----------------------------------------------------
        # HTML
        # ----------------------------------------------------

        html = f"""
        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="UTF-8">

        <style>

            * {{
                box-sizing: border-box;
            }}

            html,
            body {{
                margin: 0;
                padding: 0;

                width: {PLANTILLA_W}px;
                height: {PLANTILLA_H}px;

                overflow: hidden;
            }}


            .contenedor {{
                position: relative;

                width: {PLANTILLA_W}px;
                height: {PLANTILLA_H}px;

                background-image: url("{plantilla_base64}");

                background-size:
                    {PLANTILLA_W}px
                    {PLANTILLA_H}px;

                background-repeat: no-repeat;
            }}


            .foto {{
                position: absolute;

                left: 50px;
                top: 143px;

                width: {FOTO_W}px;
                height: {FOTO_H}px;

                object-fit: cover;
            }}


            .nombre {{
                position: absolute;

                top: 40px;
                left: 0;

                width: {PLANTILLA_W}px;

                text-align: center;

                font-family:
                    Arial,
                    sans-serif;
                color: blue;
                font-size: 80px;

                font-weight: bold;
            }}


            .info {{
                position: absolute;

                top: 1200px;
                left: 0;

                width: {PLANTILLA_W}px;

                text-align: center;

                font-family:
                    Arial,
                    sans-serif;

                font-size: 60px;

                color: blue;

                line-height: 1.3;
            }}

        </style>

        </head>

        <body>

            <div class="contenedor">

                <img
                    class="foto"
                    src="{foto_base64}"
                >

                <div class="nombre">
                    {nombre}
                </div>

                <div class="info">

                    SUMÓ<br>

                    {km}<br>

                    {fecha}

                </div>

            </div>

        </body>

        </html>
        """


        # ----------------------------------------------------
        # Renderizar
        # ----------------------------------------------------

        page.set_content(
            html
        )


        # Esperar fuentes
        page.evaluate(
            "() => document.fonts.ready"
        )


        # ----------------------------------------------------
        # Guardar
        # ----------------------------------------------------

        output_file = (
            OUTPUT_PATH /
            f"{s['id']}-{s['nombre']}.png"
        )


        page.screenshot(
            path=str(output_file),
            full_page=True
        )


        print(
            f"  ✓ Generada: {output_file}"
        )


    browser.close()


print("Proceso terminado.")