/* =============================================
   APP.JS — TurnosPro Frontend
   SPA vanilla con vistas, navegación y API client
   ============================================= */

/* === ESTADO GLOBAL === */
const estado = {
    vistaActual: 'agenda',
    tipoVistaCalendario: 'mes',
    fechaActual: new Date(),
    filtros: {
        peluquero: 'todos',
    },
    formulario: {
        paso: 1,
        cliente: null,
        servicio: null,
        peluquero: 'cualquiera',
        fecha: null,
        horario: null,
    },
    cache: {
        peluqueros: [],
        servicios: [],
        turnos: [],
    },
};

/* === INICIALIZACIÓN === */
document.addEventListener('DOMContentLoaded', () => {
    inicializarApp();
});

async function inicializarApp() {
    cargarEventos();
    await Promise.all([cargarDatosIniciales(), cargarTurnosIniciales()]);
    renderizarCalendario();
    actualizarNavLinks();
}

/* === CARGA DE DATOS === */
function cargarTurnosIniciales() {
    return api.listarTurnos().then(turnos => {
        estado.cache.turnos = normalizarTurnos(turnos);
    }).catch(err => {
        estado.cache.turnos = demoMode.listarTurnos();
    });
}

async function cargarDatosIniciales() {
    try {
        const peluqueros = await api.listarPeluqueros();
        estado.cache.peluqueros = peluqueros.map(p => ({
            ...p,
            nombre: p.nombre || p.name,
        }));
    } catch (err) {
        estado.cache.peluqueros = demoMode.listarPeluqueros();
        if (err.message === 'BACKEND_UNAVAILABLE') {
            mostrarToast('⚠️ Modo offline: datos de demo', 'warning');
        }
    }

    try {
        const servicios = await api.listarServicios();
        estado.cache.servicios = normalizarServicios(servicios);
    } catch (err) {
        estado.cache.servicios = demoMode.listarServicios();
    }

    renderizarFiltrosPeluquero();
}

function normalizarServicios(servicios) {
    return servicios.map(s => ({
        ...s,
        duracion_min: s.duracion_min || s.duration_min || 30,
    }));
}

function normalizarTurnos(turnos) {
    return turnos.map(t => ({
        ...t,
        cliente_nombre: t.cliente_nombre || t.nombre_cliente || `${t.cliente_id}`,
        servicio_nombre: t.servicio_nombre || t.nombre_servicio || `${t.servicio_id}`,
        peluquero_nombre: t.peluquero_nombre || t.nombre_peluquero || `${t.peluquero_id}`,
        servicio_duracion: t.servicio_duracion || t.duracion_min || 30,
    }));
}

