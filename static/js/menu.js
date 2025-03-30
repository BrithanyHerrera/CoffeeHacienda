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
function agregarAlCarrito(nombre, precio, imagen, tamaño, id) {
    const productoExistente = carrito.find(item => item.nombre === nombre && item.tamaño === tamaño);
    
    if (productoExistente) {
        productoExistente.cantidad++;
    } else {
        carrito.push({ 
            nombre, 
            precio, 
            cantidad: 1, 
            imagen, 
            tamaño,
            id // Usar el ID real del producto
        });
    }
    
    actualizarCarrito();
}

// Agregar eventos a los botones "Añadir a la orden"
document.querySelectorAll('.añadirCarrito').forEach(button => {
    button.addEventListener('click', function() {
        const producto = this.parentElement;
        const nombre = producto.querySelector('h3').textContent;
        const imagen = producto.querySelector('img').src;
        const id = parseInt(producto.getAttribute('data-id')); // Obtener el ID real del producto
        
        // Obtener el tamaño seleccionado (si hay varios)
        let tamaño, precio;
        const tamaños = producto.querySelectorAll('.tamaño');
        
        if (tamaños.length > 1) {
            // Si hay múltiples tamaños, seleccionar uno
            const tamaño_seleccionado = prompt(`Seleccione un tamaño para ${nombre}:\n${Array.from(tamaños).map((t, i) => `${i+1}. ${t.textContent.trim()}`).join('\n')}`);
            
            if (!tamaño_seleccionado) return; // Si el usuario cancela
            
            const indice = parseInt(tamaño_seleccionado) - 1;
            if (isNaN(indice) || indice < 0 || indice >= tamaños.length) {
                alert('Selección inválida');
                return;
            }
            
            tamaño = tamaños[indice].textContent.split('-')[0].trim();
            precio = parseFloat(tamaños[indice].getAttribute('preciosDatos'));
        } else if (tamaños.length === 1) {
            // Si solo hay un tamaño, seleccionarlo automáticamente
            tamaño = tamaños[0].textContent.split('-')[0].trim();
            precio = parseFloat(tamaños[0].getAttribute('preciosDatos'));
        } else {
            // Si no hay tamaños definidos, usar valores por defecto
            tamaño = 'Único';
            precio = parseFloat(producto.getAttribute('data-precio') || 0);
        }
        
        agregarAlCarrito(nombre, precio, imagen, tamaño, id);
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

// Modify the realizarPedido function to ensure PDF is only generated on success
function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const numeroMesa = paraLlevar ? '' : document.getElementById('numeroMesa').value.trim();
    const metodoPago = document.querySelector('select[name="metodoPago"]').value;

    if (nombreCliente === '') {
        alert('Por favor, ingrese el nombre del cliente.');
        return;
    }

    if (!paraLlevar && numeroMesa === '') {
        alert('Por favor, ingrese el número de mesa o marque la opción "Para llevar".');
        return;
    }

    if (carrito.length === 0) {
        alert('El carrito está vacío. Agregue productos antes de realizar la orden.');
        return;
    }

    // Preparar los datos para enviar al servidor
    const productos = carrito.map(item => ({
        id: item.id,
        cantidad: item.cantidad,
        precio: item.precio
    }));

    // Calcular el total
    const total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

    // Enviar los datos al servidor
    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            cliente: nombreCliente,
            mesa: numeroMesa,
            productos: productos,
            total: total,
            metodo_pago: obtenerIdMetodoPago(metodoPago)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito
            alert('Venta registrada exitosamente');
            
            // Generar PDF solo si la venta fue exitosa
            generarPDF();
            
            // Vaciar el carrito
            carrito = [];
            actualizarCarrito();
            document.getElementById('nombreCliente').value = '';
        } else {
            // Verificar si hay productos sin stock suficiente
            if (data.productos_sin_stock) {
                let mensaje = "No se puede completar la venta:\n\n";
                data.productos_sin_stock.forEach(p => {
                    mensaje += `- ${p.nombre}: Stock disponible: ${p.stock_actual}, Solicitado: ${p.cantidad_solicitada}\n`;
                });
                alert(mensaje);
            } else {
                // Mostrar mensaje de error
                alert('Error al registrar la venta: ' + data.message);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la venta');
    });
}

// Update the procesarVenta function to also handle PDF generation
// Fix the procesarVenta function to only generate PDF on success
function procesarVenta() {
    if (carrito.length === 0) {
        mostrarNotificacion('El carrito está vacío', 'error');
        return;
    }

    // Obtener datos del formulario
    const cliente = document.getElementById('nombreCliente').value || 'Cliente General';
    const mesa = document.getElementById('numeroMesa').value || '';
    const metodoPago = document.getElementById('metodoPago').value || 1;

    // Preparar datos para enviar
    const datos = {
        cliente: cliente,
        mesa: mesa,
        productos: carrito.map(item => ({
            id: item.id,
            cantidad: item.cantidad,
            precio: item.precio
        })),
        total: calcularTotal(),
        metodo_pago: metodoPago
    };

    // Enviar solicitud al servidor
    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion(data.message, 'success');
            
            // Generar PDF solo si la venta fue exitosa
            generarPDF();
            
            // Limpiar carrito y formulario
            carrito = [];
            actualizarCarritoUI();
            document.getElementById('formularioVenta').reset();
            // Cerrar modal
            document.getElementById('finalizarVentaModal').style.display = 'none';
        } else {
            // Verificar si hay productos sin stock suficiente
            if (data.productos_sin_stock) {
                let mensaje = "No se puede completar la venta:\n\n";
                data.productos_sin_stock.forEach(p => {
                    mensaje += `- ${p.nombre}: Stock disponible: ${p.stock_actual}, Solicitado: ${p.cantidad_solicitada}\n`;
                });
                mostrarNotificacion(mensaje, 'error', 10000); // Mostrar por más tiempo
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la venta', 'error');
    });
}

// Add a helper function to calculate total if it doesn't exist
function calcularTotal() {
    return carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
}

// Eliminar la función obtenerIdProducto ya que no la necesitamos más
// function obtenerIdProducto(nombre, tamaño) { ... }

// Función para obtener el ID del método de pago
function obtenerIdMetodoPago(metodoPago) {
    switch(metodoPago) {
        case 'efectivo':
            return 1;
        case 'tarjeta':
            return 2;
        case 'transferencia':
            return 3;
        default:
            return 1;
    }
}

// Función para eliminar un producto del carrito
function eliminarDelCarrito(nombre, tamaño) {
    carrito = carrito.filter(item => !(item.nombre === nombre && item.tamaño === tamaño));
    actualizarCarrito();
}

function actualizarCarrito() {
    const carritoItems = document.querySelector('.carritoItems');
    carritoItems.innerHTML = '';

    let total = 0;
    carrito.forEach((item, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('carritoItem');

        itemDiv.innerHTML = `
            <img src="${item.imagen}" alt="${item.nombre}">
            <div>
                <h4>${item.nombre} (${item.tamaño})</h4>
                <p>Precio: $${item.precio}</p>
                <p>Total: $<span class="total-item">${item.precio * item.cantidad}</span></p>
            </div>
            <input type="number" class="cantidadProducto" data-index="${index}" value="${item.cantidad}" min="1">
            <button class="eliminarItemCarrito" data-index="${index}">X</button>
        `;

        carritoItems.appendChild(itemDiv);
        total += item.precio * item.cantidad;
    });

    document.getElementById('total').textContent = `$${total}`;

    // Agregar evento a los botones de eliminar
    document.querySelectorAll('.eliminarItemCarrito').forEach(button => {
        button.addEventListener('click', function() {
            const index = this.getAttribute('data-index');
            carrito.splice(index, 1);
            actualizarCarrito();
        });
    });

    // Agregar evento a los inputs de cantidad
    document.querySelectorAll('.cantidadProducto').forEach(input => {
        input.addEventListener('change', function() {
            const index = this.getAttribute('data-index');
            let nuevaCantidad = parseInt(this.value);

            // Evitar que la cantidad sea menor a 1
            if (nuevaCantidad < 1 || isNaN(nuevaCantidad)) {
                nuevaCantidad = 1;
                this.value = 1;
            }

            carrito[index].cantidad = nuevaCantidad;
            actualizarCarrito();
        });
    });
}

function generarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    if (!doc.autoTable) {
        console.error("autoTable no está cargado correctamente.");
        alert("Error al generar el PDF. Asegúrate de incluir la librería jsPDF.");
        return;
    }

    const margenIzquierdo = 10;
    let posicionY = 10;

    // Obtener información del pedido
    const fechaHora = new Date().toLocaleString();
    const nombreCliente = document.getElementById('nombreCliente').value.trim() || "No especificado";
    const direccionSucursal = "Calle Ejemplo 123, Ciudad";
    const nombreVendedor = "Administrador"; // Puedes cambiar esto si el vendedor varía

    // Configurar fuente compatible
    doc.setFont("times", "normal");

    // Título
    doc.setFontSize(16);
    doc.text("RECIBO DE COMPRA", 105, posicionY, { align: "center" });
    posicionY += 10;

    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Datos del pedido
    doc.setFontSize(12);
    doc.text(`Fecha y Hora: ${fechaHora}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Nombre del Vendedor: ${nombreVendedor}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Dirección: ${direccionSucursal}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Cliente: ${nombreCliente}`, margenIzquierdo, posicionY);
    posicionY += 10;

    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Listar productos comprados
    doc.setFont("times", "bold");
    doc.text("Artículos Comprados:", margenIzquierdo, posicionY);
    posicionY += 8;
    doc.setFont("times", "normal");

    let columnas = ["Producto", "Tamaño", "Cantidad", "Precio", "Subtotal"];
    let filas = [];

    // Obtener productos del carrito
    let total = 0;
    carrito.forEach(item => {
        let subtotal = item.precio * item.cantidad;
        total += subtotal;
        filas.push([
            item.nombre,
            item.tamaño,
            item.cantidad,
            `$${item.precio.toFixed(2)}`,
            `$${subtotal.toFixed(2)}`
        ]);
    });

    // Si no hay productos en el carrito, mostrar mensaje
    if (filas.length === 0) {
        filas.push(["No hay productos en la orden", "", "", "", ""]);
    }

    doc.autoTable({
        startY: posicionY,
        head: [columnas],
        body: filas,
        theme: "striped",
        styles: { fontSize: 10, cellPadding: 3 },
        headStyles: { fillColor: [0, 0, 0], textColor: [255, 255, 255] }
    });

    // Posicionar el total después de la tabla
    posicionY = doc.lastAutoTable.finalY + 10;

    doc.setFont("times", "bold");
    doc.text(`TOTAL: $${total.toFixed(2)}`, margenIzquierdo, posicionY);

    // Guardar el PDF
    doc.save(`Recibo_${nombreCliente}.pdf`);
}

