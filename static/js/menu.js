// ==========================================
// BÚSQUEDA Y FILTROS INTERACTIVOS COMBINADOS
// ==========================================

let categoriaSeleccionada = 'todas';

function aplicarFiltros() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = (searchInput ? searchInput.value : '').trim().toLowerCase();
    const productos = document.querySelectorAll('.producto');

    const catFiltro = (categoriaSeleccionada || 'todas').toLowerCase().trim();
    const esTodas = catFiltro === 'todas' || catFiltro === 'todos';

    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('h3') ? producto.querySelector('h3').textContent.toLowerCase() : '';
        const descProducto = producto.querySelector('p') ? producto.querySelector('p').textContent.toLowerCase() : '';
        const productoCategoria = (producto.getAttribute('categoriasDatos') || '').toLowerCase().trim();

        const coincideCategoria = esTodas || (productoCategoria === catFiltro);
        const coincideBusqueda = !searchTerm 
            || nombreProducto.includes(searchTerm) 
            || descProducto.includes(searchTerm);

        if (coincideCategoria && coincideBusqueda) {
            producto.style.display = '';
        } else {
            producto.style.display = 'none';
        }
    });
}

function buscarProducto() {
    aplicarFiltros();
}

function filtrarProductos(categoria) {
    categoriaSeleccionada = (categoria || 'todas').toLowerCase().trim();
    const botones = document.querySelectorAll('.categoriasBebidas button, .categorias-tabs .tab-categoria');

    botones.forEach(btn => {
        const btnCat = (btn.getAttribute('data-categoria') || btn.textContent).toLowerCase().trim();
        const esTodasBtn = btnCat === 'todas' || btnCat === 'todos';
        const esTodasFiltro = categoriaSeleccionada === 'todas' || categoriaSeleccionada === 'todos';

        if (esTodasFiltro && esTodasBtn) {
            btn.classList.add('active');
        } else if (!esTodasFiltro && !esTodasBtn && btnCat === categoriaSeleccionada) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    aplicarFiltros();
}

function inicializarCategoriasDinamicas() {
    const contenedorTabs = document.querySelector('.categoriasBebidas, .categorias-tabs');
    if (!contenedorTabs) return;

    // Detectar categorías de los productos en el DOM
    const productos = document.querySelectorAll('.producto');
    const categoriasPresentes = new Set();
    
    productos.forEach(p => {
        const cat = (p.getAttribute('categoriasDatos') || '').trim();
        if (cat && cat.toLowerCase() !== 'todos' && cat.toLowerCase() !== 'todas') {
            categoriasPresentes.add(cat);
        }
    });

    // Detectar botones ya presentes
    const botonesExistentes = contenedorTabs.querySelectorAll('button');
    const categoriasConBoton = new Set();
    botonesExistentes.forEach(btn => {
        const cat = (btn.getAttribute('data-categoria') || btn.textContent).trim().toLowerCase();
        categoriasConBoton.add(cat);
    });

    // Añadir dinámicamente cualquier categoría de los productos que aún no tenga botón
    categoriasPresentes.forEach(cat => {
        if (!categoriasConBoton.has(cat.toLowerCase())) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tab-categoria';
            btn.dataset.categoria = cat;
            btn.textContent = cat;
            btn.onclick = () => filtrarProductos(cat);
            contenedorTabs.appendChild(btn);
        }
    });
}

const inputBusquedaEl = document.getElementById('searchInput');
if (inputBusquedaEl) {
    inputBusquedaEl.addEventListener('input', aplicarFiltros);
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

    document.getElementById('total').textContent = `$${total.toFixed(2)}`;

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

function mostrarAlertaVentaExitosa(infoTicket) {
    const contenedor = (typeof crearContenedorAlertas === 'function')
        ? crearContenedorAlertas()
        : (document.getElementById('contenedor-alertas') || (() => {
            const c = document.createElement('div');
            c.id = 'contenedor-alertas';
            c.style.position = 'fixed';
            c.style.top = '20px';
            c.style.right = '20px';
            c.style.zIndex = '9999';
            document.body.appendChild(c);
            return c;
        })());

    const alerta = document.createElement('div');
    alerta.className = 'alerta alerta-exito alerta-venta-ticket';

    const contenidoIzquierdo = document.createElement('div');
    contenidoIzquierdo.style.display = 'flex';
    contenidoIzquierdo.style.alignItems = 'center';
    contenidoIzquierdo.style.gap = '10px';
    contenidoIzquierdo.style.flexWrap = 'wrap';

    const texto = document.createElement('span');
    texto.style.fontWeight = '500';
    texto.textContent = 'Venta registrada exitosamente.';
    contenidoIzquierdo.appendChild(texto);

    const ticketUrl = infoTicket && infoTicket.blobUrl ? infoTicket.blobUrl : null;
    if (ticketUrl) {
        const btnTicket = document.createElement('a');
        btnTicket.href = ticketUrl;
        btnTicket.target = '_blank';
        btnTicket.rel = 'noopener noreferrer';
        btnTicket.className = 'btn-ver-ticket';
        btnTicket.textContent = '📄 Ver/Imprimir Ticket';
        btnTicket.setAttribute('title', 'Abrir ticket para visualizar o imprimir en nueva pestaña');
        contenidoIzquierdo.appendChild(btnTicket);

        if (infoTicket.promesaGuardar) {
            infoTicket.promesaGuardar.then(res => {
                if (res && res.url) {
                    btnTicket.href = res.url;
                }
            });
        }
    }

    alerta.appendChild(contenidoIzquierdo);

    const botonCerrar = document.createElement('button');
    botonCerrar.type = 'button';
    botonCerrar.textContent = '×';
    botonCerrar.style.background = 'none';
    botonCerrar.style.border = 'none';
    botonCerrar.style.color = '#fff';
    botonCerrar.style.fontSize = '22px';
    botonCerrar.style.lineHeight = '1';
    botonCerrar.style.cursor = 'pointer';
    botonCerrar.style.padding = '0';
    botonCerrar.style.marginLeft = '12px';
    botonCerrar.onclick = () => alerta.remove();

    alerta.appendChild(botonCerrar);
    contenedor.appendChild(alerta);

    setTimeout(() => {
        if (alerta.parentElement) {
            alerta.remove();
        }
    }, 8000);
}






// ==========================================
// REALIZAR PEDIDO
// ==========================================

function normalizarMesa(m) {
    if (!m) return 'Para llevar';
    const s = String(m).trim();
    if (!s || s.toLowerCase() === 'sin mesa' || s.toLowerCase() === 'none' || s.toLowerCase() === 'null') {
        return 'Para llevar';
    }
    return s;
}

function realizarPedido() {
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    const selectorMesa = document.getElementById('numeroMesa');
    const paraLlevarCheckbox = document.getElementById('paraLlevar');
    let numeroMesa = normalizarMesa(selectorMesa ? selectorMesa.value : '');
    if (paraLlevarCheckbox && paraLlevarCheckbox.checked) {
        numeroMesa = 'Para llevar';
    }
    const paraLlevar = numeroMesa === 'Para llevar';
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
            const infoTicket = generarPDF(data);
            mostrarAlertaVentaExitosa(infoTicket);
            carrito = [];
            actualizarCarrito();
            // Limpiar formulario
            document.getElementById('nombreCliente').value = '';
            if (selectorMesa) {
                selectorMesa.value = 'Para llevar';
            }
            document.getElementById('inputDineroRecibido').value = '';
            document.getElementById('inputCambio').value = '0';
            document.getElementById('metodoPago').selectedIndex = 0;
            if (paraLlevarCheckbox) {
                paraLlevarCheckbox.checked = false;
            }
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
    const selectorMesa = document.getElementById('numeroMesa');
    const paraLlevarCheckbox = document.getElementById('paraLlevar');
    const mesaContainer = document.getElementById('mesaContainer');
    
    if (paraLlevarCheckbox && selectorMesa) {
        if (paraLlevarCheckbox.checked) {
            selectorMesa.value = 'Para llevar';
        }
    }
    if (mesaContainer) {
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
    const selectorMesa = document.getElementById('numeroMesa');
    let mesaVal = selectorMesa ? selectorMesa.value : '';
    if (!mesaVal && datosVenta) {
        mesaVal = datosVenta.mesa || datosVenta.numero_mesa || '';
    }
    const mesaNormalizada = normalizarMesa(mesaVal);
    const paraLlevar = mesaNormalizada === 'Para llevar';

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
    posicionY += 6;
    doc.text(`Mesa / Servicio: ${mesaNormalizada}`, margenIzquierdo, posicionY);
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
        const mesaLimpia = mesaNormalizada.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]/g, '').replace(/\s+/g, '_');
        nombreArchivo = `${mesaLimpia}_${vendedorLimpio}_${fechaCorta}.pdf`;
    }

    // Guardado silencioso de Tickets: se desactiva la descarga automática para no saturar descargas
    // doc.save(nombreArchivo);

    // Generar URL Blob para permitir visualización o impresión bajo demanda
    const pdfBlob = doc.output('blob');
    const blobUrl = URL.createObjectURL(pdfBlob);

    // Guardar en el servidor (instance/pdfs/tickets_ventas/)
    const pdfBase64 = doc.output('datauristring').split(',')[1];
    const promesaGuardar = fetch('/api/guardar-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            pdf: pdfBase64,
            nombre: nombreArchivo,
            tipo: 'ticket'
        })
    }).then(res => res.json())
      .catch(err => {
          console.error('Error al guardar PDF en servidor:', err);
          return null;
      });

    return {
        blobUrl: blobUrl,
        nombreArchivo: nombreArchivo,
        promesaGuardar: promesaGuardar
    };
}


// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Configurar listener para buscador interactivo
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', aplicarFiltros);
    }

    // Inicializar categorías dinámicas desde los productos en el DOM
    inicializarCategoriasDinamicas();

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