/* === NAVEGACIÓN === */
function navegarA(vista) {
    estado.vistaActual = vista;

    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    document.getElementById(`view-${vista}`).classList.add('active');

    actualizarNavLinks();

    if (vista === 'formulario') {
        setTimeout(() => {
            estado.formulario = {
                paso: 1,
                cliente: null,
                servicio: null,
                peluquero: 'cualquiera',
                fecha: null,
                horario: null,
            };
            actualizarFormulario();
        }, 50);
    }

    if (vista === 'admin') {
        cargarDashboardAdmin();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function actualizarNavLinks() {
    document.querySelectorAll('.nav-link, .mobile-nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.view === estado.vistaActual);
    });
}

function toggleMenu() {
    const links = document.querySelector('.navbar-links');
    links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
}

/* === CALENDARIO === */
function renderizarCalendario() {
    if (estado.tipoVistaCalendario === 'mes') {
        renderizarMes();
    } else {
        renderizarSemana();
    }
}

function renderizarMes() {
    const grid = document.getElementById('cal-dias');
    const titulo = document.getElementById('agenda-titulo');

    const año = estado.fechaActual.getFullYear();
    const mes = estado.fechaActual.getMonth();

    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    titulo.textContent = `${meses[mes]} ${año}`;

    const primerDia = new Date(año, mes, 1).getDay();
    const diasEnMes = new Date(año, mes + 1, 0).getDate();
    const diasMesAnterior = new Date(año, mes, 0).getDate();

    let html = '';

    for (let i = primerDia - 1; i >= 0; i--) {
        const dia = diasMesAnterior - i;
        html += `<div class="cal-day other-month"><div class="day-number">${dia}</div></div>`;
    }

    const hoy = new Date();
    for (let dia = 1; dia <= diasEnMes; dia++) {
        const fecha = `${año}-${(mes + 1).toString().padStart(2, '0')}-${dia.toString().padStart(2, '0')}`;
        const esHoy = hoy.getDate() === dia && hoy.getMonth() === mes && hoy.getFullYear() === año;
        const turnos = obtenerTurnosPorFecha(fecha);

        html += `<div class="cal-day${esHoy ? ' today' : ''}" onclick="seleccionarFecha('${fecha}')">`;
        html += `<div class="day-number">${dia}</div>`;

        if (window.innerWidth <= 480) {
            html += `<div class="day-dots">`;
            turnos.slice(0, 4).forEach(t => {
                html += `<span class="day-dot" style="background: var(--${t.estado.replace('_', '-')})"></span>`;
            });
            html += `</div>`;
        } else {
            html += `<div class="day-events">`;
            turnos.slice(0, 3).forEach(t => {
                html += `<div class="day-event event-${t.estado.replace('_', '-')}">${t.hora_inicio} ${t.cliente_nombre.split(' ')[0]}</div>`;
            });
            if (turnos.length > 3) {
                html += `<div class="day-more">+${turnos.length - 3} más</div>`;
            }
            html += `</div>`;
        }

        html += `</div>`;
    }

    const totalCeldas = 42;
    const celdasUsadas = primerDia + diasEnMes;
    const celdasRestantes = totalCeldas - celdasUsadas;

    for (let dia = 1; dia <= celdasRestantes; dia++) {
        html += `<div class="cal-day other-month"><div class="day-number">${dia}</div></div>`;
    }

    grid.innerHTML = html;
}

function renderizarSemana() {
    const grid = document.getElementById('semana-grid');
    const titulo = document.getElementById('agenda-titulo');

    const año = estado.fechaActual.getFullYear();
    const mes = estado.fechaActual.getMonth();
    const dia = estado.fechaActual.getDate();

    const inicioSemana = new Date(año, mes, dia - new Date(año, mes, dia).getDay());
    const finSemana = new Date(inicioSemana);
    finSemana.setDate(finSemana.getDate() + 6);

    const formatear = d => `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}`;
    titulo.textContent = `${formatear(inicioSemana)} — ${formatear(finSemana)}`;

    const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    let html = `<div class="semana-header-empty"></div>`;
    for (let i = 0; i < 7; i++) {
        const fecha = new Date(inicioSemana);
        fecha.setDate(fecha.getDate() + i);
        const esHoy = fecha.getTime() === hoy.getTime();
        html += `<div class="semana-header${esHoy ? ' today' : ''}">${diasSemana[fecha.getDay()]}<br>${fecha.getDate()}</div>`;
    }

    for (let h = 8; h <= 18; h++) {
        html += `<div class="semana-hora">${h.toString().padStart(2, '0')}:00</div>`;

        for (let d = 0; d < 7; d++) {
            const fecha = new Date(inicioSemana);
            fecha.setDate(fecha.getDate() + d);
            const fechaStr = fecha.toISOString().split('T')[0];
            const hora = `${h.toString().padStart(2, '0')}:00`;
            const turnosHora = obtenerTurnosPorFechaYHora(fechaStr, hora);

            html += `<div class="semana-cell" onclick="seleccionarHorarioSemana('${fechaStr}', '${hora}')">`;
            turnosHora.forEach(t => {
                const border_color = `var(--${t.estado.replace('_', '-')})`;
                html += `<div class="semana-event" style="border-left-color: ${border_color}; background: var(--${t.estado.replace('_', '-')}-bg);">`;
                html += `<span class="semana-event-hora">${t.hora_inicio}</span> ${t.cliente_nombre} · ${t.servicio_nombre}`;
                html += `</div>`;
            });
            html += `</div>`;
        }
    }

    grid.innerHTML = html;
}

function cambiarFecha(direccion) {
    if (estado.tipoVistaCalendario === 'mes') {
        estado.fechaActual.setMonth(estado.fechaActual.getMonth() + direccion);
    } else {
        estado.fechaActual.setDate(estado.fechaActual.getDate() + (direccion * 7));
    }
    renderizarCalendario();
}

function cambiarVista(tipo) {
    estado.tipoVistaCalendario = tipo;

    document.querySelectorAll('.view-tab').forEach(el => {
        el.classList.toggle('active', el.dataset.vista === tipo);
    });

    document.getElementById('vista-mes').classList.toggle('active', tipo === 'mes');
    document.getElementById('vista-semana').classList.toggle('active', tipo === 'semana');

    renderizarCalendario();
}

function seleccionarFecha(fecha) {
    estado.formulario.fecha = fecha;
    navegarA('formulario');
}

function seleccionarHorarioSemana(fecha, hora) {
    estado.formulario.fecha = fecha;
    estado.formulario.horario = hora;
    navegarA('formulario');
}

function filtrarPeluquero(id) {
    estado.filtros.peluquero = id;
    document.querySelectorAll('#filtros-peluquero .chip, .view-filters .chip[data-filtro]').forEach(el => {
        el.classList.toggle('active', el.dataset.filtro === id);
    });
    renderizarCalendario();
    if (estado.vistaActual === 'admin') cargarDashboardAdmin();
}

function renderizarFiltrosPeluquero() {
    const cont = document.getElementById('filtros-peluquero');
    cont.innerHTML = '';
    estado.cache.peluqueros.forEach(p => {
        const chip = document.createElement('button');
        chip.className = 'chip';
        chip.dataset.filtro = p.id;
        chip.textContent = p.nombre;
        chip.onclick = () => filtrarPeluquero(p.id);
        cont.appendChild(chip);
    });
}

/* === TURNOS POR FECHA/HORA === */
function obtenerTurnosPorFecha(fecha) {
    let turnos = estado.cache.turnos.filter(t => t.fecha === fecha && t.estado !== 'cancelado');
    if (estado.filtros.peluquero !== 'todos') {
        turnos = turnos.filter(t => t.peluquero_id === estado.filtros.peluquero);
    }
    return turnos.sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
}

function obtenerTurnosPorFechaYHora(fecha, hora) {
    return estado.cache.turnos.filter(t => {
        if (t.fecha !== fecha || t.estado === 'cancelado') return false;
        if (estado.filtros.peluquero !== 'todos' && t.peluquero_id !== estado.filtros.peluquero) return false;
        const inicio = t.hora_inicio;
        const fin = t.hora_fin;
        return hora >= inicio && hora < fin;
    });
}

/* === FORMULARIO === */
async function buscarCliente(query) {
    const lista = document.getElementById('cliente-resultados');

    if (query.length < 2) {
        lista.classList.add('hidden');
        return;
    }

    let clientes = [];
    try {
        clientes = await api.listarClientes(query);
    } catch (err) {
        clientes = demoMode.listarClientes(query);
    }

    if (clientes.length === 0) {
        lista.innerHTML = `<div class="autocomplete-item" onclick="mostrarNuevoCliente()">
            <span class="ac-nombre">+ Crear nuevo cliente</span>
            <br><span class="ac-telefono">No se encontraron resultados</span>
        </div>`;
    } else {
        lista.innerHTML = clientes.map(c => `
            <div class="autocomplete-item" onclick="seleccionarCliente(${c.id}, '${c.nombre}')">
                <span class="ac-nombre">${c.nombre}</span>
                <br><span class="ac-telefono">${c.telefono}</span>
            </div>
        `).join('');
    }

    lista.classList.remove('hidden');
}

function seleccionarCliente(id, nombre) {
    estado.formulario.cliente = { id, nombre };
    document.getElementById('input-cliente').value = nombre;
    document.getElementById('cliente-resultados').classList.add('hidden');
}

function mostrarNuevoCliente() {
    const nombre = prompt('Nombre del nuevo cliente:');
    if (!nombre) return;

    const telefono = prompt('Teléfono (opcional):') || '';

    try {
        const cliente = demoMode.crearCliente({ nombre, telefono });
        seleccionarCliente(cliente.id, cliente.nombre);
        mostrarToast(`✓ Cliente "${cliente.nombre}" creado`, 'success');
    } catch (err) {
        mostrarToast('Error al crear cliente', 'error');
    }
}

function cargarServiciosFormulario() {
    const cont = document.getElementById('servicios-lista');
    cont.innerHTML = estado.cache.servicios.map(s => `
        <button class="chip ${estado.formulario.servicio?.id === s.id ? 'active' : ''}"
                onclick="seleccionarServicio(${s.id})">
            ${s.nombre} · ${s.duracion_min}m · $${s.precio}
        </button>
    `).join('');

    const contP = document.getElementById('peluqueros-lista');
    contP.innerHTML = `<button class="chip ${estado.formulario.peluquero === 'cualquiera' ? 'active' : ''}"
            onclick="seleccionarPeluquero('cualquiera')">Cualquiera</button>` +
        estado.cache.peluqueros.map(p => `
            <button class="chip ${estado.formulario.peluquero === p.id ? 'active' : ''}"
                    onclick="seleccionarPeluquero(${p.id})">${p.nombre}</button>
        `).join('');
}

function seleccionarServicio(id) {
    estado.formulario.servicio = estado.cache.servicios.find(s => s.id === id);
    cargarServiciosFormulario();
}

function seleccionarPeluquero(id) {
    estado.formulario.peluquero = id;
    cargarServiciosFormulario();
}

async function cargarDisponibilidad() {
    const fecha = document.getElementById('input-fecha').value;
    if (!fecha || !estado.formulario.servicio) return;

    estado.formulario.fecha = fecha;

    try {
        const data = await api.disponibilidad(fecha, estado.formulario.servicio.id);
        const horarios = Array.isArray(data) ? data.map(item => item.huecos || []).flat() : (data.horarios || []);
        renderizarHorarios(horarios);
    } catch (err) {
        const data = demoMode.disponibilidad(fecha, estado.formulario.servicio.id);
        renderizarHorarios(data.horarios);
    }
}

function renderizarHorarios(horarios) {
    const cont = document.getElementById('horarios-lista');
    if (horarios.length === 0) {
        cont.innerHTML = '<p class="form-hint">No hay horarios disponibles para esta fecha</p>';
        return;
    }

    cont.innerHTML = horarios.map(h => `
        <button class="chip ${estado.formulario.horario === h ? 'active' : ''}"
                onclick="seleccionarHorario('${h}')">${h}</button>
    `).join('');

    if (estado.formulario.horario && horarios.includes(estado.formulario.horario)) {
        seleccionarHorario(estado.formulario.horario);
    }
}

function seleccionarHorario(horario) {
    estado.formulario.horario = horario;

    const errorDiv = document.getElementById('error-solapamiento');
    const fecha = estado.formulario.fecha;
    const duracion = estado.formulario.servicio?.duracion_min || 30;
    const [h, m] = horario.split(':').map(Number);
    const fin = `${(h + Math.floor((m + duracion) / 60)).toString().padStart(2, '0')}:${((m + duracion) % 60).toString().padStart(2, '0')}`;

    const conflicto = estado.cache.turnos.find(t =>
        t.fecha === fecha &&
        t.estado !== 'cancelado' &&
        horario < t.hora_fin && fin > t.hora_inicio
    );

    if (conflicto) {
        errorDiv.textContent = `⚠ Este horario se superpone con el turno de ${conflicto.cliente_nombre} (${conflicto.hora_inicio}-${conflicto.hora_fin}).`;
        errorDiv.classList.remove('hidden');
        document.getElementById('btn-paso-siguiente').disabled = true;
    } else {
        errorDiv.classList.add('hidden');
        document.getElementById('btn-paso-siguiente').disabled = false;
    }

    document.querySelectorAll('#horarios-lista .chip').forEach(el => {
        el.classList.toggle('active', el.textContent.trim() === horario);
    });
}

function pasoAnterior() {
    if (estado.formulario.paso > 1) {
        estado.formulario.paso--;
        actualizarFormulario();
    }
}

function pasoSiguiente() {
    if (estado.formulario.paso === 1 && !estado.formulario.cliente) {
        mostrarToast('Seleccione un cliente', 'warning');
        return;
    }
    if (estado.formulario.paso === 2 && !estado.formulario.servicio) {
        mostrarToast('Seleccione un servicio', 'warning');
        return;
    }
    if (estado.formulario.paso === 3) {
        if (!estado.formulario.fecha || !estado.formulario.horario) {
            mostrarToast('Seleccione fecha y horario', 'warning');
            return;
        }
        crearTurno();
        return;
    }

    estado.formulario.paso++;
    actualizarFormulario();
}

function actualizarFormulario() {
    const paso = estado.formulario.paso;

    document.querySelectorAll('.progress-step').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.paso) <= paso);
    });

    document.querySelectorAll('.form-step').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.paso) === paso);
    });

    document.getElementById('btn-paso-anterior').style.display = paso > 1 ? 'inline-flex' : 'none';
    const btnSiguiente = document.getElementById('btn-paso-siguiente');
    btnSiguiente.textContent = paso === 3 ? '✓ Confirmar Turno' : 'Siguiente';
    btnSiguiente.className = paso === 3 ? 'btn btn-success' : 'btn btn-primary';

    if (paso === 2) cargarServiciosFormulario();
    if (paso === 3 && estado.formulario.fecha) {
        document.getElementById('input-fecha').value = estado.formulario.fecha;
        cargarDisponibilidad();
    }
}

