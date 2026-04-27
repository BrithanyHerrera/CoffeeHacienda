// ==========================================
// BÚSQUEDA Y FILTROS
// ==========================================

document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const productos = document.querySelectorAll('.producto');

    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('h3').textContent.toLowerCase();
        producto.style.display = nombreProducto.includes(searchTerm) ? '' : 'none';
    });
});

function filtrarProductos(categoria) {
    const productos = document.querySelectorAll('.producto');
    const botones = document.querySelectorAll('.categoriasBebidas button');

    // Marcar el botón activo
    botones.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(categoria) || 
            (categoria === 'todos' && btn.textContent === 'Todos')) {
            btn.classList.add('active');
        }
    });

    productos.forEach(producto => {
        const productoCategoria = producto.getAttribute('categoriasDatos').toLowerCase();
        producto.style.display = (productoCategoria === categoria || categoria === 'todos') ? '' : 'none';
    });
}


// ==========================================
// CARRITO
// ==========================================

let carrito = [];

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
            id
        });
    }
    
    actualizarCarrito();
}

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

    // Eventos para botones de eliminar
    document.querySelectorAll('.eliminarItemCarrito').forEach(button => {
        button.addEventListener('click', function() {
            const index = this.getAttribute('data-index');
            carrito.splice(index, 1);
            actualizarCarrito();
        });
    });

    // Eventos para inputs de cantidad
    document.querySelectorAll('.cantidadProducto').forEach(input => {
        input.addEventListener('change', function() {
            const index = this.getAttribute('data-index');
            let nuevaCantidad = parseInt(this.value);

            if (nuevaCantidad < 1 || isNaN(nuevaCantidad)) {
                nuevaCantidad = 1;
                this.value = 1;
            }

            carrito[index].cantidad = nuevaCantidad;
            actualizarCarrito();
        });
    });

    // Actualizar cambio si hay dinero recibido
    calcularCambio();
}


// ==========================================
// SELECCIÓN DE TAMAÑO (Modal en vez de prompt)
// ==========================================

// Variables para el modal de tamaño
let tamanoCallback = null;

function mostrarModalTamano(nombre, tamaños, callback) {
    const modal = document.getElementById('tamanoModal');
    const titulo = document.getElementById('tamanoModalTitulo');
    const opciones = document.getElementById('tamanoOpciones');

    titulo.textContent = `Seleccione tamaño para ${nombre}`;
    opciones.innerHTML = '';

    tamaños.forEach((tamano, index) => {
        const btn = document.createElement('button');
        btn.className = 'añadirCarrito'; // Reutilizar el estilo del botón
        btn.style.width = '100%';
        btn.style.padding = '12px';
        btn.style.fontSize = '15px';
        btn.textContent = tamano.textContent.trim();
        btn.addEventListener('click', function() {
            callback(index);
            cerrarModalTamano();
        });
        opciones.appendChild(btn);
    });

    modal.style.display = 'flex';
}

function cerrarModalTamano() {
    const modal = document.getElementById('tamanoModal');
    modal.style.display = 'none';
}

// Cerrar modal al hacer clic afuera
document.addEventListener('click', function(e) {
    const modal = document.getElementById('tamanoModal');
    if (e.target === modal) {
        cerrarModalTamano();
    }
});


// ==========================================
// EVENTOS DE BOTONES "AÑADIR A LA ORDEN"
// ==========================================

document.querySelectorAll('.añadirCarrito').forEach(button => {
    button.addEventListener('click', function() {
        const producto = this.parentElement;
        const nombre = producto.querySelector('h3').textContent;
        const imagen = producto.querySelector('img').src;
        const id = parseInt(producto.getAttribute('data-id'));
        
        const tamaños = producto.querySelectorAll('.tamaño');
        
        if (tamaños.length > 1) {
            // Múltiples tamaños → abrir modal bonito
            mostrarModalTamano(nombre, tamaños, function(indice) {
                const tamaño = tamaños[indice].textContent.split('-')[0].trim();
                const precio = parseFloat(tamaños[indice].getAttribute('preciosDatos'));
                agregarAlCarrito(nombre, precio, imagen, tamaño, id);
            });
        } else if (tamaños.length === 1) {
            // Un solo tamaño → agregar directo
            const tamaño = tamaños[0].textContent.split('-')[0].trim();
            const precio = parseFloat(tamaños[0].getAttribute('preciosDatos'));
            agregarAlCarrito(nombre, precio, imagen, tamaño, id);
        } else {
            // Sin tamaños definidos
            const tamaño = 'Único';
            const precio = parseFloat(producto.getAttribute('data-precio') || 0);
            agregarAlCarrito(nombre, precio, imagen, tamaño, id);
        }
    });
});


