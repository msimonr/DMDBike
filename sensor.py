# sensor.py
import sqlite3
from datetime import datetime, UTC
import time
import RPi.GPIO as GPIO
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "bici.db")

# CONFIGURACIÓN DE TU RUEDA
WHEEL_CIRCUMFERENCE_M = 2.10  # 2,10 m de perímetro
MAGNETS_PER_WHEEL = 1

# PIN DEL SENSOR
SENSOR_PIN = 3

# anti-rebote en ms
DEBOUNCE_MS = 150

def agregar_distancia(metros: float):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT km FROM estado WHERE id = 1;")
    row = cur.fetchone()
    km_actual = row[0] if row else 0.0
    km_nuevo = km_actual + (metros / 1000.0)
    print('km_actual:', km_actual)
    cur.execute(
        "UPDATE estado SET km = ?, actualizado_en = ? WHERE id = 1;",
        (km_nuevo, datetime.now(UTC).isoformat())
    )
    conn.commit()
    conn.close()

def sensor_callback(channel):
    metros = WHEEL_CIRCUMFERENCE_M / MAGNETS_PER_WHEEL
    try:
        agregar_distancia(metros)
        print("Pulso detectado, sumé", metros, "m")
    except Exception as e:
        print("Error guardando distancia:", e)

def main():
    # setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)
    
    # detectar flanco descendente (HIGH -> LOW)
    GPIO.add_event_detect(
        SENSOR_PIN,
        GPIO.FALLING,
        callback=sensor_callback,
        bouncetime=DEBOUNCE_MS
    )

    print("Sensor listo. Esperando pulsos... Ctrl+C para salir.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Saliendo...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
