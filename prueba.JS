document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const productos = document.querySelectorAll('.producto');

    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('h3').textContent.toLowerCase();
        producto.style.display = nombreProducto.includes(searchTerm) ? '' : 'none';
    });
});

// Función para filtrar productos por categoría
function filtrarProductos(categoria) {
    const productos = document.querySelectorAll('.producto');

    productos.forEach(producto => {
        const productoCategoria = producto.getAttribute('categoriasDatos').toLowerCase();
        producto.style.display = (productoCategoria === categoria || categoria === 'todos') ? '' : 'none';
    });
}

// Inicializar el carrito
let carrito = [];

// Función para agregar un producto al carrito
function agregarAlCarrito(nombre, precio, imagen, tamaño) {
    const productoExistente = carrito.find(item => item.nombre === nombre && item.tamaño === tamaño);
    
    if (productoExistente) {
        productoExistente.cantidad++;
    } else {
        carrito.push({ nombre, precio, cantidad: 1, imagen, tamaño });
    }
    
    actualizarCarrito();
}

// Agregar eventos a los botones "Añadir a la orden"
document.querySelectorAll('.añadirCarrito').forEach(button => {
    button.addEventListener('click', function() {
        const producto = this.parentElement;
        const nombre = producto.querySelector('h3').textContent;
        const imagen = producto.querySelector('img').src;
        const tamañoTexto = producto.querySelector('.tamaños p').textContent;

        const [tamaño, precioTexto] = tamañoTexto.split(' - $');
        const precio = parseFloat(precioTexto);

        agregarAlCarrito(nombre, precio, imagen, tamaño);
    });
});

// Función para actualizar el carrito en la interfaz
function actualizarCarrito() {
    const carritoItems = document.querySelector('.carritoItems');
    carritoItems.innerHTML = '';

    let total = 0;
    carrito.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('carritoItem');
        itemDiv.innerHTML = `
            <img src="${item.imagen}" alt="${item.nombre}">
            <div>
                <h4>${item.nombre} (${item.tamaño})</h4>
                <p>${item.cantidad} - $${item.precio * item.cantidad}</p>
            </div>
            <button class="eliminarItemCarrito" onclick="eliminarDelCarrito('${item.nombre}', '${item.tamaño}')">X</button>
        `;
        carritoItems.appendChild(itemDiv);
        total += item.precio * item.cantidad;
    });

    document.getElementById('total').textContent = `$${total}`;
}

// Función para eliminar un producto del carrito
function eliminarDelCarrito(nombre, tamaño) {
    carrito = carrito.filter(item => item.nombre !== nombre || item.tamaño !== tamaño);
    actualizarCarrito();
}

// Función para realizar el pedido
function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();

    if (nombreCliente === '') {
        alert('Por favor, ingrese su nombre.');
        return;
    }

    alert(`Pedido realizado por: ${nombreCliente}\nTotal: ${document.getElementById('total').textContent}`);
    
    carrito = [];
    actualizarCarrito();
    document.getElementById('nombreCliente').value = '';
}

// Función para eliminar un producto del carrito
function eliminarDelCarrito(nombre, tamaño) {
    carrito = carrito.filter(item => item.nombre !== nombre || item.tamaño !== tamaño);
    actualizarCarrito();
}


function generarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Obtener la fecha y hora actual
    const fechaHora = new Date().toLocaleString();
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const direccionSucursal = "Calle Ejemplo 123, Ciudad"; // Dirección de la sucursal

    // Agregar contenido al PDF
    doc.text(`Recibo`, 10, 10);
    doc.text(`Fecha y Hora: ${fechaHora}`, 10, 20);
    doc.text(`Nombre del Vendedor: Administrador`, 10, 30);
    doc.text(`Dirección de la Sucursal: ${direccionSucursal}`, 10, 40);
    doc.text(`Nombre del Cliente: ${nombreCliente}`, 10, 50);
    doc.text(`Artículos:`, 10, 60);

    // Agregar los artículos al PDF
    let y = 70; // Posición vertical inicial para los artículos
    carrito.forEach(item => {
        doc.text(`${item.nombre} (${item.tamaño}) - $${item.precio} x ${item.cantidad}`, 10, y);
        y += 10; // Incrementar la posición vertical
    });

    // Calcular y agregar el total
    const total = carrito.reduce((acc, item) => acc + (item.precio * item.cantidad), 0);
    doc.text(`Total: $${total}`, 10, y);

    // Guardar el PDF
    doc.save('recibo.pdf');
}