// Cargar órdenes al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarOrdenes();
});

function cargarOrdenes() {
    fetch('/api/ordenes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaOrdenes = document.getElementById("tablaOrdenes");
                tablaOrdenes.innerHTML = "";
                
                if (data.ordenes.length === 0) {
                    tablaOrdenes.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">No hay órdenes pendientes</td>
                        </tr>
                    `;
                    return;
                }

                data.ordenes.forEach(orden => {
                    const vendedor = orden.vendedor || 'No disponible';
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

                    console.log("Fecha API:", orden.fecha_hora, "→ Convertida:", fechaFormateada);

                    // Determinar la clase CSS para el estado
                    let estadoClase = {
                        'Pendiente': 'Pendiente',
                        'En proceso': 'EnProceso',
                        'Completado': 'Completada',
                        'Cancelado': 'Cancelada'
                    }[orden.estado] || '';

                    // Determinar qué botones mostrar según el estado
                    let botonesHTML = `<button class="btnVerOrden" onclick="verDetallesOrden(${orden.id})">👁️ Ver</button>`;

                    if (orden.estado === 'Pendiente') {
                        botonesHTML += `<button class="btnProcesarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'En proceso')">⏳ Procesando</button>`;
                        botonesHTML += `<button class="btnCancelarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Cancelado')">❌ Cancelar</button>`;
                    } else if (orden.estado === 'En proceso') {
                        botonesHTML += `<button class="btnListaOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Completado')">✔️ Lista</button>`;
                        botonesHTML += `<button class="btnCancelarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Cancelado')">❌ Cancelar</button>`;
                    }


                    // Crear la fila de la tabla con la nueva columna
                    let fila = `
                        <tr data-id="${orden.id}" data-cliente="${orden.cliente}" data-fecha="${fechaFormateada}" data-total="${orden.total}" data-mesa="${orden.numero_mesa || ''}" data-vendedor="${vendedor}">
                            <td>${orden.cliente}</td>
                            <td>${fechaFormateada}</td>
                            <td>${vendedor}</td> <!-- Nueva columna -->
                            <td><span class="estadoOrden ${estadoClase}">${orden.estado}</span></td>
                            <td>${botonesHTML}</td>
                        </tr>
                    `;
                    tablaOrdenes.innerHTML += fila;
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
                
                let detallesHTML = `
                    <div class="infoOrden">
                        <div class="orden-header">
                            <div class="orden-id">
                                <span class="orden-label">Orden #</span>
                                <span class="orden-value">${id}</span>
                            </div>
                            <div class="orden-estado">
                                <span class="estado-badge">Activa</span>
                            </div>
                        </div>
                        <div class="orden-cliente-info">
                            <div class="info-grupo">
                                <span class="info-label">Cliente:</span>
                                <span class="info-value">${cliente}</span>
                            </div>
                            <div class="info-grupo">
                                <span class="info-label">Vendedor:</span>
                                <span class="info-value">${vendedor}</span>
                            </div>
                            <div class="info-grupo">
                                <span class="info-label">Fecha:</span>
                                <span class="info-value">${fecha}</span>
                            </div>
                            ${mesa ? `<div class="info-grupo"><span class="info-label">Mesa:</span><span class="info-value">${mesa}</span></div>` : ''}
                        </div>
                    </div>
                    <div class="productosOrden">
                        <h4 class="productos-titulo">Detalle de Productos</h4>
                        <div class="tabla-responsive">
                            <table class="tabla-productos">
                                <thead>
                                    <tr>
                                        <th>Producto</th>
                                        <th>Tamaño</th>
                                        <th>Precio Unit.</th>
                                        <th>Cant.</th>
                                        <th>Subtotal</th>
                                    </tr>
                                </thead>
                                <tbody>`;

                let subtotal = 0;
                data.detalles.forEach(detalle => {
                    const precioFormateado = parseFloat(detalle.precio).toFixed(2);
                    const subtotalItem = parseFloat(detalle.subtotal).toFixed(2);
                    subtotal += parseFloat(subtotalItem);
                    const tamano = detalle.tamano || 'No aplica';
                    
                    detallesHTML += `
                        <tr>
                            <td class="producto-nombre">${detalle.nombre_producto}</td>
                            <td class="producto-tamano">${tamano}</td>
                            <td class="precio-unitario">$${precioFormateado}</td>
                            <td class="cantidad-producto">${detalle.cantidad}</td>
                            <td class="subtotal-producto">$${subtotalItem}</td>
                        </tr>`;
                });

                detallesHTML += `
                                </tbody>
                                <tfoot>
                                    <tr class="total-row">
                                        <td colspan="4" class="total-label">Total</td>
                                        <td class="total-value">$${parseFloat(total).toFixed(2)}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>`;
                
                document.getElementById('detallesOrden').innerHTML = detallesHTML;
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
    document.getElementById('confirmacionModal').style.display = 'flex'; // Mostrar el modal de confirmación
}

function confirmarCambioEstado() {
    fetch(`/api/ordenes/${idOrdenAActualizar}/estado`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ estado: nuevoEstadoAActualizar })
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

function buscarVentas() {
    const busqueda = document.getElementById('buscarCliente').value.toLowerCase();
    document.querySelectorAll('#tablaOrdenes tr').forEach(fila => {
        fila.style.display = fila.querySelector('td:first-child').textContent.toLowerCase().includes(busqueda) ? '' : 'none';
    });
}

function reestablecerFiltros() {
    document.getElementById('buscarCliente').value = '';
    cargarOrdenes();
}

function mostrarAlerta(mensaje, tipo = 'ExitoG') {
    const contenedor = document.querySelector('.contenedorAlertas') || crearContenedorAlertas();

    const alerta = document.createElement('div');
    alerta.className = `alertaGeneral alerta-${tipo}`;

    // Configurar icono y título según el tipo de alerta
    let icono, titulo;
    if (tipo === 'ErrorG') {
        icono = '⚠️';
        titulo = '¡Atención!';
    } else {
        icono = '✅';
        titulo = '¡Éxito!';
    }

    alerta.innerHTML = `
        <span class="iconoAlertaG">${icono}</span>
        <div class="mensajeAlertaG">
            <h3>${titulo}</h3>
            <p>${mensaje}</p>
        </div>
        <button class="cerrarAlertaG" onclick="this.parentElement.remove()">×</button>
    `;

    contenedor.appendChild(alerta);

    // Aumentar el tiempo de espera a 10 segundos
    setTimeout(() => alerta.remove(), 3000); // Eliminar después de 10s
}


function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
}
