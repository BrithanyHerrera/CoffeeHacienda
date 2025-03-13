// Función para abrir el modal de Edición y Agregar Producto
function abrirEAModal(id = null, nombre = '', descripcion = '', precio = 0, stock = 0, 
                      stockMin = 10, stockMax = 100, categoriaId = null, imagen = '') {
    document.getElementById('idProducto').value = id || '';
    document.getElementById('nombreProducto').value = nombre;
    document.getElementById('descripcionProducto').value = descripcion || '';
    document.getElementById('precioProducto').value = precio;
    document.getElementById('stockProducto').value = stock || 0;
    document.getElementById('stockMinProducto').value = stockMin || 10;
    document.getElementById('stockMaxProducto').value = stockMax || 100;
    document.getElementById('categoriaProducto').value = categoriaId || '';
    document.getElementById('tituloModal').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    
    // Si estamos editando, mostrar la imagen actual
    if (id) {
        document.getElementById('imagenActual').src = imagen;
        document.getElementById('imagenActual').style.display = 'block';
    } else {
        document.getElementById('imagenActual').style.display = 'none';
    }

    document.getElementById('productoModal').style.display = 'flex';
}


// Cerrar el modal de agregar/editar
function cerrarEAModal() {
    document.getElementById('productoModal').style.display = 'none';
    document.getElementById('formProducto').reset();
    document.getElementById('imagenActual').style.display = 'none';
}

function abrirVerProducto(id, nombre, descripcion, precio, stock, stockMin, stockMax, categoria, imagen) {
    document.getElementById('verIDProducto').innerText = id;
    document.getElementById('verNombreProducto').innerText = nombre;
    document.getElementById('verDescripcionProducto').innerText = descripcion || 'Sin descripción';
    document.getElementById('verPrecioProducto').innerText = precio;
    document.getElementById('verStockProducto').innerText = stock || 0;
    document.getElementById('verStockMinProducto').innerText = stockMin || 10;
    document.getElementById('verStockMaxProducto').innerText = stockMax || 100;
    document.getElementById('verCategoriaProducto').innerText = categoria || 'Sin categoría';
    document.getElementById('verImagenProducto').src = imagen || '/static/images/default-product.jpg';
    
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

// Función para cargar las categorías en el select
function cargarCategorias() {
    fetch('/api/categorias')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const selectCategoria = document.getElementById('categoriaProducto');
                // Limpiar opciones existentes
                selectCategoria.innerHTML = '<option value="">Seleccione una categoría</option>';
                
                // Agregar las categorías
                data.categorias.forEach(categoria => {
                    const option = document.createElement('option');
                    option.value = categoria.Id;
                    option.textContent = categoria.categoria;
                    selectCategoria.appendChild(option);
                });
            } else {
                console.error('Error al cargar categorías:', data.message);
            }
        })
        .catch(error => {
            console.error('Error al cargar categorías:', error);
        });
}

// Función para cargar los tamaños en el select
function cargarTamanos() {
    fetch('/api/tamanos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const selectTamano = document.getElementById('tamanoProducto');
                // Limpiar opciones existentes
                selectTamano.innerHTML = '<option value="">Seleccione un tamaño</option>';
                
                // Agregar los tamaños
                data.tamanos.forEach(tamano => {
                    const option = document.createElement('option');
                    option.value = tamano.Id;
                    option.textContent = tamano.tamano;
                    selectTamano.appendChild(option);
                });
            } else {
                console.error('Error al cargar tamaños:', data.message);
            }
        })
        .catch(error => {
            console.error('Error al cargar tamaños:', error);
        });
}

// Cargar categorías y tamaños cuando se carga la página
// Ensure this code is in your DOMContentLoaded event handler
document.addEventListener('DOMContentLoaded', function() {
    cargarCategorias();
    cargarTamanos();
    
    // Add event listener for the form
    const formProducto = document.getElementById('formProducto');
    if (formProducto) {
        formProducto.addEventListener('submit', function(event) {
            event.preventDefault();
            guardarProducto(event);
        });
    }
});

// Función para guardar el producto
function guardarProducto(event) {
    event.preventDefault();
    
    // Obtener los valores de los campos
    const nombreProducto = document.getElementById('nombreProducto').value;
    const precioProducto = document.getElementById('precioProducto').value;
    const stockProducto = document.getElementById('stockProducto').value;
    const categoriaProducto = document.getElementById('categoriaProducto').value;

    // Verificar si los campos obligatorios están vacíos
    if (!nombreProducto || !precioProducto || !stockProducto || !categoriaProducto) {
        alert("Por favor, complete todos los campos requeridos.");
        return;  // Evita el envío del formulario
    }

    // Validar que el stock esté dentro de los límites
    const stockMin = parseInt(document.getElementById('stockMinProducto').value);
    const stockMax = parseInt(document.getElementById('stockMaxProducto').value);
    const stock = parseInt(stockProducto);
    
    if (stockMin > stockMax) {
        alert("El stock mínimo no puede ser mayor que el stock máximo.");
        return;
    }

    // Si todo está correcto, se crea un objeto FormData
    const formData = new FormData(document.getElementById('formProducto'));
    
    // Asegurarse de que los nombres de los campos coincidan con lo que espera el servidor
    formData.set('nombreProducto', nombreProducto);
    formData.set('descripcionProducto', document.getElementById('descripcionProducto').value);
    formData.set('precioProducto', precioProducto);
    formData.set('stockProducto', stockProducto);
    formData.set('stockMinProducto', stockMin);
    formData.set('stockMaxProducto', stockMax);
    formData.set('categoriaProducto', categoriaProducto);
    formData.set('tamanoProducto', document.getElementById('tamanoProducto').value);

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

