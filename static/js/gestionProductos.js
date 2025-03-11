// Función para abrir el modal de Edición y Agregar Producto
function abrirEAModal(id = null, nombre = '', descripcion = '', precio = 0, stock = 0, 
                      stockMin = 10, stockMax = 100, categoriaId = null, imagen = '') {
    // Rellenar los campos del formulario
    document.getElementById('idProducto').value = id || '';
    document.getElementById('nombreProducto').value = nombre;
    document.getElementById('descripcionProducto').value = descripcion || '';
    document.getElementById('precioProducto').value = precio;
    document.getElementById('stockProducto').value = stock || 0;
    document.getElementById('stockMinProducto').value = stockMin || 10;
    document.getElementById('stockMaxProducto').value = stockMax || 100;
    
    // Esperar a que las categorías se carguen y luego seleccionar la correcta
    setTimeout(() => {
        const categoriaSelect = document.getElementById('categoriaProducto');
        if (categoriaSelect && categoriaSelect.options.length > 0) {
            categoriaSelect.value = categoriaId || '';
        }
        
        // También resetear el selector de tamaño
        const tamanoSelect = document.getElementById('tamanoProducto');
        if (tamanoSelect) {
            tamanoSelect.value = '';
        }
    }, 100);
    
    // Si estamos editando, cargar el tamaño del producto
    if (id) {
        cargarTamanoProducto(id);
    }
    
    // Actualizar el título del modal
    document.getElementById('tituloModal').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    
    // Si estamos editando, mostrar la imagen actual
    if (id && imagen) {
        document.getElementById('imagenActual').src = imagen;
        document.getElementById('imagenActual').style.display = 'block';
        document.getElementById('imagenPreview').style.display = 'none';
    } else {
        document.getElementById('imagenActual').style.display = 'none';
        document.getElementById('imagenPreview').style.display = 'none';
    }

    // Mostrar el modal
    document.getElementById('productoModal').style.display = 'flex';
}

// Función para cargar el tamaño del producto
// Función para cargar el tamaño del producto
function cargarTamanoProducto(productoId) {
    fetch(`/api/productos/variantes/${productoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.variantes && data.variantes.length > 0) {
                // Seleccionar el tamaño del producto
                const tamanoSelect = document.getElementById('tamanoProducto');
                if (tamanoSelect) {
                    // Asegurarse de que el valor sea un string para la comparación
                    const tamanoId = String(data.variantes[0].tamano_id);
                    
                    // Esperar un poco para asegurarse de que las opciones estén cargadas
                    setTimeout(() => {
                        // Verificar si existe la opción con ese valor
                        const optionExists = Array.from(tamanoSelect.options).some(
                            option => option.value === tamanoId
                        );
                        
                        if (optionExists) {
                            tamanoSelect.value = tamanoId;
                            console.log('Tamaño seleccionado:', tamanoId);
                        } else {
                            console.error('No se encontró la opción de tamaño con ID:', tamanoId);
                        }
                    }, 200);
                }
            } else {
                console.log('No se encontraron variantes para el producto');
            }
        })
        .catch(error => {
            console.error('Error al cargar el tamaño del producto:', error);
        });
}

// Función para guardar un producto
function guardarProducto(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('formProducto'));
    
    fetch('/api/productos/guardar', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            window.location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al guardar el producto');
    });
}

// Función para abrir el modal de Ver Producto
function abrirVerProducto(id, nombre, descripcion, precio, stock, stockMin, stockMax, categoria, imagen) {
    // Rellenar los campos del modal
    document.getElementById('verIDProducto').innerText = id;
    document.getElementById('verNombreProducto').innerText = nombre;
    document.getElementById('verDescripcionProducto').innerText = descripcion || 'Sin descripción';
    document.getElementById('verPrecioProducto').innerText = precio;
    document.getElementById('verStockProducto').innerText = stock;
    document.getElementById('verStockMinProducto').innerText = stockMin;
    document.getElementById('verStockMaxProducto').innerText = stockMax;
    document.getElementById('verCategoriaProducto').innerText = categoria;
    
    // Cargar y mostrar el tamaño del producto
    cargarTamanoProductoVer(id);
    
    // Mostrar la imagen
    if (imagen) {
        document.getElementById('verImagenProducto').src = imagen;
        document.getElementById('verImagenProducto').style.display = 'block';
    } else {
        document.getElementById('verImagenProducto').src = '/static/images/default-product.jpg';
        document.getElementById('verImagenProducto').style.display = 'block';
    }
    
    // Mostrar el modal
    document.getElementById('verModalProducto').style.display = 'flex';
}

// Función para cargar y mostrar el tamaño del producto en el modal de Ver
function cargarTamanoProductoVer(productoId) {
    fetch(`/api/productos/variantes/${productoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tamanoElement = document.getElementById('verTamanoProducto');
                if (tamanoElement) {
                    if (data.variantes && data.variantes.length > 0) {
                        tamanoElement.innerText = data.variantes[0].tamano;
                    } else {
                        tamanoElement.innerText = 'No especificado';
                    }
                }
            } else {
                console.error('Error al cargar el tamaño del producto:', data.message);
                document.getElementById('verTamanoProducto').innerText = 'Error al cargar';
            }
        })
        .catch(error => {
            console.error('Error al cargar el tamaño del producto:', error);
            document.getElementById('verTamanoProducto').innerText = 'Error al cargar';
        });
}