// Agregar esta función para manejar la respuesta cuando no hay suficiente stock
function procesarVenta() {
    if (carrito.length === 0) {
        mostrarNotificacion('El carrito está vacío', 'error');
        return;
    }

    // Obtener datos del formulario
    const cliente = document.getElementById('nombreCliente').value || 'Cliente General';
    const mesa = document.getElementById('numeroMesa').value || '';
    const metodoPago = document.getElementById('metodoPago').value || 1;

    // Preparar datos para enviar
    const datos = {
        cliente: cliente,
        mesa: mesa,
        productos: carrito,
        total: calcularTotal(),
        metodo_pago: metodoPago
    };

    // Enviar solicitud al servidor
    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion(data.message, 'success');
            // Limpiar carrito y formulario
            carrito = [];
            actualizarCarritoUI();
            document.getElementById('formularioVenta').reset();
            // Cerrar modal
            document.getElementById('finalizarVentaModal').style.display = 'none';
        } else {
            // Verificar si hay productos sin stock suficiente
            if (data.productos_sin_stock) {
                let mensaje = "No se puede completar la venta:\n\n";
                data.productos_sin_stock.forEach(p => {
                    mensaje += `- ${p.nombre}: Stock disponible: ${p.stock_actual}, Solicitado: ${p.cantidad_solicitada}\n`;
                });
                mostrarNotificacion(mensaje, 'error', 10000); // Mostrar por más tiempo
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la venta', 'error');
    });
}

