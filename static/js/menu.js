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

function agregarAlCarrito(nombre, precio, imagen, tamaño, id, varianteId = null) {
    const productoExistente = carrito.find(item => (
        item.id === id && item.varianteId === varianteId
    ));
    
    if (productoExistente) {
        productoExistente.cantidad++;
    } else {
        carrito.push({ 
            nombre, 
            precio, 
            cantidad: 1, 
            imagen, 
            tamaño,
            id,
            varianteId
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
    carritoItems.replaceChildren();

    let total = 0;
    carrito.forEach((item, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('carritoItem');

        const imagenElemento = document.createElement('img');
        imagenElemento.src = item.imagen;
        imagenElemento.alt = item.nombre;
        const detalles = document.createElement('div');
        const titulo = document.createElement('h4');
        titulo.textContent = `${item.nombre} (${item.tamaño})`;
        const precio = document.createElement('p');
        precio.textContent = `Precio: $${Number(item.precio).toFixed(2)}`;
        const totalItem = document.createElement('p');
        totalItem.textContent = 'Total: $';
        const totalValor = document.createElement('span');
        totalValor.className = 'total-item';
        totalValor.textContent = (item.precio * item.cantidad).toFixed(2);
        totalItem.append(totalValor);
        detalles.append(titulo, precio, totalItem);
        const cantidad = document.createElement('input');
        cantidad.type = 'number';
        cantidad.className = 'cantidadProducto';
        cantidad.dataset.index = index;
        cantidad.value = item.cantidad;
        cantidad.min = '1';
        const eliminar = document.createElement('button');
        eliminar.className = 'eliminarItemCarrito';
        eliminar.dataset.index = index;
        eliminar.type = 'button';
        eliminar.textContent = 'X';
        itemDiv.append(imagenElemento, detalles, cantidad, eliminar);

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
    opciones.replaceChildren();

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
                const tamaño = tamaños[indice].dataset.tamano || 'No aplica';
                const precio = parseFloat(tamaños[indice].getAttribute('preciosDatos'));
                const varianteValor = tamaños[indice].dataset.varianteId;
                const varianteId = varianteValor ? parseInt(varianteValor, 10) : null;
                agregarAlCarrito(nombre, precio, imagen, tamaño, id, varianteId);
            });
        } else if (tamaños.length === 1) {
            // Un solo tamaño → agregar directo
            const tamaño = tamaños[0].dataset.tamano || 'No aplica';
            const precio = parseFloat(tamaños[0].getAttribute('preciosDatos'));
            const varianteValor = tamaños[0].dataset.varianteId;
            const varianteId = varianteValor ? parseInt(varianteValor, 10) : null;
            agregarAlCarrito(nombre, precio, imagen, tamaño, id, varianteId);
        } else {
            // Sin tamaños definidos
            const tamaño = 'Único';
            const precio = parseFloat(producto.getAttribute('data-precio') || 0);
            agregarAlCarrito(nombre, precio, imagen, tamaño, id, null);
        }
    });
});


// ==========================================
// ALERTAS / NOTIFICACIONES
// ==========================================






// ==========================================
// REALIZAR PEDIDO
// ==========================================

function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const numeroMesa = paraLlevar ? '' : document.getElementById('numeroMesa').value.trim();
    const selectorPago = document.querySelector('select[name="metodoPago"]');
    const metodoPagoId = parseInt(selectorPago.value, 10);
    const metodoPagoCodigo = selectorPago.selectedOptions[0]?.dataset.codigo || '';
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
    if (!Number.isInteger(metodoPagoId) || !metodoPagoCodigo) {
        mostrarAlerta('Seleccione un método de pago válido.', 'ErrorG');
        return;
    }

    if (metodoPagoCodigo === 'EFECTIVO' && dineroRecibido < total) {
        mostrarAlerta('El monto recibido es menor al total de la compra. No se puede realizar la venta.', 'ErrorG');
        return;
    }

    const productos = carrito.map(item => ({
        id: item.id,
        cantidad: item.cantidad,
        variante_id: item.varianteId
    }));

    const botonCheckout = document.querySelector('.checkout');
    if (botonCheckout.disabled) {
        return;
    }
    botonCheckout.disabled = true;

    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            cliente: nombreCliente,
            mesa: numeroMesa,
            productos: productos,
            metodo_pago: metodoPagoId,
            dinero_recibido: metodoPagoCodigo === 'EFECTIVO' ? dineroRecibido : 0
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Venta registrada exitosamente.', 'ExitoG');
            generarPDF(data);
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
    })
    .finally(() => {
        botonCheckout.disabled = false;
    });
}


// ==========================================
// UTILIDADES
// ==========================================

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
    const selectorPago = document.getElementById('metodoPago');
    const metodoPagoCodigo = selectorPago.selectedOptions[0]?.dataset.codigo || '';
    const dineroRecibidoDiv = document.querySelector('.dineroRecibido');
    const cambioDiv = document.querySelector('.cambio');

    if (metodoPagoCodigo === 'EFECTIVO') {
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

function generarPDF(datosVenta = {}) {
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
    const ahora = new Date();
    const fechaHora = ahora.toLocaleString();
    const fechaCorta = ahora.toISOString().slice(0, 10); // 2026-05-04
    const nombreCliente = document.getElementById('nombreCliente').value.trim() || "No especificado";
    const direccionSucursal = "Haciendas de San Vicente, 63737 San Vicente, Nay.";
    const nombreVendedor = nombreUsuario || "No especificado"; 
    const dineroRecibido = datosVenta.dinero_recibido
        ?? document.getElementById('inputDineroRecibido').value
        ?? "0.00";
    const cambio = datosVenta.cambio
        ?? document.getElementById('inputCambio').value
        ?? "0.00";
    const metodoPagoSelect = document.getElementById('metodoPago');
    const metodoPago = metodoPagoSelect.selectedOptions[0]?.textContent || "No especificado";
    const paraLlevar = document.getElementById('paraLlevar').checked;
    const numeroMesa = document.getElementById('numeroMesa').value.trim();

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
    const productosTicket = Array.isArray(datosVenta.productos) ? datosVenta.productos : carrito;
    productosTicket.forEach(item => {
        const precio = parseFloat(item.precio) || 0;
        const tamano = item.tamano || item.tamaño || 'No aplica';
        let subtotal = precio * item.cantidad;
        total += subtotal;
        filas.push([
            item.nombre,
            tamano,
            item.cantidad,
            `$${precio.toFixed(2)}`,
            `$${subtotal.toFixed(2)}`
        ]);
    });

    const totalServidor = parseFloat(datosVenta.total);
    if (Number.isFinite(totalServidor)) {
        total = totalServidor;
    }

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

    // Generar nombre estructurado del archivo
    const vendedorLimpio = nombreVendedor.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]/g, '').replace(/\s+/g, '_');
    const clienteLimpio = nombreCliente.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]/g, '').replace(/\s+/g, '_');
    let nombreArchivo;

    if (paraLlevar) {
        nombreArchivo = `Llevar_${clienteLimpio}_${vendedorLimpio}_${fechaCorta}.pdf`;
    } else {
        nombreArchivo = `Mesa${numeroMesa || '0'}_${vendedorLimpio}_${fechaCorta}.pdf`;
    }

    // Descargar localmente
    doc.save(nombreArchivo);

    // Guardar en el servidor
    const pdfBase64 = doc.output('datauristring').split(',')[1];
    fetch('/api/guardar-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            pdf: pdfBase64,
            nombre: nombreArchivo,
            tipo: 'ticket'
        })
    }).catch(err => console.error('Error al guardar PDF en servidor:', err));
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
