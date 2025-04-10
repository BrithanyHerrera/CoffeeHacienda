// Función para abrir el modal de Edición y Agregar Producto
function abrirEAModal(id = null, nombre = '', descripcion = '', precio = '', stock = '', 
                     stockMin = '', stockMax = '', categoriaId = null, imagen = '', variantes = []) {
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
    
    // Cargar tamaño si hay variantes
    if (id && variantes.length > 0) {
        document.getElementById('tamanoProducto').value = variantes[0].tamano_id;
    }
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
                        mostrarAlerta('Error al obtener información de la categoría', 'ErrorG'); // Cambiado a mostrarAlerta
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
                mostrarAlerta('Error al obtener los datos del producto', 'ErrorG'); // Cambiado a mostrarAlerta
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al obtener los datos del producto', 'ErrorG'); // Cambiado a mostrarAlerta
        });
}

// Cerrar el modal de ver producto
function cerrarVerProducto() {
    document.getElementById('verModalProducto').style.display = 'none';
}

let idProductoAEliminar = null; // Variable global para almacenar el ID del producto a eliminar

function eliminarProducto(id) {
    idProductoAEliminar = id; // Almacenar el ID del producto a eliminar
    document.getElementById('mensajeConfirmacion').textContent = '¿Estás seguro de que deseas eliminar este producto? Esta acción no puede deshacerse.';
    document.getElementById('confirmacionModal').style.display = 'flex'; // Mostrar el modal de confirmación
}

function confirmarEliminacion() {
    fetch('/api/productos/eliminar', {
        method: 'POST',
        body: JSON.stringify({ id: idProductoAEliminar }),
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta(data.message); // Mostrar mensaje de éxito
            setTimeout(() => {
                location.reload();  // Recargar la página después de 3 segundos
            }, 3000); // Esperar 3 segundos antes de recargar
        } else {
            mostrarAlerta('Error al eliminar el producto: ' + data.message, 'ErrorG'); // Mostrar mensaje de error
        }
    })
    .catch(error => {
        mostrarAlerta('Error al eliminar el producto: ' + error, 'ErrorG'); // Mostrar mensaje de error
    });

    cerrarConfirmacionModal(); // Cerrar el modal de confirmación
}

function cerrarConfirmacionModal() {
    document.getElementById('confirmacionModal').style.display = 'none'; // Ocultar el modal de confirmación
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
            console.error('Error al cargar categorías:', error, 'ErrorG');
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
                console.error('Error al cargar tamaños:', data.message, 'ErrorG');
            }
        })
        .catch(error => {
            console.error('Error al cargar tamaños:', error, 'ErrorG');
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
    const categoriaText = categoriaSelect.options[categoriaSelect.selectedIndex]?.text.trim().toLowerCase();
    
    if (!categoriaId) {
        // Si no hay categoría seleccionada, no hacer nada
        return;
    }
    
    // Verificar si la categoría es "Postre" o "Snack" directamente
    const esInventariable = categoriaText === 'postre' || 
                           categoriaText === 'postres' || 
                           categoriaText === 'snack' || 
                           categoriaText === 'snacks';
    
    if (esInventariable) {
        // Mostrar campos de stock para categorías inventariables
        mostrarOcultarCamposStock(true);
        
        // Buscar el valor de "No Aplica" en las opciones de tamaño
        for (let i = 0; i < tamanoSelect.options.length; i++) {
            if (tamanoSelect.options[i].text === 'No Aplica') {
                tamanoSelect.value = tamanoSelect.options[i].value;
                break;
            }
        }
        return;
    }
    
    // Para otras categorías, obtener información para saber si requiere inventario
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
            console.error('Error al obtener información de la categoría:', error, 'ErrorG');
        });
}

