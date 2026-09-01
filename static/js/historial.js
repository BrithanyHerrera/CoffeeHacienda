

// Estado de paginación
let paginaActual = 1;

document.addEventListener("DOMContentLoaded", function() {
    cargarHistorialVentas();

    document.getElementById("buscarCliente").addEventListener("input", () => { paginaActual = 1; buscarVentas(); });
    document.getElementById("fechaInicio").addEventListener("change", () => { paginaActual = 1; buscarVentas(); });
    document.getElementById("fechaFin").addEventListener("change", () => { paginaActual = 1; buscarVentas(); });
});



function cargarHistorialVentas(filtroCliente = "", fechaInicio = "", fechaFin = "") {
    let url = `/api/historial-ventas?cliente=${encodeURIComponent(filtroCliente)}&fechaInicio=${fechaInicio}&fechaFin=${fechaFin}&pagina=${paginaActual}&por_pagina=15`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaHistorial = document.getElementById("tablaHistorialVentas");
                tablaHistorial.replaceChildren();

                if (data.ventas.length === 0) {
                    const filaVacia = document.createElement('tr');
                    const celdaVacia = document.createElement('td');
                    celdaVacia.colSpan = 6;
                    celdaVacia.className = 'text-center';
                    celdaVacia.textContent = 'No se encontraron ventas';
                    filaVacia.append(celdaVacia);
                    tablaHistorial.append(filaVacia);
                    document.getElementById("paginacionHistorial").replaceChildren();
                    document.getElementById("paginacionInfo").replaceChildren();
                    return;
                }

                data.ventas.forEach(venta => {
                    const fechaFormateada = formatearFecha(venta.fecha_hora);
                    const ventaId = Number.parseInt(venta.id, 10);
                    if (!Number.isInteger(ventaId) || ventaId <= 0) {
                        return;
                    }
                    const fila = document.createElement('tr');
                    [venta.vendedor, venta.cliente, fechaFormateada,
                        `$${Number(venta.total || 0).toFixed(2)}`,
                        venta.numero_mesa ? `Mesa: ${venta.numero_mesa}` : 'Sin mesa']
                        .forEach(valor => { const celda = document.createElement('td'); celda.textContent = valor || ''; fila.append(celda); });
                    const acciones = document.createElement('td');
                    const boton = document.createElement('button');
                    boton.className = 'btnVerVenta';
                    boton.type = 'button';
                    boton.textContent = '👁️';
                    boton.addEventListener('click', () => verDetallesVenta(ventaId));
                    acciones.append(boton); fila.append(acciones);
                    tablaHistorial.append(fila);
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
        contenedor.replaceChildren();
        info.replaceChildren();
        const resumen = document.createElement('span');
        resumen.textContent = `${totalVentas} venta${totalVentas !== 1 ? 's' : ''} en total`;
        info.append(resumen);
        return;
    }
    
    contenedor.replaceChildren();
    const agregarBoton = (texto, pagina, clase = '', deshabilitado = false) => {
        const boton = document.createElement('button');
        boton.className = `pag-btn ${clase}`.trim(); boton.type = 'button'; boton.textContent = texto;
        boton.disabled = deshabilitado; boton.addEventListener('click', () => irAPagina(pagina));
        contenedor.append(boton);
    };
    agregarBoton('‹', paginaActualServer - 1, 'pag-flecha', paginaActualServer <= 1);
    
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
        agregarBoton('1', 1);
        if (inicio > 2) { const puntos = document.createElement('span'); puntos.className = 'pag-puntos'; puntos.textContent = '...'; contenedor.append(puntos); }
    }
    
    // Páginas del rango
    for (let i = inicio; i <= fin; i++) {
        agregarBoton(String(i), i, i === paginaActualServer ? 'pag-activa' : '');
    }
    
    // Última página + puntos suspensivos si es necesario
    if (fin < totalPaginas) {
        if (fin < totalPaginas - 1) { const puntos = document.createElement('span'); puntos.className = 'pag-puntos'; puntos.textContent = '...'; contenedor.append(puntos); }
        agregarBoton(String(totalPaginas), totalPaginas);
    }
    
    // Botón siguiente
    agregarBoton('›', paginaActualServer + 1, 'pag-flecha', paginaActualServer >= totalPaginas);
    
    // Info
    const desde = (paginaActualServer - 1) * 15 + 1;
    const hasta = Math.min(paginaActualServer * 15, totalVentas);
    info.replaceChildren();
    const resumen = document.createElement('span');
    resumen.textContent = `Mostrando ${desde}-${hasta} de ${totalVentas} ventas`;
    info.append(resumen);
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
                const elemento = (tag, clase, texto) => {
                    const nodo = document.createElement(tag);
                    if (clase) nodo.className = clase;
                    if (texto !== undefined) nodo.textContent = texto;
                    return nodo;
                };
                const contenido = document.getElementById('detallesVenta');
                contenido.replaceChildren();
                const encabezado = elemento('div', 'venta-header');
                const ventaId = elemento('div', 'venta-id');
                ventaId.append(elemento('span', 'venta-label', 'Venta #'), elemento('span', 'venta-value', id));
                const fecha = elemento('div', 'venta-fecha');
                fecha.append(elemento('span', 'fecha-value', formatearFecha(venta.fecha_hora)));
                encabezado.append(ventaId, fecha);
                contenido.append(encabezado);

                const info = elemento('div', 'venta-info-container');
                [['Vendedor:', venta.vendedor || 'No disponible'], ['Cliente:', venta.cliente || 'No disponible'],
                    ['Método de pago:', venta.metodo_pago || 'No especificado'],
                    ['Dinero recibido:', `$${parseFloat(venta.dinero_recibido || 0).toFixed(2)}`],
                    ['Cambio:', `$${parseFloat(venta.cambio || 0).toFixed(2)}`]]
                    .concat(venta.numero_mesa ? [['Mesa:', venta.numero_mesa]] : [])
                    .forEach(([etiqueta, valor]) => { const grupo = elemento('div', 'venta-info-grupo'); grupo.append(elemento('span', 'info-label', etiqueta), elemento('span', 'info-value', valor)); info.append(grupo); });
                contenido.append(info);

                const productos = elemento('div', 'productos-container');
                productos.append(elemento('h4', 'productos-titulo', 'Productos Vendidos'));
                const responsive = elemento('div', 'tabla-responsive');
                const tabla = elemento('table', 'tabla-productos');
                const thead = elemento('thead'); const headRow = elemento('tr');
                ['Producto', 'Tamaño', 'Precio Unit.', 'Cant.', 'Subtotal'].forEach(t => headRow.append(elemento('th', null, t)));
                thead.append(headRow); tabla.append(thead);
                const tbody = elemento('tbody');
                if (!detalles.length) { const row = elemento('tr'); const cell = elemento('td', 'no-productos', 'No hay productos en esta venta'); cell.colSpan = 5; row.append(cell); tbody.append(row); }
                else detalles.forEach(producto => { let precio = parseFloat(producto.precio); if (isNaN(precio) && producto.subtotal && producto.cantidad) precio = parseFloat(producto.subtotal) / parseInt(producto.cantidad); const row = elemento('tr'); [producto.nombre_producto, producto.tamano || 'No aplica', `$${isNaN(precio) ? '0.00' : precio.toFixed(2)}`, producto.cantidad, `$${parseFloat(producto.subtotal || 0).toFixed(2)}`].forEach(v => row.append(elemento('td', null, v))); tbody.append(row); });
                tabla.append(tbody);
                const tfoot = elemento('tfoot'); const totalRow = elemento('tr', 'total-row'); const label = elemento('td', 'total-label', 'Total'); label.colSpan = 4; totalRow.append(label, elemento('td', 'total-value', `$${parseFloat(venta.total || 0).toFixed(2)}`)); tfoot.append(totalRow); tabla.append(tfoot);
                responsive.append(tabla); productos.append(responsive); contenido.append(productos);
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
