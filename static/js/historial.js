document.addEventListener("DOMContentLoaded", function() {
    cargarHistorialVentas();

    document.getElementById("buscarCliente").addEventListener("input", buscarVentas);
    document.getElementById("fechaInicio").addEventListener("change", buscarVentas);
    document.getElementById("fechaFin").addEventListener("change", buscarVentas);
});

function formatearFecha(fechaStr) {
    if (!fechaStr) return "Sin fecha";
    
    // Verificar si la fecha es válida
    const fecha = new Date(fechaStr);
    if (isNaN(fecha.getTime())) return "Fecha inválida";
    
    // Formatear la fecha como DD/MM/YYYY hh:mm AM/PM
    return fecha.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true // Esto agrega el formato AM/PM
    });
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
    
    fetch(`/api/historial-ventas/${id}`)
        .then(response => {
            console.log("Respuesta de la API:", response);
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos:", data);
            
            if (data.success && data.detalles && data.detalles.length > 0) {
                let venta = data.detalles[0]; // Tomamos la primera fila para obtener la info general
                console.log("Datos de la venta:", venta);
                
                // Verificar los nombres de las propiedades
                console.log("Propiedades disponibles:", Object.keys(venta));
                
                // Formatear la fecha correctamente
                const fechaFormateada = formatearFecha(venta.fecha_hora);
                
                // Crear el contenido HTML para los detalles de la venta
                let detallesHTML = `
                    <div class="infoVenta">
                        <p><strong>ID Venta:</strong> <span id="idVenta">${venta.id}</span></p>
                        <p><strong>Cliente:</strong> <span id="nombreClienteVenta">${venta.cliente}</span></p>
                        <p><strong>Fecha:</strong> <span id="fechaVenta">${fechaFormateada}</span></p>
                        <p><strong>Total:</strong> $<span id="totalVenta">${venta.total}</span></p>`;
                
                // Agregar número de mesa si existe
                if (venta.numero_mesa) {
                    detallesHTML += `<p><strong>Mesa:</strong> <span id="mesaVenta">${venta.numero_mesa}</span></p>`;
                }
                
                detallesHTML += `
                    </div>
                    <div class="productosVenta">
                        <h4>Productos</h4>
                        <table id="tablaProductosVenta">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th>Precio Unitario</th>
                                    <th>Cantidad</th>
                                    <th>Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>`;
                
                data.detalles.forEach(producto => {
                    // Verificar si precio_unitario existe, si no, usar precio
                    let precioUnitario = producto.precio_unitario || producto.precio;
                    
                    detallesHTML += `
                        <tr>
                            <td>${producto.nombre_producto}</td>
                            <td>$${precioUnitario}</td>
                            <td>${producto.cantidad}</td>
                            <td>$${(precioUnitario * producto.cantidad).toFixed(2)}</td>
                        </tr>`;
                });
                
                detallesHTML += `
                            </tbody>
                        </table>
                    </div>`;
                
                // Insertar el HTML en el contenedor de detalles
                document.getElementById("detallesVenta").innerHTML = detallesHTML;
                
                // Mostrar el modal
                document.getElementById("ventaModal").style.display = "flex";
            } else {
                console.error("Datos de la venta incompletos:", data);
                alert("No se encontraron detalles de la venta. Revisa la consola para más información.");
            }
        })
        .catch(error => {
            console.error("Error al obtener detalles de la venta:", error);
            alert("Error al cargar los detalles de la venta. Revisa la consola para más información.");
        });
}

function cerrarDetallesVenta() {
    document.getElementById("ventaModal").style.display = "none";
}