// Función para manejar el cambio de tamaño
function manejarCambioTamano() {
    const categoriaSelect = document.getElementById('categoriaProducto');
    const tamanoSelect = document.getElementById('tamanoProducto');
    const tamanoValue = tamanoSelect.value;
    const tamanoText = tamanoSelect.options[tamanoSelect.selectedIndex]?.text;
    
    console.log("Tamaño seleccionado:", tamanoText); // Para depuración
    
    // Si se selecciona "No Aplica", buscar y seleccionar la categoría "Postre" o "Snack"
    if (tamanoText === 'No Aplica') {
        console.log("Buscando categoría Postre o Snack..."); // Para depuración
        
        // Buscar la categoría "Postre" o "Snack" en las opciones
        let categoriaEncontrada = false;
        for (let i = 0; i < categoriaSelect.options.length; i++) {
            console.log(`Opción ${i}:`, categoriaSelect.options[i].text); // Para depuración
            
            const categoriaTexto = categoriaSelect.options[i].text.trim().toLowerCase();
            if (categoriaTexto === 'postre' || 
                categoriaTexto === 'postres' || 
                categoriaTexto === 'snack' || 
                categoriaTexto === 'snacks') {
                console.log("¡Categoría inventariable encontrada!"); // Para depuración
                categoriaSelect.value = categoriaSelect.options[i].value;
                categoriaEncontrada = true;
                
                // Activar los campos de stock ya que estas categorías requieren inventario
                mostrarOcultarCamposStock(true);
                
                // Disparar el evento change para activar cualquier lógica adicional
                const event = new Event('change');
                categoriaSelect.dispatchEvent(event);
                break;
            }
        }
        
        if (!categoriaEncontrada) {
            console.error("No se encontró una categoría inventariable"); // Para depuración
        }
    } 
    // Si se selecciona un tamaño que no es "No Aplica" y la categoría es "Postre" o "Snack",
    // resetear la categoría
    else if (tamanoText && tamanoText !== 'No Aplica') {
        const categoriaId = categoriaSelect.value;
        const categoriaText = categoriaSelect.options[categoriaSelect.selectedIndex]?.text.trim().toLowerCase();
        
        console.log("Categoría actual:", categoriaText); // Para depuración
        
        if (categoriaText === 'postre' || 
            categoriaText === 'postres' || 
            categoriaText === 'snack' || 
            categoriaText === 'snacks') {
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
    
    const idProducto = document.getElementById('idProducto').value;
    const formData = new FormData(document.getElementById('formProducto'));
    
    // Si es edición, agregar flag para manejar variantes
    if (idProducto) {
        formData.append('es_edicion', 'true');
    }

    fetch('/api/productos/guardar', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta(data.message);
            cerrarEAModal();
            setTimeout(() => location.reload(), 2000);
        } else {
            mostrarAlerta(data.message || 'Error al guardar el producto', 'ErrorG');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar el producto', 'ErrorG');
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
                    
                    // Si hay variantes, seleccionar el tamaño correctamente
                    if (data.variantes && data.variantes.length > 0) {
                        // Seleccionar el tamaño de la primera variante
                        document.getElementById('tamanoProducto').value = data.variantes[0].tamano_id;
                        console.log("Tamaño seleccionado:", data.variantes[0].tamano_id);
                    } else {
                        // Buscar la opción "No Aplica" en el select de tamaños
                        const selectTamano = document.getElementById('tamanoProducto');
                        for (let i = 0; i < selectTamano.options.length; i++) {
                            if (selectTamano.options[i].text === 'No Aplica') {
                                selectTamano.value = selectTamano.options[i].value;
                                console.log("Seleccionando No Aplica:", selectTamano.options[i].value);
                                break;
                            }
                        }
                    }
                    
                    // Mostrar la imagen actual si existe
                    if (producto.ruta_imagen) {
                        document.getElementById('imagenActual').src = producto.ruta_imagen;
                        document.getElementById('imagenActual').style.display = 'block';
                        
                        // Quitar el required del input de imagen cuando ya existe una
                        document.getElementById('imagenProducto').removeAttribute('required');
                    } else {
                        document.getElementById('imagenActual').style.display = 'none';
                    }
                    
                    document.getElementById('tituloModal').innerText = 'Editar Producto';
                } else {
                    mostrarAlerta('Error al obtener los datos del producto', 'ErrorG');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('Error al obtener los datos del producto', 'ErrorG');
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
        
        // Para nuevo producto, la imagen es requerida
        document.getElementById('imagenProducto').setAttribute('required', 'required');
        
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

function mostrarAlerta(mensaje, tipo = 'ExitoG') {
    const contenedor = document.querySelector('.contenedorAlertas') || crearContenedorAlertas();

    const alerta = document.createElement('div');
    alerta.className = `alertaGeneral alerta-${tipo}`;

    // Configurar icono y título según el tipo de alerta
    let icono, titulo;
    if (tipo === 'ErrorG') {
        icono = '⚠️';
        titulo = '¡Atención!';
    } else {
        icono = '✅';
        titulo = '¡Éxito!';
    }

    alerta.innerHTML = `
        <span class="iconoAlertaG">${icono}</span>
        <div class="mensajeAlertaG">
            <h3>${titulo}</h3>
            <p>${mensaje}</p>
        </div>
        <button class="cerrarAlertaG" onclick="this.parentElement.remove()">×</button>
    `;

    contenedor.appendChild(alerta);

    // Aumentar el tiempo de espera a 10 segundos
    setTimeout(() => alerta.remove(), 3000); // Eliminar después de 10s
}


function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
}
