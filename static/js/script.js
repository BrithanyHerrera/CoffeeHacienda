//Funcion para abrir el modal de Edición y Agregar producto.
function abrirEAModal(id = null, nombre = '', precio = '') {
    document.getElementById('productoId').value = id;
    document.getElementById('productoNombre').value = nombre;
    document.getElementById('productoPrecio').value = precio;
    document.getElementById('modalTitulo').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    document.getElementById('productoModal').style.display = 'flex';
}

function cerrarEAModal() {
    document.getElementById('productoModal').style.display = 'none';
}

document.getElementById('productoForm').addEventListener('submit', function(event) {
    event.preventDefault();
    closeModal();
});

function abrirVerProducto(id, nombre, precio, imagen) {
    // Establecer el contenido en el modal de ver producto
    document.getElementById('verProductoID').textContent = id;
    document.getElementById('verProductoNombre').textContent = nombre;
    document.getElementById('verProductoPrecio').textContent = precio;
    document.getElementById('verProductoImagen').src = imagen;
    
    // Mostrar el modal de ver producto
    document.getElementById('verProductoModal').style.display = 'flex';
}

function cerrarVerProducto() {
    // Cerrar el modal de ver producto
    document.getElementById('verProductoModal').style.display = 'none';
}

