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

    setTimeout(() => alerta.remove(), 5000); // Eliminar después de 5s
}


function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
}

function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const numeroMesa = paraLlevar ? '' : document.getElementById('numeroMesa').value.trim();
    const metodoPago = document.querySelector('select[name="metodoPago"]').value;
    const dineroRecibido = parseFloat(document.getElementById('inputDineroRecibido').value) || 0;
    const total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

    // Validaciones básicas
    if (nombreCliente === '') {
        mostrarAlerta('Por favor, ingrese el nombre del cliente.', 'ErrorG');
        return;
    }

    if (!paraLlevar && numeroMesa === '') {
        mostrarAlerta('Ingrese el número de mesa o marque "Para llevar".', 'ErrorG');
        return;
    }

    if (carrito.length === 0) {
        mostrarAlerta('El carrito está vacío. Agregue productos antes de realizar la orden.', 'ErrorG');
        return;
    }

    // Validación de dinero recibido SOLO para pagos en efectivo
    if (metodoPago.toLowerCase() === 'efectivo' && dineroRecibido < total) {
        mostrarAlerta('El monto recibido es menor al total de la compra. No se puede realizar la venta.', 'ErrorG');
        return;
    }

    const productos = carrito.map(item => ({
        id: item.id,
        cantidad: item.cantidad,
        precio: item.precio
    }));

    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
            mostrarAlerta('Venta registrada exitosamente.', 'ExitoG');
            generarPDF();
            carrito = [];
            actualizarCarrito();
            // Limpiar todos los campos del formulario
            document.getElementById('nombreCliente').value = '';
            document.getElementById('numeroMesa').value = '';
            document.getElementById('inputDineroRecibido').value = '';
            document.getElementById('inputCambio').value = '0';
            document.getElementById('metodoPago').selectedIndex = 0;
            document.getElementById('paraLlevar').checked = false;
            toggleMesaField(); // Para ocultar el campo de mesa si es necesario
        } else {
            if (data.productos_sin_stock) {
                let mensaje = "Stock insuficiente:\n";
                data.productos_sin_stock.forEach(p => {
                    mensaje += `- ${p.nombre} (Disponible: ${p.stock_actual}, Solicitado: ${p.cantidad_solicitada})\n`;
                });
                mostrarAlerta(mensaje, 'ErrorG');
            } else {
                mostrarAlerta('Error al registrar la venta: ' + data.message, 'ErrorG');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al procesar la venta.', 'ErrorG');
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
    // Convertir a minúsculas para hacer la comparación insensible a mayúsculas
    const metodo = metodoPago.toLowerCase();
    
    if (metodo.includes('efectivo')) return 1;
    if (metodo.includes('tarjeta')) return 2;
    if (metodo.includes('transferencia')) return 3;
    
    return 1; // Por defecto, usar efectivo
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
    const direccionSucursal = "Haciendas de San Vicente, 63737 San Vicente, Nay.";
    const nombreVendedor = nombreUsuario || "No especificado"; 
    const dineroRecibido = document.getElementById('inputDineroRecibido').value || "0.00";
    const cambio = document.getElementById('inputCambio').value || "0.00";
    const metodoPago = document.getElementById('metodoPago').value || "No especificado";

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
    doc.text(`Método de Pago: ${metodoPago}`, margenIzquierdo, posicionY); // Aquí agregas el método de pago
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
    posicionY += 6;
    
    // Añadir información de dinero recibido y cambio
    doc.text(`Dinero Recibido: $${dineroRecibido}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Cambio: $${cambio}`, margenIzquierdo, posicionY);

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

// Función para mostrar notificaciones con duración personalizable
function mostrarNotificacion(mensaje, tipo, duracion = 3000) {
    // Crear el contenedor principal si no existe
    let contenedorAlertas = document.querySelector('.contenedorAlertas');
    if (!contenedorAlertas) {
        contenedorAlertas = document.createElement('div');
        contenedorAlertas.className = 'contenedorAlertas';
        document.body.appendChild(contenedorAlertas);
    }
    
    // Crear la alerta
    const alerta = document.createElement('div');
    alerta.className = `alertaInventario ${tipo === 'error' ? 'alerta-critica' : 'alerta-normal'}`;
    
    // Crear el icono
    const icono = document.createElement('div');
    icono.className = 'iconoAlerta';
    icono.innerHTML = tipo === 'error' ? '⚠️' : '✅';
    
    // Crear el mensaje
    const mensajeDiv = document.createElement('div');
    mensajeDiv.className = 'mensajeAlerta';
    
    const titulo = document.createElement('h3');
    titulo.textContent = tipo === 'error' ? 'Error' : 'Éxito';
    
    const parrafo = document.createElement('p');
    parrafo.textContent = mensaje;
    
    mensajeDiv.appendChild(titulo);
    mensajeDiv.appendChild(parrafo);
    
    // Crear el botón de cerrar
    const btnCerrar = document.createElement('button');
    btnCerrar.className = 'cerrarAlerta';
    btnCerrar.innerHTML = '&times;';
    btnCerrar.onclick = function() {
        contenedorAlertas.removeChild(alerta);
    };
    
    // Ensamblar la alerta
    alerta.appendChild(icono);
    alerta.appendChild(mensajeDiv);
    alerta.appendChild(btnCerrar);
    
    // Añadir la alerta al contenedor
    contenedorAlertas.appendChild(alerta);
    
    // Eliminar automáticamente después de la duración especificada
    setTimeout(() => {
        if (alerta.parentNode === contenedorAlertas) {
            contenedorAlertas.removeChild(alerta);
        }
        
        // Si no quedan más alertas, eliminar el contenedor
        if (contenedorAlertas.children.length === 0) {
            document.body.removeChild(contenedorAlertas);
        }
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


// Función para calcular el cambio
function calcularCambio() {
    const dineroRecibido = parseFloat(document.getElementById('inputDineroRecibido').value) || 0;
    const totalVenta = parseFloat(document.getElementById('total').textContent.replace('$', '')) || 0;
    
    let cambio = 0;
    if (dineroRecibido >= totalVenta) {
        cambio = dineroRecibido - totalVenta;
    }
    
    document.getElementById('inputCambio').value = cambio.toFixed(2);
}

// Actualizar la función actualizarTotal para que también actualice el cambio
function actualizarTotal() {
    total = 0;
    carrito.forEach(item => {
        total += item.precio * item.cantidad;
    });
    
    document.getElementById('total').textContent = '$' + total.toFixed(2);
    
    // Actualizar el cambio si hay un valor en dinero recibido
    calcularCambio();
}


// Función para mostrar/ocultar los campos de dinero recibido y cambio
function toggleCamposPago() {
    const metodoPago = document.getElementById('metodoPago').value.toLowerCase();
    const dineroRecibidoDiv = document.querySelector('.dineroRecibido');
    const cambioDiv = document.querySelector('.cambio');

    if (metodoPago === 'efectivo') {
        dineroRecibidoDiv.style.display = 'block';
        cambioDiv.style.display = 'block';
    } else {
        dineroRecibidoDiv.style.display = 'none';
        cambioDiv.style.display = 'none';
        // Limpiar los valores si se ocultan
        document.getElementById('inputDineroRecibido').value = '';
        document.getElementById('inputCambio').value = '';
    }
}

// Añadir evento al cambiar el método de pago
document.getElementById('metodoPago').addEventListener('change', toggleCamposPago);

// Ejecutar al cargar la página para establecer el estado inicial
document.addEventListener('DOMContentLoaded', toggleCamposPago);

// Asegurarse de que la función se ejecute cuando cambie el método de pago
document.addEventListener('DOMContentLoaded', function() {
    const metodoPagoSelect = document.getElementById('metodoPago');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener('change', toggleCamposPago);
        toggleCamposPago(); // Ejecutar al cargar la página
    }
});


