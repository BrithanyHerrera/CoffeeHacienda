document.getElementById('btnFiltrarFechas').addEventListener('click', function () {
    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;

    if (!fechaDesde || !fechaHasta) {
        alert("Selecciona un rango de fechas válido.");
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
        document.getElementById('calculadoCheque').value = data.transferencias;
        document.getElementById('calculadoVales').value = data.paypal; // Asignar valor 0 por defecto si es necesario

    })
    .catch(error => console.error('Error al obtener las ventas:', error));

})
// Botón para calcular los totales cuando se hace clic en "Calcular Corte"
document.getElementById('btnCalcularCorte').addEventListener('click', function () {
    // Calcular la diferencia
    document.getElementById('diferencia').value = 
        parseFloat(document.getElementById('contado').value) - parseFloat(document.getElementById('calculado').value);
    document.getElementById('diferenciaCheque').value = 
        parseFloat(document.getElementById('cheque').value) - parseFloat(document.getElementById('calculadoCheque').value);
    document.getElementById('diferenciaVales').value = 
        parseFloat(document.getElementById('vales').value) - parseFloat(document.getElementById('calculadoVales').value);

    // Calcular totales
    let totalContado = parseFloat(document.getElementById('contado').value) + 
                       parseFloat(document.getElementById('cheque').value) + 
                       parseFloat(document.getElementById('vales').value); // Incluir tarjeta si es necesario

    // Calcular el total
    let totalCalculado = parseFloat(document.getElementById('calculado').value) + 
                         parseFloat(document.getElementById('calculadoCheque').value) + 
                         parseFloat(document.getElementById('calculadoVales').value);

    let totalDiferencia = totalContado - totalCalculado;

    // Actualizar la fila del total
    document.getElementById('total').value = totalContado;
    document.getElementById('total2').value = totalCalculado;
    document.getElementById('totalDiferencia').value = totalDiferencia;
});

// Función para guardar el corte de caja
document.getElementById('btnRealizarCorte').addEventListener('click', function (event) {
    event.preventDefault();

    // Obtener los valores de los campos
    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;
    const totalVentas = parseFloat(document.getElementById('total2').value);
    const totalContado = parseFloat(document.getElementById('total').value);
    const totalEfectivo = parseFloat(document.getElementById('calculado').value);
    const totalTransferencias = parseFloat(document.getElementById('calculadoCheque').value);
    const totalPaypal = parseFloat(document.getElementById('calculadoVales').value);
    const pagosRealizados = parseFloat(document.getElementById('pagos_realizados').value);
    const fondo = parseFloat(document.getElementById('fondo').value);

    // Verificar que las fechas estén presentes
    if (!fechaDesde || !fechaHasta) {
        alert("Por favor, selecciona las fechas de inicio y cierre.");
        return;  // Evita continuar si las fechas no están completas
    }

    // Verificar que los valores sean válidos
    if (isNaN(totalVentas) || isNaN(totalContado) || isNaN(totalEfectivo) || isNaN(totalTransferencias) || isNaN(totalPaypal) || isNaN(pagosRealizados) || isNaN(fondo)) {
        alert("Por favor, asegúrate de que todos los campos numéricos estén completos y sean válidos.");
        return;
    }

    // Log de los datos que se van a enviar
    console.log("Enviando datos al servidor: ");
    console.log({
        fecha_hora_inicio: fechaDesde,
        fecha_hora_cierre: fechaHasta,
        total_ventas: totalVentas,
        total_efectivo: totalEfectivo,
        total_transferencias: totalTransferencias,
        total_paypal: totalPaypal,
        total_contado: totalContado,
        pagos_realizados: pagosRealizados,
        fondo: fondo
    });

    // Realizamos la solicitud con fetch
    fetch('/guardarCorteCaja', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  // Asegúrate de enviar los datos como JSON
        },
        body: JSON.stringify({
            fecha_hora_inicio: fechaDesde,
            fecha_hora_cierre: fechaHasta,
            total_ventas: totalVentas,
            total_efectivo: totalEfectivo,
            total_transferencias: totalTransferencias,
            total_paypal: totalPaypal,
            total_contado: totalContado,
            pagos_realizados: pagosRealizados,
            fondo: fondo
        })
    })
    .then(response => {
        console.log(response);  // Muestra la respuesta completa
        return response.json(); // Intenta convertir a JSON
    })
    .then(data => {
        console.log(data); // Muestra el JSON recibido
        if (data.success) {
            alert("Corte de caja guardado exitosamente.");
        } else {
            alert("Hubo un problema al guardar el corte: " + data.error);
        }
    })    
    .catch(error => {
        alert('Error al guardar el corte de caja: ' + error);
    });
});
