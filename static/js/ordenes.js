// Cargar órdenes al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarOrdenes();
});

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
                    // Formatear la fecha correctamente con la zona horaria
                    const fecha = new Date(orden.fecha_hora);
                    fecha.setMinutes(fecha.getMinutes() - fecha.getTimezoneOffset());
                    const opcionesFecha = { year: 'numeric', month: '2-digit', day: '2-digit' };
                    const opcionesHora = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
                    const fechaFormateada = fecha.toLocaleDateString('es-ES', opcionesFecha) + ' ' + fecha.toLocaleTimeString('es-ES', opcionesHora);
                    
                    // Determinar la clase CSS para el estado
                    let estadoClase = '';
                    if (orden.estado === 'Pendiente') estadoClase = 'Pendiente';
                    else if (orden.estado === 'En proceso') estadoClase = 'EnProceso';
                    else if (orden.estado === 'Completado') estadoClase = 'Completada';
                    else if (orden.estado === 'Cancelado') estadoClase = 'Cancelada';
                    
                    // Determinar qué botones mostrar según el estado
                    let botonesHTML = '';
                    botonesHTML += `<button class="btnVerOrden" onclick="verDetallesOrden(${orden.id})">👁️ Ver</button>`;
                    
                    if (orden.estado === 'Pendiente') {
                        botonesHTML += `<button class="btnProcesarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'En proceso')">⏳ Procesando</button>`;
                        botonesHTML += `<button class="btnCancelarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Cancelado')">❌ Cancelar</button>`;
                    } else if (orden.estado === 'En proceso') {
                        botonesHTML += `<button class="btnListaOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Completado')">✔️ Lista</button>`;
                        botonesHTML += `<button class="btnCancelarOrden" onclick="cambiarEstadoOrden(${orden.id}, 'Cancelado')">❌ Cancelar</button>`;
                    }
                    
                    let fila = `
                        <tr data-id="${orden.id}" data-cliente="${orden.cliente}" data-fecha="${fechaFormateada}" data-total="${orden.total}" data-mesa="${orden.numero_mesa || ''}">
                            <td>${orden.cliente}</td>
                            <td>${fechaFormateada}</td>
                            <td><span class="estadoOrden ${estadoClase}">${orden.estado}</span></td>
                            <td>
                                ${botonesHTML}
                            </td>
                        </tr>
                    `;
                    
                    tablaOrdenes.innerHTML += fila;
                });
            } else {
                console.error('Error al cargar órdenes:', data.message);
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error);
        });
}

function verDetallesOrden(id) {
    // Obtener los detalles de la orden desde la API
    fetch(`/api/ordenes/${id}/detalles`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Obtener información de la orden desde la fila de la tabla
                const fila = document.querySelector(`tr[data-id="${id}"]`);
                const cliente = fila.getAttribute('data-cliente');
                const fecha = fila.getAttribute('data-fecha');
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
                                <span class="info-label">Fecha:</span>
                                <span class="info-value">${fecha}</span>
                            </div>
                            ${mesa ? `
                            <div class="info-grupo">
                                <span class="info-label">Mesa:</span>
                                <span class="info-value">${mesa}</span>
                            </div>` : ''}
                        </div>
                    </div>
                    
                    <div class="productosOrden">
                        <h4 class="productos-titulo">Detalle de Productos</h4>
                        <div class="tabla-responsive">
                            <table class="tabla-productos">
                                <thead>
                                    <tr>
                                        <th>Producto</th>
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
                    
                    detallesHTML += `
                        <tr>
                            <td class="producto-nombre">${detalle.nombre_producto}</td>
                            <td class="precio-unitario">$${precioFormateado}</td>
                            <td class="cantidad-producto">${detalle.cantidad}</td>
                            <td class="subtotal-producto">$${subtotalItem}</td>
                        </tr>`;
                });
                
                detallesHTML += `
                                </tbody>
                                <tfoot>
                                    <tr class="total-row">
                                        <td colspan="3" class="total-label">Total</td>
                                        <td class="total-value">$${parseFloat(total).toFixed(2)}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>`;
                
                document.getElementById('detallesOrden').innerHTML = detallesHTML;
                document.getElementById('ordenModal').style.display = 'flex';
            } else {
                alert('Error al cargar detalles: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error);
        });
}

function cerrarDetallesOrden() {
    document.getElementById('ordenModal').style.display = 'none';
}

function cambiarEstadoOrden(id, nuevoEstado) {
    if (!confirm(`¿Estás seguro de cambiar esta orden a estado "${nuevoEstado}"?`)) {
        return;
    }
    
    fetch(`/api/ordenes/${id}/estado`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            estado: nuevoEstado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            cargarOrdenes(); // Recargar la lista de órdenes
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error en la solicitud:', error);
    });
}

function buscarOrdenes() {
    const busqueda = document.getElementById('buscarCliente').value.toLowerCase();
    const filas = document.querySelectorAll('#tablaOrdenes tr');
    
    filas.forEach(fila => {
        const cliente = fila.querySelector('td:first-child').textContent.toLowerCase();
        if (cliente.includes(busqueda)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
}

function reestablecerFiltros() {
    document.getElementById('buscarCliente').value = '';
    cargarOrdenes();}
