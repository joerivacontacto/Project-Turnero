"""Test imports to verify the application structure."""
import sys
sys.path.insert(0, "/home/fulbo/.hermes/kanban/workspaces/t_1ddf4a95")

try:
    from app.config import get_settings
    print("config OK")

    from app.database import get_connection, init_schema, get_db
    print("database OK")

    from app.models import Usuario, Peluquero, Servicio, Cliente, Turno, Horario, Ausencia
    print("models OK")

    from app.schemas import (
        LoginRequest, TokenResponse, UsuarioResponse,
        PeluqueroCreate, PeluqueroUpdate, PeluqueroResponse,
        ServicioCreate, ServicioUpdate, ServicioResponse,
        ClienteCreate, ClienteUpdate, ClienteResponse,
        TurnoCreate, TurnoUpdateEstado, TurnoResponse,
        HorarioCreate, HorarioResponse,
        AusenciaCreate, AusenciaResponse,
    )
    print("schemas OK")

    from app.auth.jwt import hash_password, verify_password, create_access_token, decode_token, get_current_user, require_rol, oauth2_scheme
    print("auth.jwt OK")

    from app.services.turno_service import TurnoService
    print("services.turno_service OK")

    from app.utils.time import ahora, ahora_str, hoy_str, validate_time_format, validate_date_format, add_minutes, time_to_minutes, format_fecha_arg
    print("utils.time OK")

    from app.routes import auth, peluqueros, servicios, clientes, turnos, agenda, admin
    print("routes OK")

    from app.main import app
    print("main OK")

    print("\n=== ALL IMPORTS SUCCESSFUL ===")

except Exception as e:
    print(f"IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
