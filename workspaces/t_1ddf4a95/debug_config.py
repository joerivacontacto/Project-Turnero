"""Debug config loading."""
import os
print("CWD:", os.getcwd())
print("ENV FILE EXISTS:", os.path.exists(".env"))
print("TIMEZONE from env:", repr(os.getenv("TIMEZONE")))
print("TZ from env:", repr(os.getenv("TZ")))

# Try loading with pydantic_settings
from app.config import get_settings
settings = get_settings()
print("settings.TIMEZONE:", repr(settings.TIMEZONE))