async function crearTurno() {
    const datos = {
        cliente_id: estado.formulario.cliente.id,
        servicio_id: estado.formulario.servicio.id,
        peluquero_id: estado.formulario.peluquero === 'cualquiera' ? estado.cache.peluqueros[0].id : estado.formulario.peluquero,
        fecha: estado.formulario.fecha,
        hora_inicio: estado.formulario.horario,
        hora_fin: (() => {
            const [h, m] = estado.formulario.horario.split(':').map(Number);
            const mins = h * 60 + m + (estado.formulario.servicio?.duracion_min || 30);
            const hh = Math.floor(mins / 60).toString().padStart(2, '0');
            const mm = (mins % 60).toString().padStart(2, '0');
            return `${hh}:${mm}`;
        })(),
    };

    try {
        const turno = await api.crearTurno(datos);
        mostrarToast('✓ Turno creado exitosamente', 'success');
        estado.cache.turnos.push({
            ...turno,
            cliente_nombre: estado.formulario.cliente.nombre,
            servicio_nombre: estado.formulario.servicio.nombre,
        });
        navegarA('agenda');
    } catch (err) {
        if (err.message === 'BACKEND_UNAVAILABLE') {
            const turno = demoMode.crearTurno(datos);
            estado.cache.turnos.push({
                ...turno,
                cliente_nombre: estado.formulario.cliente.nombre,
                servicio_nombre: estado.formulario.servicio.nombre,
            });
            mostrarToast('✓ Turno creado (modo demo)', 'success');
            navegarA('agenda');
        } else {
            mostrarToast(err.message, 'error');
        }
    }
}

