// Función para abrir el modal de Edición y Agregar Producto
function abrirEAModal(id = null, nombre = '', descripcion = '', precio = '', stock = '', 
                      stockMin = '', stockMax = '', categoriaId = null, imagen = '') {
    document.getElementById('idProducto').value = id || '';
    document.getElementById('nombreProducto').value = nombre;
    document.getElementById('descripcionProducto').value = descripcion || '';
    document.getElementById('precioProducto').value = precio;
    document.getElementById('stockProducto').value = stock || '';
    document.getElementById('stockMinProducto').value = stockMin || '';
    document.getElementById('stockMaxProducto').value = stockMax || '';
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

function abrirVerProducto(id) {
    // Obtener los datos completos del producto incluyendo tamaño y categoría
    fetch(`/api/productos/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const producto = data.producto;
                
                // Establecer el contenido en el modal de ver producto
                document.getElementById('verIDProducto').textContent = producto.Id;
                document.getElementById('verNombreProducto').textContent = producto.nombre_producto;
                document.getElementById('verDescripcionProducto').textContent = producto.descripcion || 'Sin descripción';
                document.getElementById('verPrecioProducto').textContent = producto.precio;
                
                // Verificar si la categoría requiere inventario
                fetch(`/api/categorias/${producto.categoria_id}`)
                    .then(response => response.json())
                    .then(catData => {
                        if (catData.success) {
                            const requiereInventario = catData.categoria.requiere_inventario;
                            
                            // Mostrar valores de stock según si requiere inventario
                            if (requiereInventario) {
                                document.getElementById('verStockProducto').textContent = producto.stock || '0';
                                document.getElementById('verStockMinProducto').textContent = producto.stock_minimo || '0';
                                document.getElementById('verStockMaxProducto').textContent = producto.stock_maximo || '0';
                                
                                // Mostrar las etiquetas de stock
                                document.getElementById('verStockLabel').style.display = 'block';
                                document.getElementById('verStockMinLabel').style.display = 'block';
                                document.getElementById('verStockMaxLabel').style.display = 'block';
                                document.getElementById('verStockProducto').style.display = 'inline';
                                document.getElementById('verStockMinProducto').style.display = 'inline';
                                document.getElementById('verStockMaxProducto').style.display = 'inline';
                            } else {
                                // Ocultar las etiquetas y valores de stock
                                document.getElementById('verStockLabel').style.display = 'none';
                                document.getElementById('verStockMinLabel').style.display = 'none';
                                document.getElementById('verStockMaxLabel').style.display = 'none';
                                document.getElementById('verStockProducto').style.display = 'none';
                                document.getElementById('verStockMinProducto').style.display = 'none';
                                document.getElementById('verStockMaxProducto').style.display = 'none';
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error al obtener información de la categoría:', error);
                    });
                
                document.getElementById('verCategoriaProducto').textContent = producto.categoria || 'Sin categoría';
                
                // Mostrar el tamaño si hay variantes
                if (data.variantes && data.variantes.length > 0) {
                    const tamanos = data.variantes.map(v => v.tamano).join(', ');
                    document.getElementById('verTamanoProducto').textContent = tamanos;
                } else {
                    document.getElementById('verTamanoProducto').textContent = 'Sin tamaño';
                }
                
                // Mostrar la imagen
                document.getElementById('verImagenProducto').src = producto.ruta_imagen || '/static/images/default-product.jpg';
                
                // Mostrar el modal de ver producto
                document.getElementById('verModalProducto').style.display = 'flex';
            } else {
                alert('Error al obtener los datos del producto');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al obtener los datos del producto');
        });
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
    
    // Agregar event listeners para los cambios en categoría y tamaño
    const categoriaSelect = document.getElementById('categoriaProducto');
    const tamanoSelect = document.getElementById('tamanoProducto');
    
    if (categoriaSelect) {
        categoriaSelect.addEventListener('change', function() {
            manejarCambioCategoria();
        });
    }
    
    if (tamanoSelect) {
        tamanoSelect.addEventListener('change', function() {
            manejarCambioTamano();
        });
    }
});

// Función para manejar el cambio de categoría
function manejarCambioCategoria() {
    const categoriaSelect = document.getElementById('categoriaProducto');
    const tamanoSelect = document.getElementById('tamanoProducto');
    const categoriaId = categoriaSelect.value;
    
    if (!categoriaId) {
        // Si no hay categoría seleccionada, no hacer nada
        return;
    }
    
    // Obtener información de la categoría para saber si requiere inventario
    fetch(`/api/categorias/${categoriaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const requiereInventario = data.categoria.requiere_inventario;
                
                // Mostrar u ocultar campos de stock según requiera inventario
                mostrarOcultarCamposStock(requiereInventario);
                
                // Si requiere inventario, seleccionar automáticamente "No Aplica" como tamaño
                if (requiereInventario) {
                    // Buscar el valor de "No Aplica" en las opciones
                    for (let i = 0; i < tamanoSelect.options.length; i++) {
                        if (tamanoSelect.options[i].text === 'No Aplica') {
                            tamanoSelect.value = tamanoSelect.options[i].value;
                            break;
                        }
                    }
                } else {
                    // Si no requiere inventario y el tamaño es "No Aplica", resetear el tamaño
                    for (let i = 0; i < tamanoSelect.options.length; i++) {
                        if (tamanoSelect.options[i].text === 'No Aplica' && tamanoSelect.value === tamanoSelect.options[i].value) {
                            tamanoSelect.value = '';
                            break;
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error al obtener información de la categoría:', error);
        });
}

// Función para manejar el cambio de tamaño
function manejarCambioTamano() {
    const categoriaSelect = document.getElementById('categoriaProducto');
    const tamanoSelect = document.getElementById('tamanoProducto');
    const tamanoValue = tamanoSelect.value;
    const tamanoText = tamanoSelect.options[tamanoSelect.selectedIndex]?.text;
    
    console.log("Tamaño seleccionado:", tamanoText); // Para depuración
    
    // Si se selecciona "No Aplica", buscar y seleccionar la categoría "Postre"
    if (tamanoText === 'No Aplica') {
        console.log("Buscando categoría Postre..."); // Para depuración
        
        // Buscar la categoría "Postre" en las opciones
        let postreEncontrado = false;
        for (let i = 0; i < categoriaSelect.options.length; i++) {
            console.log(`Opción ${i}:`, categoriaSelect.options[i].text); // Para depuración
            
            if (categoriaSelect.options[i].text.trim() === 'Postre' || 
                categoriaSelect.options[i].text.trim() === 'Postres') {
                console.log("¡Categoría Postre encontrada!"); // Para depuración
                categoriaSelect.value = categoriaSelect.options[i].value;
                postreEncontrado = true;
                
                // Activar los campos de stock ya que Postre requiere inventario
                mostrarOcultarCamposStock(true);
                
                // Disparar el evento change para activar cualquier lógica adicional
                const event = new Event('change');
                categoriaSelect.dispatchEvent(event);
                break;
            }
        }
        
        if (!postreEncontrado) {
            console.error("No se encontró la categoría Postre"); // Para depuración
        }
    } 
    // Si se selecciona un tamaño que no es "No Aplica" y la categoría es "Postre",
    // resetear la categoría
    else if (tamanoText && tamanoText !== 'No Aplica') {
        const categoriaId = categoriaSelect.value;
        const categoriaText = categoriaSelect.options[categoriaSelect.selectedIndex]?.text;
        
        console.log("Categoría actual:", categoriaText); // Para depuración
        
        if (categoriaText === 'Postre' || categoriaText === 'Postres') {
            console.log("Reseteando categoría porque se cambió de No Aplica"); // Para depuración
            categoriaSelect.value = '';
            mostrarOcultarCamposStock(false);
        }
    }
}

// Función para mostrar u ocultar campos de stock
function mostrarOcultarCamposStock(mostrar) {
    const stockFields = [
        document.querySelector('label[for="stockProducto"]'),
        document.getElementById('stockProducto'),
        document.querySelector('label[for="stockMinProducto"]'),
        document.getElementById('stockMinProducto'),
        document.querySelector('label[for="stockMaxProducto"]'),
        document.getElementById('stockMaxProducto')
    ];
    
    stockFields.forEach(field => {
        if (field) {
            field.style.display = mostrar ? 'block' : 'none';
        }
    });
    
    // Si no se requiere inventario, establecer valores predeterminados
    if (!mostrar) {
        document.getElementById('stockProducto').value = '0';
        document.getElementById('stockMinProducto').value = '0';
        document.getElementById('stockMaxProducto').value = '0';
    }
}

// Función para guardar el producto
function guardarProducto(event) {
    event.preventDefault();
    
    // Obtener los valores de los campos
    const nombreProducto = document.getElementById('nombreProducto').value;
    const precioProducto = document.getElementById('precioProducto').value;
    const stockProducto = document.getElementById('stockProducto').value;
    const categoriaProducto = document.getElementById('categoriaProducto').value;
    const idProducto = document.getElementById('idProducto').value;

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

    // Verificar si se está editando y no se seleccionó una nueva imagen
    const imagenInput = document.getElementById('imagenProducto');
    if (idProducto && (!imagenInput.files || !imagenInput.files[0]) && document.getElementById('imagenActual').style.display !== 'none') {
        // Si estamos editando y no se seleccionó una nueva imagen, no es necesario validar el campo de imagen
        imagenInput.required = false;
    } else if (!idProducto) {
        // Si es un nuevo producto, la imagen es requerida
        imagenInput.required = true;
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

// Función para filtrar productos
function filtrarProductos() {
    // Obtener valores de los filtros
    const nombre = document.getElementById('buscarNombre').value.toLowerCase();
    const tamano = document.getElementById('buscarTamano').value;
    const categoria = document.getElementById('buscarCategoria').value;

    // Obtener la lista de productos
    const productos = document.querySelectorAll('#productosLista tr');

    // Recorrer todos los productos
    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const tamanoProducto = producto.querySelector('.tamanoProducto').textContent.trim();
        const categoriaProducto = producto.querySelector('.categoriaProducto').textContent.trim();

        // Verificar si el producto coincide con los filtros
        const coincideNombre = !nombre || nombreProducto.includes(nombre);
        const coincideTamano = !tamano || tamanoProducto === tamano;
        const coincideCategoria = !categoria || categoriaProducto === categoria;

        // Mostrar u ocultar el producto según los filtros
        if (coincideNombre && coincideTamano && coincideCategoria) {
            producto.style.display = ''; // Mostrar
        } else {
            producto.style.display = 'none'; // Ocultar
        }
    });
}

// Función para restablecer los filtros
function reestablecerFiltros() {
    // Limpiar valores de los filtros
    document.getElementById('buscarNombre').value = '';
    document.getElementById('buscarTamano').value = '';
    document.getElementById('buscarCategoria').value = '';

    // Mostrar todos los productos
    const productos = document.querySelectorAll('#productosLista tr');
    productos.forEach(producto => {
        producto.style.display = ''; // Mostrar todos
    });
}

function abrirEAModal(id = null) {
    if (id) {
        // Si es edición, obtener los datos completos del producto
        fetch(`/api/productos/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const producto = data.producto;
                    
                    // Rellenar los campos del modal con los valores recibidos
                    document.getElementById('idProducto').value = producto.Id;
                    document.getElementById('nombreProducto').value = producto.nombre_producto;
                    document.getElementById('descripcionProducto').value = producto.descripcion || '';
                    document.getElementById('precioProducto').value = producto.precio;
                    document.getElementById('stockProducto').value = producto.stock || '';
                    document.getElementById('stockMinProducto').value = producto.stock_minimo || '';
                    document.getElementById('stockMaxProducto').value = producto.stock_maximo || '';
                    
                    // Asegurarse de seleccionar la categoría correcta
                    if (producto.categoria_id) {
                        document.getElementById('categoriaProducto').value = producto.categoria_id;
                        
                        // Verificar si la categoría requiere inventario
                        fetch(`/api/categorias/${producto.categoria_id}`)
                            .then(response => response.json())
                            .then(catData => {
                                if (catData.success) {
                                    mostrarOcultarCamposStock(catData.categoria.requiere_inventario);
                                }
                            });
                    }
                    
                    // Si hay variantes, seleccionar el tamaño
                    if (data.variantes && data.variantes.length > 0) {
                        document.getElementById('tamanoProducto').value = data.variantes[0].tamano_id;
                    }
                    
                    // Mostrar la imagen actual si existe
                    if (producto.ruta_imagen) {
                        document.getElementById('imagenActual').src = producto.ruta_imagen;
                        document.getElementById('imagenActual').style.display = 'block';
                    } else {
                        document.getElementById('imagenActual').style.display = 'none';
                    }
                    
                    document.getElementById('tituloModal').innerText = 'Editar Producto';
                } else {
                    alert('Error al obtener los datos del producto');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al obtener los datos del producto');
            });
    } else {
        // Si es un nuevo producto, limpiar el formulario
        document.getElementById('idProducto').value = '';
        document.getElementById('nombreProducto').value = '';
        document.getElementById('descripcionProducto').value = '';
        document.getElementById('precioProducto').value = '';
        document.getElementById('stockProducto').value = '';
        document.getElementById('stockMinProducto').value = '';
        document.getElementById('stockMaxProducto').value = '';
        document.getElementById('categoriaProducto').value = '';
        document.getElementById('tamanoProducto').value = '';
        document.getElementById('imagenActual').style.display = 'none';
        document.getElementById('tituloModal').innerText = 'Agregar Producto';
        
        // Por defecto, ocultar los campos de stock
        mostrarOcultarCamposStock(false);
    }
    
    document.getElementById('productoModal').style.display = 'flex';
}

document.addEventListener("DOMContentLoaded", function () {
    const numericFields = [
        "precioProducto",
        "stockProducto",
        "stockMinProducto",
        "stockMaxProducto",
    ];

    numericFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        field.addEventListener("input", function () {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});

// Agregar event listeners para limpiar el valor "0" al hacer clic
document.addEventListener('DOMContentLoaded', function() {
    const stockInputs = [
        document.getElementById('stockProducto'),
        document.getElementById('stockMinProducto'),
        document.getElementById('stockMaxProducto')
    ];
    
    stockInputs.forEach(input => {
        if (input) {
            input.addEventListener('focus', function() {
                if (this.value === '0') {
                    this.value = '';
                }
            });
            
            // Restaurar el valor "0" si el campo queda vacío al perder el foco
            input.addEventListener('blur', function() {
                if (this.value === '') {
                    this.value = '0';
                }
            });
        }
    });
});


