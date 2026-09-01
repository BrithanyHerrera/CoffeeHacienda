

// Cargar órdenes al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    cargarOrdenes();
});

function cargarOrdenes() {
    fetch('/api/ordenes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaOrdenes = document.getElementById("tablaOrdenes");
                tablaOrdenes.replaceChildren();

                if (data.ordenes.length === 0) {
                    const filaVacia = document.createElement('tr');
                    const celdaVacia = document.createElement('td');
                    celdaVacia.colSpan = 4; celdaVacia.className = 'text-center';
                    celdaVacia.textContent = 'No hay órdenes pendientes'; filaVacia.append(celdaVacia);
                    tablaOrdenes.append(filaVacia);
                    return;
                }

                data.ordenes.forEach(orden => {
                    const ordenId = Number.parseInt(orden.id, 10);
                    if (!Number.isInteger(ordenId) || ordenId <= 0) {
                        return;
                    }
                    const vendedor = orden.vendedor || 'No disponible';
                    const cliente = orden.cliente || 'No disponible';
                    const mesa = orden.numero_mesa || '';
                    const metodoPago = orden.metodo_pago || 'No especificado';
                    const estado = orden.estado || '';
                    // Convertir la fecha correctamente a la zona horaria local
                    const fechaUTC = new Date(orden.fecha_hora);
                    const fechaLocal = new Date(fechaUTC.getTime() + fechaUTC.getTimezoneOffset() * 60000);

                    // Formatear fecha y hora en formato 24 horas
                    const dia = fechaLocal.getDate().toString().padStart(2, '0');
                    const mes = (fechaLocal.getMonth() + 1).toString().padStart(2, '0');
                    const anio = fechaLocal.getFullYear();
                    const horas = fechaLocal.getHours().toString().padStart(2, '0');
                    const minutos = fechaLocal.getMinutes().toString().padStart(2, '0');
                    const segundos = fechaLocal.getSeconds().toString().padStart(2, '0');

                    const fechaFormateada = `${dia}/${mes}/${anio} ${horas}:${minutos}:${segundos}`;

                    // Determinar la clase CSS para el estado
                    let estadoClase = {
                        'Pendiente': 'Pendiente',
                        'En proceso': 'EnProceso',
                        'Completado': 'Completada',
                        'Cancelado': 'Cancelada'
                    }[orden.estado] || '';

                    // Determinar qué botones mostrar según el estado
                    const fila = document.createElement('tr');
                    fila.dataset.id = ordenId; fila.dataset.cliente = cliente; fila.dataset.fecha = fechaFormateada;
                    fila.dataset.total = Number(orden.total) || 0; fila.dataset.mesa = mesa; fila.dataset.vendedor = vendedor;
                    fila.dataset.metodo = metodoPago; fila.dataset.dinero = Number(orden.dinero_recibido) || 0; fila.dataset.cambio = Number(orden.cambio) || 0;
                    [cliente, fechaFormateada, vendedor].forEach(valor => { const celda = document.createElement('td'); celda.textContent = valor; fila.append(celda); });
                    const estadoCelda = document.createElement('td'); const estadoSpan = document.createElement('span'); estadoSpan.className = `estadoOrden ${estadoClase}`; estadoSpan.textContent = estado; estadoCelda.append(estadoSpan); fila.append(estadoCelda);
                    const acciones = document.createElement('td');
                    const agregarAccion = (clase, texto, estadoNuevo) => { const boton = document.createElement('button'); boton.className = clase; boton.type = 'button'; boton.textContent = texto; boton.addEventListener('click', () => cambiarEstadoOrden(ordenId, estadoNuevo)); acciones.append(boton); };
                    const ver = document.createElement('button'); ver.className = 'btnVerOrden'; ver.type = 'button'; ver.textContent = '👁️'; ver.addEventListener('click', () => verDetallesOrden(ordenId)); acciones.append(ver);
                    if (orden.estado === 'Pendiente') { agregarAccion('btnProcesarOrden', 'Procesando', 'En proceso'); agregarAccion('btnCancelarOrden', 'Cancelar', 'Cancelado'); }
                    else if (orden.estado === 'En proceso') { agregarAccion('btnListaOrden', 'Lista', 'Completado'); agregarAccion('btnCancelarOrden', 'Cancelar', 'Cancelado'); }
                    fila.append(acciones); tablaOrdenes.append(fila);
                });
            } else {
                console.error('Error al cargar órdenes:', data.message, 'ErrorG');
            }
        })
        .catch(error => console.error('Error en la solicitud:', error, 'ErrorG'));
}