/* === ADMIN === */
async function cargarDashboardAdmin() {
    const hoy = new Date().toISOString().split('T')[0];

    try {
        const dashboard = await api.dashboardDia(hoy);
        actualizarStats(dashboard);
    } catch (err) {
        const dashboard = demoMode.dashboardDia(hoy);
        actualizarStats(dashboard);
    }

    cargarTablaTurnos(hoy);
}

function actualizarStats(dashboard) {
    document.getElementById('stat-total').textContent = dashboard.total;
    document.getElementById('stat-confirmados').textContent = dashboard.confirmados;
    document.getElementById('stat-pendientes').textContent = dashboard.pendientes;
    document.getElementById('stat-en-curso').textContent = dashboard.en_curso;
}

function cargarTablaTurnos(fecha) {
    const turnos = obtenerTurnosPorFecha(fecha);
    const tbody = document.getElementById('tabla-turnos');

    if (turnos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 32px; color: var(--gris);">No hay turnos para hoy</td></tr>`;
        return;
    }

    tbody.innerHTML = turnos.map(t => `
        <tr>
            <td><strong>${t.hora_inicio}</strong></td>
            <td>${t.cliente_nombre}</td>
            <td>${t.servicio_nombre}</td>
            <td>${t.peluquero_nombre}</td>
            <td><span class="badge badge-${t.estado.replace('_', '-')}">${formatearEstado(t.estado)}</span></td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="cambiarEstado(${t.id})" title="Cambiar estado">✎</button>
                <button class="btn btn-danger btn-sm" onclick="cancelarTurno(${t.id})" title="Cancelar">✕</button>
            </td>
        </tr>
    `).join('');
}

