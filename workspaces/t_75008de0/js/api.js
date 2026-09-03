/* =============================================
   API CLIENT — TurnosPro
   Consume endpoints REST de FastAPI (jose).
   Si el backend no responde, usa datos demo.
   ============================================= */

const API_BASE = 'http://localhost:8080';
const API_KEY_STORAGE = 'turnospro_token';

// Estado de conexión
let backendDisponible = null;

const api = {
    /* === CONFIGURACIÓN === */
    baseURL: API_BASE,

    getToken() {
        return localStorage.getItem(API_KEY_STORAGE);
    },

    setToken(token) {
        localStorage.setItem(API_KEY_STORAGE, token);
    },

    clearToken() {
        localStorage.removeItem(API_KEY_STORAGE);
    },

    /* === FETCH WRAPPER === */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            backendDisponible = true;

            if (response.status === 401) {
                this.clearToken();
                throw new Error('Sesión expirada. Inicie sesión nuevamente.');
            }

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Error ${response.status}`);
            }

            if (response.status === 204) return null;
            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                backendDisponible = false;
                throw new Error('BACKEND_UNAVAILABLE');
            }
            throw error;
        }
    },

    /* === MÉTODOS HTTP === */
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    /* === ENDPOINTS DE NEGOCIO === */

    // Auth
    login(username, password) {
        return this.post('/auth/login', { username, password });
    },

    // Peluqueros
    listarPeluqueros() {
        return this.get('/peluqueros');
    },

    // Servicios
    listarServicios() {
        return this.get('/servicios');
    },

    // Clientes
    listarClientes(busqueda = '') {
        const q = busqueda ? `?q=${encodeURIComponent(busqueda)}` : '';
        return this.get(`/clientes${q}`);
    },

    crearCliente(datos) {
        return this.post('/clientes', datos);
    },

    // Turnos
    listarTurnos(filtros = {}) {
        const params = new URLSearchParams();
        if (filtros.fecha) params.set('fecha', filtros.fecha);
        if (filtros.peluquero_id) params.set('peluquero_id', filtros.peluquero_id);
        if (filtros.cliente_id) params.set('cliente_id', filtros.cliente_id);
        const qs = params.toString() ? `?${params.toString()}` : '';
        return this.get(`/turnos${qs}`);
    },

    crearTurno(datos) {
        return this.post('/turnos', datos);
    },

    actualizarEstadoTurno(turnoId, estado) {
        return this.put(`/turnos/${turnoId}/estado`, { estado });
    },

    cancelarTurno(turnoId) {
        return this.delete(`/turnos/${turnoId}`);
    },

    // Agenda
    agendaDia(fecha) {
        return this.get(`/agenda/dia?fecha=${fecha}`);
    },

    agendaSemana(fecha) {
        return this.get(`/agenda/semana?fecha=${fecha}`);
    },

    disponibilidad(fecha, servicioId) {
        return this.get(`/agenda/disponibilidad?fecha=${fecha}&servicio_id=${servicioId}`);
    },

    // Dashboard
    dashboardDia(fecha) {
        return this.get(`/admin/dashboard?fecha=${fecha}`);
    },

    // Exportar
    exportarCSV(fecha) {
        return this.get(`/admin/export/dia?fecha=${fecha}&format=csv`);
    },
};

/* =============================================
   DATOS DEMO — Se usan cuando backend cae
   ============================================= */

const DEMO_DATA = {
    peluqueros: [
        { id: 1, nombre: 'Juana Martínez', activo: true },
        { id: 2, nombre: 'María López', activo: true },
        { id: 3, nombre: 'Carlos García', activo: true },
    ],
    servicios: [
        { id: 1, nombre: 'Corte', duracion_min: 30, precio: 1500, activo: true },
        { id: 2, nombre: 'Coloración', duracion_min: 60, precio: 3500, activo: true },
        { id: 3, nombre: 'Peinado', duracion_min: 45, precio: 2500, activo: true },
        { id: 4, nombre: 'Tratamiento capilar', duracion_min: 30, precio: 2000, activo: true },
    ],
    clientes: [
        { id: 1, nombre: 'María González', telefono: '3333-3333', activo: true },
        { id: 2, nombre: 'Carlos Rodríguez', telefono: '4444-4444', activo: true },
        { id: 3, nombre: 'Laura Pérez', telefono: '5555-5555', activo: true },
        { id: 4, nombre: 'Pedro Sánchez', telefono: '6666-6666', activo: true },
        { id: 5, nombre: 'Ana Martínez', telefono: '7777-7777', activo: true },
    ],
    turnos: [],
};

// Generar turnos demo para los próximos 7 días
function generarTurnosDemo() {
    const hoy = new Date();
    const estados = ['pendiente', 'confirmado', 'en_curso', 'completado'];
    const turnos = [];

    for (let d = 0; d < 7; d++) {
        const fecha = new Date(hoy);
        fecha.setDate(fecha.getDate() + d);
        const fechaStr = fecha.toISOString().split('T')[0];

        const numTurnos = Math.floor(Math.random() * 4) + 2;
        const horas = [9, 10, 11, 14, 15, 16];

        for (let i = 0; i < numTurnos; i++) {
            const hora = horas[Math.floor(Math.random() * horas.length)];
            const servicio = DEMO_DATA.servicios[Math.floor(Math.random() * DEMO_DATA.servicios.length)];
            const cliente = DEMO_DATA.clientes[Math.floor(Math.random() * DEMO_DATA.clientes.length)];
            const peluquero = DEMO_DATA.peluqueros[Math.floor(Math.random() * DEMO_DATA.peluqueros.length)];

            turnos.push({
                id: turnos.length + 1,
                cliente_id: cliente.id,
                cliente_nombre: cliente.nombre,
                servicio_id: servicio.id,
                servicio_nombre: servicio.nombre,
                servicio_duracion: servicio.duracion_min,
                peluquero_id: peluquero.id,
                peluquero_nombre: peluquero.nombre,
                fecha: fechaStr,
                hora_inicio: `${hora.toString().padStart(2, '0')}:00`,
                hora_fin: `${(hora + Math.ceil(servicio.duracion_min / 60)).toString().padStart(2, '0')}:00`,
                estado: d === 0 ? estados[Math.floor(Math.random() * 3)] : estados[Math.floor(Math.random() * 2) + 1],
                tolerancia_min: 5,
            });
        }
    }
    return turnos.sort((a, b) => `${a.fecha} ${a.hora_inicio}`.localeCompare(`${b.fecha} ${b.hora_inicio}`));
}

DEMO_DATA.turnos = generarTurnosDemo();

/* === FUNCIONES HELPER DEMO === */
const demoMode = {
    listarPeluqueros() {
        return [...DEMO_DATA.peluqueros];
    },

    listarServicios() {
        return [...DEMO_DATA.servicios];
    },

    listarClientes(busqueda = '') {
        if (!busqueda) return [...DEMO_DATA.clientes];
        const q = busqueda.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        return DEMO_DATA.clientes.filter(c =>
            c.nombre.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').includes(q) ||
            c.telefono.includes(q)
        );
    },

    crearCliente(datos) {
        const nuevo = {
            id: DEMO_DATA.clientes.length + 1,
            nombre: datos.nombre,
            telefono: datos.telefono || '',
            email: datos.email || '',
            activo: true,
        };
        DEMO_DATA.clientes.push(nuevo);
        return nuevo;
    },

    listarTurnos(filtros = {}) {
        let turnos = [...DEMO_DATA.turnos];
        if (filtros.fecha) {
            turnos = turnos.filter(t => t.fecha === filtros.fecha);
        }
        if (filtros.peluquero_id) {
            turnos = turnos.filter(t => t.peluquero_id === filtros.peluquero_id);
        }
        return turnos;
    },

    crearTurno(datos) {
        const servicio = DEMO_DATA.servicios.find(s => s.id === datos.servicio_id);
        const cliente = DEMO_DATA.clientes.find(c => c.id === datos.cliente_id);
        const peluquero = DEMO_DATA.peluqueros.find(p => p.id === datos.peluquero_id) || DEMO_DATA.peluqueros[0];

        const [hora, min] = datos.hora_inicio.split(':').map(Number);
        const duracion = servicio?.duracion_min || 30;
        const horaFinNum = hora * 60 + min + duracion;
        const horaFin = `${Math.floor(horaFinNum / 60).toString().padStart(2, '0')}:${(horaFinNum % 60).toString().padStart(2, '0')}`;

        const nuevo = {
            id: DEMO_DATA.turnos.length + 1,
            cliente_id: datos.cliente_id,
            cliente_nombre: cliente?.nombre || 'Desconocido',
            servicio_id: datos.servicio_id,
            servicio_nombre: servicio?.nombre || 'Servicio',
            servicio_duracion: duracion,
            peluquero_id: peluquero.id,
            peluquero_nombre: peluquero.nombre,
            fecha: datos.fecha,
            hora_inicio: datos.hora_inicio,
            hora_fin: horaFin,
            estado: 'pendiente',
            tolerancia_min: 5,
        };

        DEMO_DATA.turnos.push(nuevo);
        return nuevo;
    },

    cancelarTurno(turnoId) {
        const idx = DEMO_DATA.turnos.findIndex(t => t.id === turnoId);
        if (idx >= 0) DEMO_DATA.turnos[idx].estado = 'cancelado';
        return true;
    },

    disponibilidad(fecha, servicioId) {
        const servicio = DEMO_DATA.servicios.find(s => s.id === servicioId);
        const duracion = servicio?.duracion_min || 30;
        const ocupados = DEMO_DATA.turnos
            .filter(t => t.fecha === fecha && t.estado !== 'cancelado')
            .map(t => ({ inicio: t.hora_inicio, fin: t.hora_fin }));

        const slots = [];
        for (let h = 8; h <= 18; h++) {
            for (let m = 0; m < 60; m += 30) {
                const inicio = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
                const finMin = h * 60 + m + duracion;
                const fin = `${Math.floor(finMin / 60).toString().padStart(2, '0')}:${(finMin % 60).toString().padStart(2, '0')}`;

                const ocupado = ocupados.some(o => inicio < o.fin && fin > o.inicio);
                if (!ocupado) {
                    slots.push(inicio);
                }
            }
        }
        return { fecha, servicio_id: servicioId, duracion_min: duracion, horarios: slots };
    },

    dashboardDia(fecha) {
        const turnos = this.listarTurnos({ fecha });
        return {
            fecha,
            total: turnos.length,
            pendientes: turnos.filter(t => t.estado === 'pendiente').length,
            confirmados: turnos.filter(t => t.estado === 'confirmado').length,
            en_curso: turnos.filter(t => t.estado === 'en_curso').length,
            completados: turnos.filter(t => t.estado === 'completado').length,
            cancelados: turnos.filter(t => t.estado === 'cancelado').length,
        };
    },
};
