function escaparHtmlHistorial(valor) {
    return String(valor ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

// Estado de paginación
let paginaActual = 1;

document.addEventListener("DOMContentLoaded", function() {
    cargarHistorialVentas();

    document.getElementById("buscarCliente").addEventListener("input", () => { paginaActual = 1; buscarVentas(); });
    document.getElementById("fechaInicio").addEventListener("change", () => { paginaActual = 1; buscarVentas(); });
    document.getElementById("fechaFin").addEventListener("change", () => { paginaActual = 1; buscarVentas(); });
});

function formatearFecha(fechaStr) {
    if (!fechaStr) return "Sin fecha";

    // Intento 1: formato ISO (2026-05-04 18:17:59 o 2026-05-04T18:17:59)
    const partes = fechaStr.match(/(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})/);
    if (partes) {
        const [, anio, mes, dia, horas, minutos, segundos] = partes;
        return `${dia}/${mes}/${anio} ${horas}:${minutos}:${segundos}`;
    }

    // Intento 2: otros formatos (ej: "Mon, 04 May 2026 18:17:59 GMT")
    const fecha = new Date(fechaStr);
    if (!isNaN(fecha.getTime())) {
        const dia = fecha.getDate().toString().padStart(2, '0');
        const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
        const anio = fecha.getFullYear();
        const horas = fecha.getHours().toString().padStart(2, '0');
        const minutos = fecha.getMinutes().toString().padStart(2, '0');
        const segundos = fecha.getSeconds().toString().padStart(2, '0');
        return `${dia}/${mes}/${anio} ${horas}:${minutos}:${segundos}`;
    }

    return fechaStr;
}

function cargarHistorialVentas(filtroCliente = "", fechaInicio = "", fechaFin = "") {
    let url = `/api/historial-ventas?cliente=${encodeURIComponent(filtroCliente)}&fechaInicio=${fechaInicio}&fechaFin=${fechaFin}&pagina=${paginaActual}&por_pagina=15`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaHistorial = document.getElementById("tablaHistorialVentas");
                tablaHistorial.innerHTML = "";

                if (data.ventas.length === 0) {
                    tablaHistorial.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 30px; opacity: 0.6;">No se encontraron ventas</td></tr>`;
                    document.getElementById("paginacionHistorial").innerHTML = "";
                    document.getElementById("paginacionInfo").innerHTML = "";
                    return;
                }

                data.ventas.forEach(venta => {
                    const fechaFormateada = formatearFecha(venta.fecha_hora);
                    const ventaId = Number.parseInt(venta.id, 10);
                    if (!Number.isInteger(ventaId) || ventaId <= 0) {
                        return;
                    }
                    const numeroMesa = venta.numero_mesa
                        ? `Mesa: ${escaparHtmlHistorial(venta.numero_mesa)}`
                        : "Sin mesa";

                    let fila = `
                        <tr>
                            <td>${escaparHtmlHistorial(venta.vendedor)}</td>
                            <td>${escaparHtmlHistorial(venta.cliente)}</td>
                            <td>${fechaFormateada}</td>
                            <td>$${venta.total}</td>
                            <td>${numeroMesa}</td>
                            <td>
                                <button class="btnVerVenta" onclick="verDetallesVenta(${ventaId})">👁️</button>
                            </td>
                        </tr>`;
                    tablaHistorial.innerHTML += fila;
                });

                // Renderizar paginación
                renderizarPaginacion(data.pagina_actual, data.total_paginas, data.total_ventas);
            } else {
                console.error("Error al cargar ventas:", data.message);
            }
        })
        .catch(error => console.error("Error al obtener historial de ventas:", error));
}

function renderizarPaginacion(paginaActualServer, totalPaginas, totalVentas) {
    const contenedor = document.getElementById("paginacionHistorial");
    const info = document.getElementById("paginacionInfo");
    
    if (totalPaginas <= 1) {
        contenedor.innerHTML = "";
        info.innerHTML = `<span>${totalVentas} venta${totalVentas !== 1 ? 's' : ''} en total</span>`;
        return;
    }
    
    let html = '';
    
    // Botón anterior
    html += `<button class="pag-btn pag-flecha ${paginaActualServer <= 1 ? 'disabled' : ''}" 
             onclick="irAPagina(${paginaActualServer - 1})" ${paginaActualServer <= 1 ? 'disabled' : ''}>‹</button>`;
    
    // Calcular rango de páginas a mostrar (máximo 7)
    let inicio = Math.max(1, paginaActualServer - 3);
    let fin = Math.min(totalPaginas, paginaActualServer + 3);
    
    // Ajustar para siempre mostrar 7 si hay suficientes
    if (fin - inicio < 6) {
        if (inicio === 1) fin = Math.min(totalPaginas, 7);
        else inicio = Math.max(1, fin - 6);
    }
    
    // Primera página + puntos suspensivos si es necesario
    if (inicio > 1) {
        html += `<button class="pag-btn" onclick="irAPagina(1)">1</button>`;
        if (inicio > 2) html += `<span class="pag-puntos">...</span>`;
    }
    
    // Páginas del rango
    for (let i = inicio; i <= fin; i++) {
        html += `<button class="pag-btn ${i === paginaActualServer ? 'pag-activa' : ''}" 
                 onclick="irAPagina(${i})">${i}</button>`;
    }
    
    // Última página + puntos suspensivos si es necesario
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) html += `<span class="pag-puntos">...</span>`;
        html += `<button class="pag-btn" onclick="irAPagina(${totalPaginas})">${totalPaginas}</button>`;
    }
    
    // Botón siguiente
    html += `<button class="pag-btn pag-flecha ${paginaActualServer >= totalPaginas ? 'disabled' : ''}" 
             onclick="irAPagina(${paginaActualServer + 1})" ${paginaActualServer >= totalPaginas ? 'disabled' : ''}>›</button>`;
    
    contenedor.innerHTML = html;
    
    // Info
    const desde = (paginaActualServer - 1) * 15 + 1;
    const hasta = Math.min(paginaActualServer * 15, totalVentas);
    info.innerHTML = `<span>Mostrando ${desde}-${hasta} de ${totalVentas} ventas</span>`;
}