function formatearEstado(estado) {
    const map = {
        pendiente: 'Pendiente',
        confirmado: 'Confirmado',
        en_curso: 'En curso',
        completado: 'Completado',
        cancelado: 'Cancelado',
    };
    return map[estado] || estado;
}

async function cambiarEstado(turnoId) {
    const nuevo = prompt('Nuevo estado (pendiente/confirmado/en_curso/completado/cancelado):');
    if (!nuevo) return;

    try {
        await api.actualizarEstadoTurno(turnoId, nuevo);
        mostrarToast('Estado actualizado', 'success');
        estado.cache.turnos = estado.cache.turnos.map(t =>
            t.id === turnoId ? { ...t, estado: nuevo } : t
        );
        cargarTablaTurnos(new Date().toISOString().split('T')[0]);
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

async function cancelarTurno(turnoId) {
    const confirmacion = confirm('¿Seguro que desea cancelar este turno?');
    if (!confirmacion) return;

    try {
        await api.cancelarTurno(turnoId);
        mostrarToast('Turno cancelado', 'success');
        estado.cache.turnos = estado.cache.turnos.map(t =>
            t.id === turnoId ? { ...t, estado: 'cancelado' } : t
        );
        cargarTablaTurnos(new Date().toISOString().split('T')[0]);
    } catch (err) {
        mostrarToast(err.message, 'error');
    }
}

function filtrarTabla() {
    const query = document.getElementById('buscar-turno').value.toLowerCase();
    const filas = document.querySelectorAll('#tabla-turnos tr');

    filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        fila.style.display = texto.includes(query) ? '' : 'none';
    });
}