// ==========================================
// ALERTAS / NOTIFICACIONES
// ==========================================

function mostrarAlerta(mensaje, tipo = 'ExitoG') {
    const contenedor = document.querySelector('.contenedorAlertas') || crearContenedorAlertas();

    const alerta = document.createElement('div');
    alerta.className = `alertaGeneral alerta-${tipo}`;

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
    setTimeout(() => alerta.remove(), 5000);
}

function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
}


// ==========================================
// REALIZAR PEDIDO
// ==========================================

function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const numeroMesa = paraLlevar ? '' : document.getElementById('numeroMesa').value.trim();
    const metodoPago = document.querySelector('select[name="metodoPago"]').value;
    const dineroRecibido = parseFloat(document.getElementById('inputDineroRecibido').value) || 0;
    const total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

    // Validaciones
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

    const cambio = parseFloat(document.getElementById('inputCambio').value) || 0;

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
            metodo_pago: obtenerIdMetodoPago(metodoPago),
            dinero_recibido: dineroRecibido,
            cambio: cambio
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Venta registrada exitosamente.', 'ExitoG');
            generarPDF();
            carrito = [];
            actualizarCarrito();
            // Limpiar formulario
            document.getElementById('nombreCliente').value = '';
            document.getElementById('numeroMesa').value = '';
            document.getElementById('inputDineroRecibido').value = '';
            document.getElementById('inputCambio').value = '0';
            document.getElementById('metodoPago').selectedIndex = 0;
            document.getElementById('paraLlevar').checked = false;
            toggleMesaField();
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


// ==========================================
// UTILIDADES
// ==========================================

function obtenerIdMetodoPago(metodoPago) {
    const metodo = metodoPago.toLowerCase();
    if (metodo.includes('efectivo')) return 1;
    if (metodo.includes('tarjeta')) return 2;
    if (metodo.includes('transferencia')) return 3;
    return 1;
}

function calcularCambio() {
    const dineroRecibido = parseFloat(document.getElementById('inputDineroRecibido').value) || 0;
    const totalVenta = parseFloat(document.getElementById('total').textContent.replace('$', '')) || 0;
    
    let cambio = 0;
    if (dineroRecibido >= totalVenta) {
        cambio = dineroRecibido - totalVenta;
    }
    
    document.getElementById('inputCambio').value = cambio.toFixed(2);
}

function toggleMesaField() {
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const mesaContainer = document.getElementById('mesaContainer');
    
    if (paraLlevar) {
        mesaContainer.style.display = 'none';
        document.getElementById('numeroMesa').value = '';
    } else {
        mesaContainer.style.display = 'block';
    }
}

function toggleCamposPago() {
    const metodoPago = document.getElementById('metodoPago').value.toLowerCase();
    const dineroRecibidoDiv = document.querySelector('.dineroRecibido');
    const cambioDiv = document.querySelector('.cambio');

    if (metodoPago === 'efectivo') {
        dineroRecibidoDiv.style.display = 'flex';
        cambioDiv.style.display = 'flex';
    } else {
        dineroRecibidoDiv.style.display = 'none';
        cambioDiv.style.display = 'none';
        document.getElementById('inputDineroRecibido').value = '';
        document.getElementById('inputCambio').value = '';
    }
}


// ==========================================
// GENERAR PDF
// ==========================================

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

    // Configurar fuente
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
    doc.text(`Método de Pago: ${metodoPago}`, margenIzquierdo, posicionY);
    posicionY += 10;

    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Artículos
    doc.setFont("times", "bold");
    doc.text("Artículos Comprados:", margenIzquierdo, posicionY);
    posicionY += 8;
    doc.setFont("times", "normal");

    let columnas = ["Producto", "Tamaño", "Cantidad", "Precio", "Subtotal"];
    let filas = [];

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

    posicionY = doc.lastAutoTable.finalY + 10;

    doc.setFont("times", "bold");
    doc.text(`TOTAL: $${total.toFixed(2)}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Dinero Recibido: $${dineroRecibido}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Cambio: $${cambio}`, margenIzquierdo, posicionY);

    doc.save(`Recibo_${nombreCliente}.pdf`);
}


// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Estado inicial del campo mesa
    toggleMesaField();
    
    // Estado inicial de campos de pago
    toggleCamposPago();
    
    // Evento al cambiar método de pago
    const metodoPagoSelect = document.getElementById('metodoPago');
    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener('change', toggleCamposPago);
    }
});
