// Función para abrir el modal de Edición y Agregar producto.
function abrirEAModal(id = null, nombre = '', precio = '') {
    // Verifica que los valores sean correctos
    console.log('Abrir modal con los siguientes datos:', id, nombre, precio);

    // Rellenar los campos del modal con los valores recibidos
    document.getElementById('idProducto').value = id;
    document.getElementById('nombreProducto').value = nombre;
    document.getElementById('precioProducto').value = precio;


    // Establecer el título del modal dependiendo si es agregar o editar
    document.getElementById('tituloModal').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    
    // Mostrar el modal de agregar/editar producto
    document.getElementById('productoModal').style.display = 'flex';
}

// Cerrar el modal de edición/agregar
function cerrarEAModal() {
    document.getElementById('productoModal').style.display = 'none';
}

// Evitar el comportamiento por defecto del formulario y cerrar el modal.
document.getElementById('formProducto').addEventListener('submit', function(event) {
    event.preventDefault();
    cerrarEAModal(); // Cambié 'closeModal()' a 'cerrarEAModal()'
});

// Función para abrir el modal de ver producto.
function abrirVerProducto(id, nombre, precio, imagen) {
    // Establecer el contenido en el modal de ver producto
    document.getElementById('verIDProducto').textContent = id;
    document.getElementById('verNombreProducto').textContent = nombre;
    document.getElementById('verPrecioProducto').textContent = precio;
    document.getElementById('verImagenProducto').src = imagen;
    
    // Mostrar el modal de ver producto
    document.getElementById('verModalProducto').style.display = 'flex';
}

// Cerrar el modal de ver producto
function cerrarVerProducto() {
    document.getElementById('verModalProducto').style.display = 'none';
}
