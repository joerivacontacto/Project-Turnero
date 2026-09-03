"""Script para inicializar la base de datos con datos de ejemplo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_connection, init_schema
from app.auth.jwt import hash_password
from app.utils.time import ahora_str

def init_db():
    conn = get_connection()
    init_schema(conn)

    try:
        # Verificar si ya hay datos
        count = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        if count > 0:
            print("La base de datos ya tiene datos. Saltando inicialización.")
            return

        # Crear usuario admin
        conn.execute(
            "INSERT INTO usuarios (username, password_hash, rol, activo, creado_en) VALUES (?, ?, 'admin', 1, ?)",
            ("admin", hash_password("admin123"), ahora_str()),
        )

        # Crear peluqueros
        peluqueros = [
            ("Carlos López",),
            ("María García",),
        ]
        for p in peluqueros:
            conn.execute("INSERT INTO peluqueros (nombre, activo, creado_en) VALUES (?, 1, ?)", (p[0], ahora_str()))

        # Crear servicios
        servicios = [
            ("Corte", 30, 1500),
            ("Corte + Barba", 45, 2000),
            ("Tintura", 60, 3000),
        ]
        for s in servicios:
            conn.execute("INSERT INTO servicios (nombre, duracion_min, precio, activo, creado_en) VALUES (?, ?, ?, 1, ?)", (s[0], s[1], s[2], ahora_str()))

        # Asignar servicios a peluqueros
        for p_id in [1, 2]:
            for s_id in [1, 2, 3]:
                conn.execute("INSERT INTO peluqueros_servicios (peluquero_id, servicio_id) VALUES (?, ?)", (p_id, s_id))

        # Crear horarios (lunes a viernes 9-18, sábados 9-13)
        for p_id in [1, 2]:
            for dia in range(5):  # Lunes a viernes
                conn.execute("INSERT INTO horarios (peluquero_id, dia_semana, hora_inicio, hora_fin) VALUES (?, ?, '09:00', '18:00')", (p_id, dia))
            conn.execute("INSERT INTO horarios (peluquero_id, dia_semana, hora_inicio, hora_fin) VALUES (?, 5, '09:00', '13:00')", (p_id,))

        # Crear clientes
        clientes = [
            ("Juan Pérez", "11-1234-5678", "juan@email.com"),
            ("Ana Rodríguez", "11-8765-4321", "ana@email.com"),
        ]
        for c in clientes:
            conn.execute("INSERT INTO clientes (nombre, telefono, email, activo, creado_en) VALUES (?, ?, ?, 1, ?)", (c[0], c[1], c[2], ahora_str()))

        conn.commit()
        print("Base de datos inicializada con datos de ejemplo.")
        print("Usuario: admin / admin123")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    init_db()
