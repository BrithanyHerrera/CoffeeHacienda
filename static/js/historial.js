document.addEventListener("DOMContentLoaded", function() {
    cargarHistorialVentas();

    document.getElementById("buscarCliente").addEventListener("input", buscarVentas);
    document.getElementById("fechaInicio").addEventListener("change", buscarVentas);
    document.getElementById("fechaFin").addEventListener("change", buscarVentas);
});

function formatearFecha(fechaStr) {
    if (!fechaStr) return "Sin fecha";

    const fechaUTC = new Date(fechaStr);
    if (isNaN(fechaUTC.getTime())) return "Fecha inválida";

    // Convertir a la zona horaria local sin desfases
    const fechaLocal = new Date(fechaUTC.getTime() + fechaUTC.getTimezoneOffset() * 60000);

    // Formatear fecha y hora en formato 24 horas (HH:MM:SS)
    const dia = fechaLocal.getDate().toString().padStart(2, '0');
    const mes = (fechaLocal.getMonth() + 1).toString().padStart(2, '0');
    const anio = fechaLocal.getFullYear();
    const horas = fechaLocal.getHours().toString().padStart(2, '0');
    const minutos = fechaLocal.getMinutes().toString().padStart(2, '0');
    const segundos = fechaLocal.getSeconds().toString().padStart(2, '0');

    return `${dia}/${mes}/${anio} ${horas}:${minutos}:${segundos}`;
}

function cargarHistorialVentas(filtroCliente = "", fechaInicio = "", fechaFin = "") {
    let url = `/api/historial-ventas?cliente=${filtroCliente}&fechaInicio=${fechaInicio}&fechaFin=${fechaFin}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaHistorial = document.getElementById("tablaHistorialVentas");
                tablaHistorial.innerHTML = "";

                data.ventas.forEach(venta => {
                    // Formatear la fecha correctamente
                    const fechaFormateada = formatearFecha(venta.fecha_hora);

                    // Mostrar número de mesa si existe
                    const numeroMesa = venta.numero_mesa ? `Mesa: ${venta.numero_mesa}` : "Sin mesa";

                    let fila = `
                        <tr>
                            <td>${venta.vendedor}</td>
                            <td>${venta.cliente}</td>
                            <td>${fechaFormateada}</td>
                            <td>$${venta.total}</td>
                            <td>${numeroMesa}</td>
                            <td>
                                <button class="btnVerVenta" onclick="verDetallesVenta(${venta.id})">👁️</button>
                            </td>
                        </tr>`;
                    tablaHistorial.innerHTML += fila;
                });
            } else {
                alert("Error al cargar ventas: " + data.message);
            }
        })
        .catch(error => console.error("Error al obtener historial de ventas:", error));
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
    cargarHistorialVentas();
}

function verDetallesVenta(id) {
    console.log("Obteniendo detalles de la venta con ID:", id);

    let ventaInfo = obtenerInfoVentaDesdeTabla(id);

    fetch(`/api/historial-ventas/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.detalles) {
                let detallesHTML = `
                    <div class="venta-header">
                        <div class="venta-id">
                            <span class="venta-label">Venta #</span>
                            <span class="venta-value">${id}</span>
                        </div>
                        <div class="venta-fecha">
                            <span class="fecha-value">${ventaInfo.fecha || 'Sin fecha'}</span>
                        </div>
                    </div>
                    
                    <div class="venta-info-container">
                        <div class="venta-info-grupo">
                            <span class="info-label">Cliente:</span>
                            <span class="info-value">${ventaInfo.cliente || 'No disponible'}</span>
                        </div>
                        
                        ${ventaInfo.mesa && ventaInfo.mesa !== "Sin mesa" ? `
                        <div class="venta-info-grupo">
                            <span class="info-label">Mesa:</span>
                            <span class="info-value">${ventaInfo.mesa.replace('Mesa: ', '')}</span>
                        </div>` : ''}
                    </div>
                    
                    <div class="productos-container">
                        <h4 class="productos-titulo">Productos Vendidos</h4>
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

                if (data.detalles.length === 0) {
                    detallesHTML += `<tr><td colspan="4" class="no-productos">No hay productos en esta venta</td></tr>`;
                } else {
                    let subtotal = 0;
                    data.detalles.forEach(producto => {
                        const precioFormateado = parseFloat(producto.precio).toFixed(2);
                        const subtotalItem = parseFloat(producto.subtotal).toFixed(2);
                        subtotal += parseFloat(subtotalItem);

                        detallesHTML += `
                            <tr>
                                <td class="producto-nombre">${producto.nombre_producto}</td>
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
                                        <td colspan="3" class="total-label">Total</td>
                                        <td class="total-value">$${parseFloat(ventaInfo.total || 0).toFixed(2)}</td>
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

function obtenerInfoVentaDesdeTabla(id) {
    const filas = document.querySelectorAll("#tablaHistorialVentas tr");
    let ventaInfo = { cliente: '', fecha: '', total: '', mesa: '' };

    for (let fila of filas) {
        const boton = fila.querySelector(`button[onclick="verDetallesVenta(${id})"]`);
        if (boton) {
            const celdas = fila.querySelectorAll("td");
            ventaInfo.cliente = celdas[1].textContent.trim();
            ventaInfo.fecha = celdas[2].textContent.trim();
            ventaInfo.total = celdas[3].textContent.trim().replace('$', '');
            ventaInfo.mesa = celdas[4].textContent.trim();
            break;
        }
    }

    return ventaInfo;
}

function cerrarDetallesVenta() {
    document.getElementById("ventaModal").style.display = "none";
}
