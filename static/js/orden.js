function cambiarEstadoOrden(id, estado) {
    // Cambiar el estado visualmente en la interfaz
    let estadoElement = document.querySelector(`#estado-${id}`);
    estadoElement.className = `estadoOrden ${estado.toLowerCase()}`;
    estadoElement.textContent = estado;
}

function verDetallesOrden(id) {
    // Mostrar un modal con los detalles de la orden
    let modal = document.getElementById('ordenModal');
    modal.style.display = 'flex';

    document.getElementById('idOrden').textContent = id;
    document.getElementById('nombreCliente').textContent = 'Ana Gomez';  // Ejemplo
    document.getElementById('fechaOrden').textContent = '2025-03-02';  // Ejemplo
    document.getElementById('estadoOrden').textContent = 'En Espera';  // Ejemplo

    let tablaProductos = document.getElementById('tablaProductos').getElementsByTagName('tbody')[0];
    tablaProductos.innerHTML = '';  

    // Ejemplo de productos
    let productos = [
        { producto: 'Cappuccino', precio: 4.98, cantidad: 2, total: 9.96 },
        { producto: 'Latte', precio: 5.50, cantidad: 1, total: 5.50 }
    ];

    productos.forEach((producto) => {
        let row = tablaProductos.insertRow();
        row.innerHTML = `<td>${producto.producto}</td><td>$${producto.precio}</td><td>${producto.cantidad}</td><td>$${producto.total}</td>`;
    });

    // Calcular el total de la orden
    let total = productos.reduce((acc, curr) => acc + curr.total, 0);
    document.getElementById('totalOrden').textContent = total.toFixed(2);
}

function cerrarDetallesOrden() {
    let modal = document.getElementById('ordenModal');
    modal.style.display = 'none';
}