// Función para eliminar un producto
function eliminarProducto(id) {
    if (confirm('¿Está seguro de que desea eliminar este producto?')) {
        fetch(`/api/productos/eliminar/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el producto: ' + error.message);
        });
    }
}

// Cerrar el modal de agregar/editar
function cerrarEAModal() {
    document.getElementById('productoModal').style.display = 'none';
}

// Cerrar el modal de ver producto
function cerrarVerProducto() {
    document.getElementById('verModalProducto').style.display = 'none';
}

// Función para mostrar la vista previa de la imagen
function mostrarImagenPreview(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('imagenPreview').src = e.target.result;
            document.getElementById('imagenPreview').style.display = 'block';
            document.getElementById('imagenActual').style.display = 'none';
        }
        reader.readAsDataURL(file);
    }
}
// Función para cargar los tamaños de todos los productos en la tabla
function cargarTamanosProductosTabla() {
    // Obtener todas las celdas de tamaño
    const celdasTamano = document.querySelectorAll('.tamano-producto');
    
    // Para cada celda, cargar el tamaño del producto
    celdasTamano.forEach(celda => {
        const productoId = celda.getAttribute('data-producto-id');
        if (productoId) {
            fetch(`/api/productos/variantes/${productoId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.variantes && data.variantes.length > 0) {
                        // Simplemente mostrar el tamaño en su propia celda
                        celda.textContent = data.variantes[0].tamano;
                    } else {
                        celda.textContent = 'No especificado';
                    }
                })
                .catch(error => {
                    console.error('Error al cargar el tamaño:', error);
                    celda.textContent = 'Error';
                });
        }
    });
}

// Asegurarse de que el modal se muestre correctamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado completamente');
    
    // Verificar que el botón y el modal existen
    const btnAgregar = document.querySelector('.btnAgregarProducto');
    const modal = document.getElementById('productoModal');
    
    if (btnAgregar && modal) {
        console.log('Botón y modal encontrados');
        btnAgregar.addEventListener('click', function() {
            console.log('Botón de agregar producto clickeado');
            abrirEAModal();
        });
    } else {
        console.error('No se encontró el botón o el modal:', {
            btnAgregar: !!btnAgregar,
            modal: !!modal
        });
    }
    
    // Cargar los tamaños de los productos en la tabla
    cargarTamanosProductosTabla();
});

