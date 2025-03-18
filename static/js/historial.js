document.addEventListener("DOMContentLoaded", function() {
    cargarHistorialVentas();

    document.getElementById("buscarCliente").addEventListener("input", buscarVentas);
    document.getElementById("fechaInicio").addEventListener("change", buscarVentas);
    document.getElementById("fechaFin").addEventListener("change", buscarVentas);
});

function cargarHistorialVentas(filtroCliente = "", fechaInicio = "", fechaFin = "") {
    let url = `/api/historial-ventas?cliente=${filtroCliente}&fechaInicio=${fechaInicio}&fechaFin=${fechaFin}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tablaHistorial = document.getElementById("tablaHistorialVentas");
                tablaHistorial.innerHTML = "";

                data.ventas.forEach(venta => {
                    let fila = `
                        <tr>
                            <td>${venta.vendedor}</td>
                            <td>${venta.cliente}</td>
                            <td>${venta.fecha_venta}</td>
                            <td>$${venta.total}</td>
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
    fetch(`/api/historial-ventas/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let venta = data.detalles[0]; // Tomamos la primera fila para obtener la info general

                document.getElementById("idVenta").innerText = venta.id;
                document.getElementById("nombreClienteVenta").innerText = venta.cliente;
                document.getElementById("fechaVenta").innerText = venta.fecha_venta;
                document.getElementById("totalVenta").innerText = venta.total;

                let tablaProductos = document.getElementById("tablaProductosVenta").querySelector("tbody");
                tablaProductos.innerHTML = "";

                data.detalles.forEach(producto => {
                    let fila = `
                        <tr>
                            <td>${producto.nombre_producto}</td>
                            <td>$${producto.precio_unitario}</td>
                            <td>${producto.cantidad}</td>
                            <td>$${(producto.precio_unitario * producto.cantidad).toFixed(2)}</td>
                        </tr>`;
                    tablaProductos.innerHTML += fila;
                });

                document.getElementById("ventaModal").style.display = "block";
            } else {
                alert("No se encontraron detalles de la venta.");
            }
        })
        .catch(error => console.error("Error al obtener detalles de la venta:", error));
}

function cerrarDetallesVenta() {
    document.getElementById("ventaModal").style.display = "none";
}
