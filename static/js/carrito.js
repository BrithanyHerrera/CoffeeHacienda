// Función para ir a finalizar orden
function irAFinalizarOrden() {
    // Verificar que haya productos en el carrito
    if (carrito.length === 0) {
        mostrarNotificacion('El carrito está vacío');
        return;
    }
    
    // Verificar que se haya ingresado un nombre de cliente
    const nombreCliente = document.getElementById('nombreCliente').value.trim();
    if (!nombreCliente) {
        mostrarNotificacion('Por favor, ingrese el nombre del cliente');
        return;
    }
    
    // Verificar que se haya ingresado el dinero recibido para método de pago en efectivo
    const metodoPago = document.querySelector('select[name="metodoPago"]').value;
    const dineroRecibido = parseFloat(document.getElementById('inputDineroRecibido').value) || 0;
    const total = parseFloat(document.getElementById('total').textContent.replace('$', '')) || 0;
    
    if (metodoPago === 'efectivo' && dineroRecibido < total) {
        mostrarNotificacion('El dinero recibido debe ser igual o mayor al total');
        return;
    }
    
    // Preparar los datos para enviar al servidor
    const productos = carrito.map(item => ({
        id: item.id,
        cantidad: item.cantidad,
        precio: item.precio
    }));
    
    // Enviar los datos al servidor
    fetch('/api/ventas/crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            cliente: nombreCliente,
            productos: productos,
            total: total,
            dineroRecibido: dineroRecibido,
            cambio: parseFloat(document.getElementById('inputCambio').value) || 0
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito
            mostrarNotificacion('Venta registrada exitosamente');
            
            // Vaciar el carrito
            vaciarCarrito();
            
            // Cerrar el panel del carrito
            const carritoPanel = document.getElementById('carritoPanel');
            if (carritoPanel) {
                carritoPanel.classList.remove('mostrar');
            }
        } else {
            // Mostrar mensaje de error
            mostrarNotificacion('Error al registrar la venta: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la venta');
    });
}

// Función para vaciar el carrito
function vaciarCarrito() {
    carrito = [];
    localStorage.removeItem('carrito');
    actualizarCarritoUI();
    
    // Mostrar notificación
    mostrarNotificacion('Carrito vaciado');
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje) {
    // Verificar si ya existe una notificación
    let notificacion = document.querySelector('.notificacion');
    
    // Si no existe, crearla
    if (!notificacion) {
        notificacion = document.createElement('div');
        notificacion.className = 'notificacion';
        document.body.appendChild(notificacion);
    }
    
    // Establecer el mensaje
    notificacion.textContent = mensaje;
    
    // Mostrar la notificación
    notificacion.classList.add('mostrar');
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notificacion.classList.remove('mostrar');
    }, 3000);
}