// Función para mostrar notificaciones con duración personalizable
function mostrarNotificacion(mensaje, tipo, duracion = 3000) {
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion ${tipo}`;
    notificacion.textContent = mensaje;
    
    document.body.appendChild(notificacion);
    
    // Mostrar la notificación
    setTimeout(() => {
        notificacion.classList.add('mostrar');
    }, 10);
    
    // Ocultar y eliminar después de la duración especificada
    setTimeout(() => {
        notificacion.classList.remove('mostrar');
        setTimeout(() => {
            document.body.removeChild(notificacion);
        }, 300);
    }, duracion);
}

// Función para mostrar/ocultar el campo de número de mesa
function toggleMesaField() {
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const mesaContainer = document.getElementById('mesaContainer');
    
    if (paraLlevar) {
        mesaContainer.style.display = 'none';
        document.getElementById('numeroMesa').value = ''; // Limpiar el valor
    } else {
        mesaContainer.style.display = 'block';
    }
}

// Asegurarse de que la función se ejecute cuando la página cargue
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar estilos al contenedor del checkbox
    const opcionLlevar = document.querySelector('.opcionLlevar');
    if (opcionLlevar) {
        opcionLlevar.style.display = 'flex';
        opcionLlevar.style.alignItems = 'center';
        opcionLlevar.style.marginBottom = '15px';
        opcionLlevar.style.marginTop = '5px';
    }
    
    // Estilizar el checkbox y su etiqueta
    const checkboxParaLlevar = document.getElementById('paraLlevar');
    if (checkboxParaLlevar) {
        checkboxParaLlevar.style.marginRight = '8px';
        
        // Ejecutar la función una vez al cargar para establecer el estado inicial
        toggleMesaField();
        
        // Agregar el evento change si no se agregó mediante el atributo HTML
        if (!checkboxParaLlevar.hasAttribute('onchange')) {
            checkboxParaLlevar.addEventListener('change', toggleMesaField);
        }
    }
});


