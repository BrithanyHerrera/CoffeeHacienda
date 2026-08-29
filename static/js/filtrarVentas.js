document.getElementById('btnFiltrarFechas').addEventListener('click', function () {
    corteCalculado = false;


    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;

    if (!fechaDesde || !fechaHasta) {
        mostrarAlerta("Selecciona un rango de fechas válido.", 'ErrorG');
        return;
    }

    fetch('/filtrarVentas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fechaDesde: fechaDesde,
            fechaHasta: fechaHasta
        })
    })
    .then(response => response.json())
    .then(data => {
        // Actualizar los campos con los valores calculados
        document.getElementById('calculado').value = data.efectivo;
        document.getElementById('cheque').value = data.transferencias;
        document.getElementById('calculadoCheque').value = data.transferencias;
        document.getElementById('vales').value = data.tarjeta;
        document.getElementById('calculadoVales').value = data.tarjeta;

    })
    .catch(error => console.error('Error al obtener las ventas:', error));

})

document.getElementById('btnCalcularCorte').addEventListener('click', function () {
    // Obtener elementos
    const contado = parseFloat(document.getElementById('contado').value) || 0;
    const cheque = parseFloat(document.getElementById('cheque').value) || 0;
    const vales = parseFloat(document.getElementById('vales').value) || 0;

    const calculado = parseFloat(document.getElementById('calculado').value) || 0;
    const calculadoCheque = parseFloat(document.getElementById('calculadoCheque').value) || 0;
    const calculadoVales = parseFloat(document.getElementById('calculadoVales').value) || 0;

    // Diferencias
    const diferencia = contado - calculado;
    const diferenciaCheque = cheque - calculadoCheque;
    const diferenciaVales = vales - calculadoVales;

    // Actualizar diferencias
    const diffInput = document.getElementById('diferencia');
    const diffChequeInput = document.getElementById('diferenciaCheque');
    const diffValesInput = document.getElementById('diferenciaVales');

    diffInput.value = diferencia;
    diffChequeInput.value = diferenciaCheque;
    diffValesInput.value = diferenciaVales;

    // Resetear estilos
    [diffInput, diffChequeInput, diffValesInput].forEach(input => {
        input.style.color = 'black';
        input.style.backgroundColor = '';
    });

    let diferenciasNegativas = false;

    // Aplicar estilo rojo si es negativo
    if (diferencia < 0) {
        diffInput.style.color = 'white';
        diffInput.style.backgroundColor = '#e74c3c'; // rojo
        diferenciasNegativas = true;
    }
    else if (diferencia > 0) {
        diffInput.style.color = 'white';
        diffInput.style.backgroundColor = '#e74c3c'; 
        diferenciasNegativas = true; 
    }

    if (diferenciaCheque < 0) {
        diffChequeInput.style.color = 'white';
        diffChequeInput.style.backgroundColor = '#e74c3c';
        diferenciasNegativas = true;
    }
    else if (diferenciaCheque > 0) {
        diffChequeInput.style.color = 'white';
        diffChequeInput.style.backgroundColor = '#e74c3c';
        diferenciasNegativas = true;
    }


    if (diferenciaVales < 0) {
        diffValesInput.style.color = 'white';
        diffValesInput.style.backgroundColor = '#e74c3c';
        diferenciasNegativas = true;
    }
    else if (diferenciaVales > 0) {
        diffValesInput.style.color = 'white';
        diffValesInput.style.backgroundColor = '#e74c3c';
        diferenciasNegativas = true;
    }
    // Calcular totales
    const totalContado = contado + cheque + vales;
    const totalCalculado = calculado + calculadoCheque + calculadoVales;
    const totalDiferencia = totalContado - totalCalculado;

    // Mostrar totales
    document.getElementById('total').value = totalContado;
    document.getElementById('total2').value = totalCalculado;
    document.getElementById('totalDiferencia').value = totalDiferencia;

    // Mostrar u ocultar la advertencia
    const alerta = document.getElementById('alertaDiferencia');
    const btnGuardar = document.getElementById('btnRealizarCorte');

    if (diferenciasNegativas) {
        alerta.style.display = 'block';
        btnGuardar.disabled = true;
    } else {
        alerta.style.display = 'none';
        btnGuardar.disabled = false;
    }

    corteCalculado = true; 
});











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