function irAPagina(pagina) {
    paginaActual = pagina;
    buscarVentas();
    // Scroll suave al inicio de la tabla
    document.querySelector('.listaVentas').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buscarVentas() {
    let cliente = document.getElementById("buscarCliente").value;
    let fechaInicio = document.getElementById("fechaInicio").value;
    let fechaFin = document.getElementById("fechaFin").value;

    cargarHistorialVentas(cliente, fechaInicio, fechaFin);
}

function reestablecerFiltros() {
    document.getElementById("buscarCliente").value = "";
    document.getElementById("fechaInicio").value = "";
    document.getElementById("fechaFin").value = "";
    paginaActual = 1;
    cargarHistorialVentas();
}

function verDetallesVenta(id) {
    fetch(`/api/historial-ventas/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.venta && data.detalles) {
                const venta = data.venta;
                const detalles = data.detalles;
                
                let detallesHTML = `
                    <div class="venta-header">
                        <div class="venta-id">
                            <span class="venta-label">Venta #</span>
                            <span class="venta-value">${id}</span>
                        </div>
                        <div class="venta-fecha">
                            <span class="fecha-value">${formatearFecha(venta.fecha_hora)}</span>
                        </div>
                    </div>
                    
                    <div class="venta-info-container">
                        <div class="venta-info-grupo">
                            <span class="info-label">Vendedor:</span>
                            <span class="info-value">${escaparHtmlHistorial(venta.vendedor || 'No disponible')}</span>
                        </div>
                        
                        <div class="venta-info-grupo">
                            <span class="info-label">Cliente:</span>
                            <span class="info-value">${escaparHtmlHistorial(venta.cliente || 'No disponible')}</span>
                        </div>
                        
                        <div class="venta-info-grupo">
                            <span class="info-label">Método de pago:</span>
                            <span class="info-value">${escaparHtmlHistorial(venta.metodo_pago || 'No especificado')}</span>
                        </div>
                        
                        <div class="venta-info-grupo">
                            <span class="info-label">Dinero recibido:</span>
                            <span class="info-value">$${parseFloat(venta.dinero_recibido || 0).toFixed(2)}</span>
                        </div>
                        
                        <div class="venta-info-grupo">
                            <span class="info-label">Cambio:</span>
                            <span class="info-value">$${parseFloat(venta.cambio || 0).toFixed(2)}</span>
                        </div>
                        
                        ${venta.numero_mesa ? `
                        <div class="venta-info-grupo">
                            <span class="info-label">Mesa:</span>
                            <span class="info-value">${escaparHtmlHistorial(venta.numero_mesa)}</span>
                        </div>` : ''}
                    </div>
                    
                    <div class="productos-container">
                        <h4 class="productos-titulo">Productos Vendidos</h4>
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

                if (detalles.length === 0) {
                    detallesHTML += `<tr><td colspan="5" class="no-productos">No hay productos en esta venta</td></tr>`;
                } else {
                    let subtotal = 0;
                    detalles.forEach(producto => {
                        // Manejar productos eliminados donde el precio puede ser nulo
                        let precio = parseFloat(producto.precio);
                        if (isNaN(precio) && producto.subtotal && producto.cantidad) {
                            precio = parseFloat(producto.subtotal) / parseInt(producto.cantidad);
                        }
                        const precioFormateado = isNaN(precio) ? '0.00' : precio.toFixed(2);
                        const subtotalItem = parseFloat(producto.subtotal || 0).toFixed(2);
                        subtotal += parseFloat(subtotalItem);
                        const tamano = producto.tamano || 'No aplica';

                        detallesHTML += `
                            <tr>
                                <td class="producto-nombre">${escaparHtmlHistorial(producto.nombre_producto)}</td>
                                <td class="producto-tamano">${escaparHtmlHistorial(tamano)}</td>
                                <td class="precio-unitario">$${precioFormateado}</td>
                                <td class="cantidad-producto">${producto.cantidad}</td>
                                <td class="subtotal-producto">$${subtotalItem}</td>
                            </tr>`;
                    });
                }

                detallesHTML += `
                                </tbody>
                                <tfoot>
                                    <tr class="total-row">
                                        <td colspan="4" class="total-label">Total</td>
                                        <td class="total-value">$${parseFloat(venta.total || 0).toFixed(2)}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>`;

                document.getElementById("detallesVenta").innerHTML = detallesHTML;
                document.getElementById("ventaModal").style.display = "flex";
            } else {
                console.error("Datos de la venta incompletos:", data);
                alert("No se encontraron detalles de la venta.");
            }
        })
        .catch(error => {
            console.error("Error al obtener detalles de la venta:", error);
            alert("Error al cargar los detalles de la venta");
        });
}

function cerrarDetallesVenta() {
    document.getElementById("ventaModal").style.display = "none";
}