function exportarCSV() {
    const hoy = new Date().toISOString().split('T')[0];
    const turnos = obtenerTurnosPorFecha(hoy);

    const headers = ['Hora', 'Cliente', 'Servicio', 'Peluquero', 'Estado'];
    const filas = turnos.map(t => [t.hora_inicio, t.cliente_nombre, t.servicio_nombre, t.peluquero_nombre, t.estado]);

    const csv = [headers, ...filas].map(fila => fila.map(campo => `"${campo}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `turnos_${hoy}.csv`;
    a.click();
    URL.revokeObjectURL(url);

    mostrarToast('✓ CSV exportado', 'success');
}

/* === TOASTS === */
function mostrarToast(mensaje, tipo = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensaje;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

/* === MODAL === */
function cerrarModal(event) {
    if (event.target.id === 'modal-overlay') {
        document.getElementById('modal-overlay').classList.add('hidden');
    }
}

function mostrarModalHTML(html) {
    document.getElementById('modal-content').innerHTML = html;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

/* === EVENTOS === */
function cargarEventos() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.getElementById('modal-overlay').classList.add('hidden');
        }
    });

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (estado.vistaActual === 'agenda') {
                renderizarCalendario();
            }
        }, 250);
    });

    document.addEventListener('click', (e) => {
        const wrapper = e.target.closest('.input-wrapper');
        if (!wrapper) {
            document.querySelectorAll('.autocomplete-list').forEach(el => el.classList.add('hidden'));
        }
    });
}
