// Función para abrir el modal de Edición y Agregar Producto
function abrirEAModal(id = null, nombre = '', precio = 0, imagen = '') {
    document.getElementById('idProducto').value = id || '';
    document.getElementById('nombreProducto').value = nombre;
    document.getElementById('precioProducto').value = precio;
    document.getElementById('tituloModal').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    
    // Si estamos editando, deshabilitar la imagen
    if (id) {
        document.getElementById('imagenProducto').disabled = true;
        document.getElementById('imagenActual').src = imagen;  // Mostrar la imagen actual
    } else {
        document.getElementById('imagenProducto').disabled = false;
    }

    document.getElementById('productoModal').style.display = 'flex';
}


// Cerrar el modal de agregar/editar
function cerrarEAModal() {
    document.getElementById('productoModal').style.display = 'none';
    document.getElementById('formProducto').reset();
}

function abrirVerProducto(id, nombre, precio, imagen) {
    document.getElementById('verIDProducto').innerText = id;
    document.getElementById('verNombreProducto').innerText = nombre;
    document.getElementById('verPrecioProducto').innerText = precio;
    document.getElementById('verImagenProducto').src = imagen || 'ruta/default/image.jpg';  // Si no hay imagen, usar una imagen predeterminada
    
    document.getElementById('verModalProducto').style.display = 'flex';
}


// Cerrar el modal de ver producto
function cerrarVerProducto() {
    document.getElementById('verModalProducto').style.display = 'none';
}

function eliminarProducto(id) {
    const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este producto? Esta acción no puede deshacerse.');
    if (confirmDelete) {
        fetch('/api/productos/eliminar', {
            method: 'POST',
            body: JSON.stringify({ id: id }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();  // Recargar la página para actualizar la lista de productos
            } else {
                alert('Error al eliminar el producto: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error al eliminar el producto: ' + error);
        });
    }
}

function guardarProducto(event) {
    event.preventDefault();  // Prevenir el envío del formulario

    // Obtener los valores de los campos
    const nombreProducto = document.getElementById('nombreProducto').value;
    const precioProducto = document.getElementById('precioProducto').value;

    // Verificar si los campos obligatorios están vacíos
    if (!nombreProducto || !precioProducto) {
        alert("Por favor, complete todos los campos requeridos.");
        return;  // Evita el envío del formulario
    }

    // Si todo está correcto, se crea un objeto FormData
    const formData = new FormData(document.getElementById('formProducto'));

    // Realizamos la solicitud con fetch
    fetch('/api/productos/guardar', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();  // Recargar la página para actualizar la lista de productos
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        alert('Error al guardar el producto: ' + error);
    });
}