function verDetallesOrden(id) {
    fetch(`/api/ordenes/${id}/detalles`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const fila = document.querySelector(`tr[data-id="${id}"]`);
                const cliente = fila.getAttribute('data-cliente');
                const fecha = fila.getAttribute('data-fecha');
                const vendedor = fila.getAttribute('data-vendedor') || 'No disponible';
                const total = fila.getAttribute('data-total');
                const mesa = fila.getAttribute('data-mesa');
                const metodoPago = fila.getAttribute('data-metodo') || 'No especificado';
                const dineroRecibido = parseFloat(fila.getAttribute('data-dinero') || 0);
                const cambioOrden = parseFloat(fila.getAttribute('data-cambio') || 0);

                const e = (tag, clase, texto) => { const n = document.createElement(tag); if (clase) n.className = clase; if (texto !== undefined) n.textContent = texto; return n; };
                const contenido = document.getElementById('detallesOrden'); contenido.replaceChildren();
                const infoOrden = e('div', 'infoOrden'); const cab = e('div', 'orden-header'); const oid = e('div', 'orden-id'); oid.append(e('span', 'orden-label', 'Orden #'), e('span', 'orden-value', id)); const est = e('div', 'orden-estado'); est.append(e('span', 'estado-badge', 'Activa')); cab.append(oid, est); infoOrden.append(cab);
                const clienteInfo = e('div', 'orden-cliente-info'); [['Cliente:', cliente], ['Vendedor:', vendedor], ['Fecha:', fecha], ['Método de pago:', metodoPago], ['Dinero recibido:', `$${dineroRecibido.toFixed(2)}`], ['Cambio:', `$${cambioOrden.toFixed(2)}`]].concat(mesa ? [['Mesa:', mesa]] : []).forEach(([label, value]) => { const grupo = e('div', 'info-grupo'); grupo.append(e('span', 'info-label', label), e('span', 'info-value', value)); clienteInfo.append(grupo); }); infoOrden.append(clienteInfo); contenido.append(infoOrden);
                const productos = e('div', 'productosOrden'); productos.append(e('h4', 'productos-titulo', 'Detalle de Productos')); const responsive = e('div', 'tabla-responsive'); const tabla = e('table', 'tabla-productos'); const head = e('tr'); ['Producto', 'Tamaño', 'Precio Unit.', 'Cant.', 'Subtotal'].forEach(t => head.append(e('th', null, t))); const thead = e('thead'); thead.append(head); tabla.append(thead); const tbody = e('tbody');
                data.detalles.forEach(detalle => { let precio = parseFloat(detalle.precio); if (isNaN(precio) && detalle.subtotal && detalle.cantidad) precio = parseFloat(detalle.subtotal) / parseInt(detalle.cantidad); const row = e('tr'); [detalle.nombre_producto, detalle.tamano || 'No aplica', `$${isNaN(precio) ? '0.00' : precio.toFixed(2)}`, detalle.cantidad, `$${parseFloat(detalle.subtotal || 0).toFixed(2)}`].forEach(v => row.append(e('td', null, v))); tbody.append(row); }); tabla.append(tbody); const foot = e('tfoot'); const totalRow = e('tr', 'total-row'); const totalLabel = e('td', 'total-label', 'Total'); totalLabel.colSpan = 4; totalRow.append(totalLabel, e('td', 'total-value', `$${parseFloat(total).toFixed(2)}`)); foot.append(totalRow); tabla.append(foot); responsive.append(tabla); productos.append(responsive); contenido.append(productos);
                document.getElementById('ordenModal').style.display = 'flex';
            } else {
                alert('Error al cargar detalles: ' + data.message, 'ErrorG');
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error, 'ErrorG');
        });
}

function cerrarDetallesOrden() {
    document.getElementById('ordenModal').style.display = 'none';
}

let idOrdenAActualizar = null; // Variable global para almacenar el ID de la orden a actualizar
let nuevoEstadoAActualizar = null; // Variable global para almacenar el nuevo estado

function cambiarEstadoOrden(id, nuevoEstado) {
    idOrdenAActualizar = id; // Almacenar el ID de la orden a actualizar
    nuevoEstadoAActualizar = nuevoEstado; // Almacenar el nuevo estado
    document.getElementById('mensajeConfirmacion').textContent = `¿Estás seguro de cambiar esta orden a estado "${nuevoEstado}"?`;
    const contenedorMotivo = document.getElementById('contenedorMotivoCancelacion');
    const motivo = document.getElementById('motivoCancelacion');
    const requiereMotivo = nuevoEstado === 'Cancelado';
    contenedorMotivo.style.display = requiereMotivo ? 'block' : 'none';
    motivo.value = '';
    document.getElementById('confirmacionModal').style.display = 'flex'; // Mostrar el modal de confirmación
}

function confirmarCambioEstado() {
    const motivo = document.getElementById('motivoCancelacion').value.trim();
    if (nuevoEstadoAActualizar === 'Cancelado' && motivo.length < 3) {
        mostrarAlerta('Indica un motivo de cancelación.', 'ErrorG');
        return;
    }

    fetch(`/api/ordenes/${idOrdenAActualizar}/estado`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            estado: nuevoEstadoAActualizar,
            motivo: nuevoEstadoAActualizar === 'Cancelado' ? motivo : null
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarAlerta(data.message); // Mostrar mensaje de éxito
                cargarOrdenes(); // Recargar las órdenes
            } else {
                mostrarAlerta('Error: ' + data.message, 'ErrorG'); // Mostrar mensaje de error
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error, 'ErrorG');
            mostrarAlerta('Error en la solicitud: ' + error, 'ErrorG'); // Mostrar mensaje de error
        });

    cerrarConfirmacionModal(); // Cerrar el modal de confirmación
}

function cerrarConfirmacionModal() {
    document.getElementById('confirmacionModal').style.display = 'none'; // Ocultar el modal de confirmación
}

function filtrarOrdenes() {
    const busquedaCliente = document.getElementById('buscarCliente').value.toLowerCase();
    const vendedorSeleccionado = document.getElementById('filtroVendedor').value.toLowerCase();
    
    document.querySelectorAll('#tablaOrdenes tr').forEach(fila => {
        const cliente = fila.querySelector('td:first-child').textContent.toLowerCase();
        const vendedor = fila.querySelector('td:nth-child(3)').textContent.toLowerCase();
        
        const coincideCliente = !busquedaCliente || cliente.includes(busquedaCliente);
        const coincideVendedor = !vendedorSeleccionado || vendedor === vendedorSeleccionado;
        
        fila.style.display = (coincideCliente && coincideVendedor) ? '' : 'none';
    });
}

function reestablecerFiltros() {
    document.getElementById('buscarCliente').value = '';
    document.getElementById('filtroVendedor').value = '';
    cargarOrdenes();
}





