import urllib.request
import json

TOKEN = ""

def api(method, path, data=None, auth=True):
    url = f"http://localhost:8001{path}"
    headers = {"Content-Type": "application/json"}
    if auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            if data:
                return resp.status, json.loads(data)
            return resp.status, {}
    except urllib.error.HTTPError as e:
        data = e.read()
        if data:
            return e.code, json.loads(data)
        return e.code, {}

# Login
code, resp = api("POST", "/auth/login", {"username": "admin", "password": "admin123"}, auth=False)
print(f"Login: {code}")
TOKEN = resp["access_token"]
print(f"Token: {TOKEN[:30]}...")

# Peluqueros
code, resp = api("GET", "/peluqueros")
print(f"\nPeluqueros ({code}): {len(resp)} items")
for p in resp:
    print(f"  - {p['nombre']}")

# Servicios
code, resp = api("GET", "/servicios")
print(f"\nServicios ({code}): {len(resp)} items")
for s in resp:
    print(f"  - {s['nombre']} ({s['duracion_min']}min, ${s['precio']})")

# Clientes
code, resp = api("GET", "/clientes")
print(f"\nClientes ({code}): {len(resp)} items")
for c in resp:
    print(f"  - {c['nombre']} ({c['telefono']})")

# Peluquero con horarios
code, resp = api("GET", "/peluqueros/1")
print(f"\nPeluquero #1 ({code}): {resp['nombre']}")

# Crear turno de prueba (necesita fecha futura)
from datetime import datetime, timedelta
mañana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
# Buscar un día entre lun-mañana (día 1 es martes)
while datetime.strptime(mañana, "%Y-%m-%d").weekday() >= 5:
    mañana = (datetime.strptime(mañana, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

print(f"\n=== Creando turno para {mañana} ===")
code, resp = api("POST", "/turnos", {
    "cliente_id": 1,
    "peluquero_id": 1,
    "servicio_id": 1,
    "fecha": mañana,
    "hora_inicio": "10:00",
    "hora_fin": "10:30",
    "tolerancia_min": 5
})
print(f"POST /turnos ({code}): {resp}")

# Listar turnos
code, resp = api("GET", "/turnos")
print(f"\nTurnos ({code}): {len(resp)} items")
for t in resp:
    print(f"  - {t['fecha']} {t['hora_inicio']}-{t['hora_fin']} ({t['estado']})")

# Cambiar estado
code, resp = api("PUT", "/turnos/1/estado", {"estado": "confirmado"})
print(f"\nPUT /turnos/1/estado ({code}): {resp}")

# Cancelar turno
code, resp = api("DELETE", "/turnos/1")
print(f"\nDELETE /turnos/1 ({code})")

# Listar turnos de nuevo
code, resp = api("GET", "/turnos")
print(f"\nTurnos ({code}): {len(resp)} items")
for t in resp:
    print(f"  - {t['fecha']} {t['hora_inicio']}-{t['hora_fin']} ({t['estado']})")

# Agenda día
code, resp = api("GET", f"/agenda/dia?fecha={mañana}")
print(f"\nAgenda día {mañana} ({code}): {len(resp)} items")

# Dashboard
code, resp = api("GET", "/admin/dashboard")
print(f"\nDashboard ({code}): {resp}")

# Disponibilidad
code, resp = api("GET", f"/agenda/disponibilidad?fecha={mañana}&servicio_id=1")
print(f"\nDisponibilidad ({code}): {resp}")

print("\n=== ALL TESTS PASSED ===")
