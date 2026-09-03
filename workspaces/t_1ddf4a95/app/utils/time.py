from datetime import datetime, timedelta
import pytz
from app.config import get_settings

settings = get_settings()

def ahora() -> datetime:
    tz_name = settings.TIMEZONE or "America/Argentina/Buenos_Aires"
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
    return datetime.now(tz)

def ahora_str() -> str:
    return ahora().strftime("%Y-%m-%d %H:%M:%S")

def hoy_str() -> str:
    return ahora().strftime("%Y-%m-%d")

def validate_time_format(time_str: str) -> bool:
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def validate_date_format(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def add_minutes(time_str: str, minutes: int) -> str:
    dt = datetime.strptime(time_str, "%H:%M")
    dt = dt + timedelta(minutes=minutes)
    return dt.strftime("%H:%M")

def time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m

def format_fecha_arg(fecha: str) -> str:
    """Convierte YYYY-MM-DD a DD/MM/YYYY para mostrar en UI."""
    try:
        dt = datetime.strptime(fecha, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return fecha
