"""Database connection using built-in sqlite3."""
import sqlite3
import threading
from app.config import get_settings

settings = get_settings()
_db_local = threading.local()

def get_connection() -> sqlite3.Connection:
    if not hasattr(_db_local, "conn") or _db_local.conn is None:
        conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _db_local.conn = conn
    return _db_local.conn

async def get_db():
    """FastAPI dependency that yields a database connection."""
    conn = get_connection()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise

def init_schema(conn: sqlite3.Connection):
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'recepcionista',
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS peluqueros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            duracion_min INTEGER NOT NULL,
            precio INTEGER NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS peluqueros_servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peluquero_id INTEGER NOT NULL REFERENCES peluqueros(id) ON DELETE CASCADE,
            servicio_id INTEGER NOT NULL REFERENCES servicios(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peluquero_id INTEGER NOT NULL REFERENCES peluqueros(id) ON DELETE CASCADE,
            dia_semana INTEGER NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            UNIQUE(peluquero_id, dia_semana)
        );
        CREATE TABLE IF NOT EXISTS ausencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peluquero_id INTEGER NOT NULL REFERENCES peluqueros(id) ON DELETE CASCADE,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            motivo TEXT
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            activo INTEGER NOT NULL DEFAULT 1,
            creado_en TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            peluquero_id INTEGER NOT NULL REFERENCES peluqueros(id),
            servicio_id INTEGER NOT NULL REFERENCES servicios(id),
            fecha TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente' CHECK(estado IN ('pendiente','confirmado','en_curso','completado','cancelado')),
            tolerancia_min INTEGER NOT NULL DEFAULT 5,
            creado_en TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recordatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turno_id INTEGER NOT NULL REFERENCES turnos(id) ON DELETE CASCADE,
            tipo TEXT NOT NULL,
            enviado_en TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente'
        );
    """)
    conn.commit()
