function verDetallesVenta(id) {
    let modal = document.getElementById('ventaModal');
    modal.style.display = 'flex';

    document.getElementById('idVenta').textContent = id;
    document.getElementById('nombreClienteVenta').textContent = 'Juan Pérez';  // Ejemplo
    document.getElementById('fechaVenta').textContent = '2025-03-02';  // Ejemplo
    document.getElementById('totalVenta').textContent = '19.92';  // Ejemplo

    let tablaProductosVenta = document.getElementById('tablaProductosVenta').getElementsByTagName('tbody')[0];
    tablaProductosVenta.innerHTML = '';  // Limpiar tabla

    // Ejemplo
    let productos = [
        { producto: 'Cappuccino', precio: 4.98, cantidad: 2, total: 9.96 },
        { producto: 'Latte', precio: 5.50, cantidad: 1, total: 5.50 }
    ];

    productos.forEach((producto) => {
        let row = tablaProductosVenta.insertRow();
        row.innerHTML = `<td>${producto.producto}</td><td>$${producto.precio}</td><td>${producto.cantidad}</td><td>$${producto.total}</td>`;
    });
}

function cerrarDetallesVenta() {
    let modal = document.getElementById('ventaModal');
    modal.style.display = 'none';
}
// Función para filtrar ventas automáticamente
function buscarVentas() {
    const cliente = document.getElementById('buscarCliente').value.toLowerCase();
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    // Filtra las filas en la tabla
    const filas = document.querySelectorAll('#tablaHistorialVentas tr');
    filas.forEach(fila => {
        const clienteNombre = fila.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const fechaVenta = fila.querySelector('td:nth-child(2)').textContent;

        // Comprueba si coincide con el cliente y las fechas
        const coincideCliente = cliente === '' || clienteNombre.includes(cliente);
        const coincideFechaInicio = fechaInicio === '' || new Date(fechaVenta) >= new Date(fechaInicio);
        const coincideFechaFin = fechaFin === '' || new Date(fechaVenta) <= new Date(fechaFin);

        if (coincideCliente && coincideFechaInicio && coincideFechaFin) {
            fila.style.display = ''; // Muestra la fila
        } else {
            fila.style.display = 'none'; // Oculta la fila
        }
    });
}
