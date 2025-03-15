document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase(); // Obtener el término de búsqueda en minúsculas
    const productos = document.querySelectorAll('.producto'); // Seleccionar todos los productos

    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('h3').textContent.toLowerCase(); // Obtener el nombre del producto
        if (nombreProducto.includes(searchTerm)) {
            producto.style.display = ''; // Mostrar el producto si coincide
        } else {
            producto.style.display = 'none'; // Ocultar el producto si no coincide
        }
    });
});

// Función para filtrar productos por categoría
function filtrarProductos(categoria) {
    const productos = document.querySelectorAll('.producto'); // Seleccionar todos los productos

    productos.forEach(producto => {
        const productoCategoria = producto.getAttribute('categoriasDatos').toLowerCase(); // Obtener la categoría del producto
        if (productoCategoria === categoria || categoria === 'todos') {
            producto.style.display = ''; // Mostrar el producto si coincide
        } else {
            producto.style.display = 'none'; // Ocultar el producto si no coincide
        }
    });
}

// Agregar eventos a los botones de categoría
document.querySelectorAll('.categoriasBebidas button').forEach(button => {
    button.addEventListener('click', function() {
        const categoria = this.textContent.toLowerCase().replace('', ''); // Obtener la categoría del botón
        filtrarProductos(categoria); // Filtrar productos
    });
});

// Filtrar todos los productos al cargar la página
window.onload = function() {
    filtrarProductos('todos'); // Mostrar todos los productos al cargar
};

// Inicializar el carrito
let carrito = [];

// Función para agregar un producto al carrito
function agregarAlCarrito(nombre, precio, imagen, tamaño) {
    // Verificar si el producto ya está en el carrito
    const productoExistente = carrito.find(item => item.nombre === nombre && item.tamaño === tamaño);
    if (productoExistente) {
        // Si ya existe, aumentar la cantidad
        productoExistente.cantidad++;
    } else {
        // Si no existe, agregarlo al carrito
        carrito.push({ nombre, precio, cantidad: 1, imagen, tamaño });
    }
    actualizarCarrito();
}

// Función para actualizar el carrito en la interfaz
function actualizarCarrito() {
    const carritoItems = document.querySelector('.carritoItems');
    carritoItems.innerHTML = ''; // Limpiar el carrito

    let total = 0; // Inicializar el total
    carrito.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('carritoItem');
        itemDiv.innerHTML = `
            <img src="${item.imagen}" alt="${item.nombre}">
            <div>
                <h4>${item.nombre} (${item.tamaño})</h4>
                <p>${item.cantidad} - $${item.precio * item.cantidad}</p>
            </div>
            <input type="number" value="${item.cantidad}" min="1" onchange="actualizarCantidad('${item.nombre}', this.value, '${item.tamaño}')">
            <button class="eliminarItemCarrito" onclick="eliminarDelCarrito('${item.nombre}', '${item.tamaño}')">X</button>
        `;
        carritoItems.appendChild(itemDiv);
        total += item.precio * item.cantidad; // Sumar al total
    });

    document.getElementById('total').textContent = `$${total}`; // Actualizar el total
}

// Función para actualizar la cantidad de un producto en el carrito
function actualizarCantidad(nombre, cantidad, tamaño) {
    const producto = carrito.find(item => item.nombre === nombre && item.tamaño === tamaño);
    if (producto) {
        producto.cantidad = parseInt(cantidad);
        actualizarCarrito();
    }
}

// Función para eliminar un producto del carrito
function eliminarDelCarrito(nombre, tamaño) {
    carrito = carrito.filter(item => item.nombre !== nombre || item.tamaño !== tamaño);
    actualizarCarrito();
}

// Agregar eventos a los botones "Añadir a la orden"
document.querySelectorAll('.añadirCarrito').forEach(button => {
    button.addEventListener('click', function() {
        const producto = this.parentElement; // Obtener el producto
        const nombre = producto.querySelector('h3').textContent; // Obtener el nombre del producto
        const imagen = producto.querySelector('img').src; // Obtener la imagen del producto
        const tamañoButton = Array.from(producto.querySelectorAll('.tamaño')).find(btn => btn.classList.contains('selected'));
        const precio = parseFloat(tamañoButton.getAttribute('preciosDatos')); // Obtener el precio del tamaño seleccionado
        const tamaño = tamañoButton.textContent.split(' - ')[0]; // Obtener el tamaño seleccionado
        agregarAlCarrito(nombre, precio, imagen, tamaño); // Agregar al carrito
    });
});

// Agregar eventos a los botones de tamaño
document.querySelectorAll('.tamaño').forEach(button => {
    button.addEventListener('click', function() {
        // Remover la clase 'selected' de todos los botones
        document.querySelectorAll('.tamaño').forEach(btn => btn.classList.remove('selected'));
        // Agregar la clase 'selected' al botón clicado
        this.classList.add('selected');
    });
});

function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim(); // Obtener el nombre del cliente

    if (nombreCliente === '') {
        alert('Por favor, ingrese su nombre.'); // Alerta si el nombre está vacío
        return; // Salir de la función si el nombre está vacío
    }

    // Aquí puedes agregar la lógica para procesar el pedido
    alert(`Pedido realizado por: ${nombreCliente}\nTotal: ${document.getElementById('total').textContent}`);
    
    // Limpiar el carrito y el nombre del cliente después de realizar el pedido
    carrito = [];
    actualizarCarrito();
    document.getElementById('nombreCliente').value = ''; // Limpiar el campo de nombre
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

function seleccionarTamaño(boton) {
    // Get all size buttons within the same product
    const producto = boton.closest('.producto');
    const botonesTamaño = producto.querySelectorAll('.tamaño');
    
    // Remove selected class from all buttons in this product
    botonesTamaño.forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Add selected class to clicked button
    boton.classList.add('selected');
}

function buscarProducto() {
    let input = document.getElementById('searchInput');
    let filter = input.value.toLowerCase();
    let productos = document.getElementsByClassName('producto');  // Asume que los productos tienen la clase "producto"
    
    // Iterar sobre los productos y esconder los que no coincidan con la búsqueda
    for (let i = 0; i < productos.length; i++) {
        let producto = productos[i];
        let nombreProducto = producto.getElementsByTagName("h3")[0].innerText.toLowerCase();  // Nombre del producto
        
        if (nombreProducto.indexOf(filter) > -1) {
            producto.style.display = "";  // Mostrar producto si coincide con la búsqueda
        } else {
            producto.style.display = "none";  // Esconder producto si no coincide con la búsqueda
        }
    }
}
