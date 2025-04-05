document.getElementById('btnRealizarCorte').addEventListener('click', function () {
    realizarCorte();
});

function realizarCorte() {
    // Recoger los datos del formulario
    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;
    
    const totalVentas = parseFloat(document.getElementById('total2').value);
    const totalContado = parseFloat(document.getElementById('total').value);
    const totalEfectivo = parseFloat(document.getElementById('calculado').value);
    const totalTransferencias = parseFloat(document.getElementById('calculadoCheque').value);
    const totalPaypal = parseFloat(document.getElementById('calculadoVales').value);
    const pagosRealizados = parseFloat(document.getElementById('pagos_realizados').value);

    // Asegurarse de que las fechas estén presentes
    if (!fechaDesde || !fechaHasta) {
        alert("Por favor, selecciona las fechas de inicio y cierre.");
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
        pagos_realizados: pagosRealizados
    });

    fetch('/guardarCorteCaja', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fecha_hora_inicio: fechaDesde,
            fecha_hora_cierre: fechaHasta,
            total_ventas: totalVentas,
            total_efectivo: totalEfectivo,
            total_transferencias: totalTransferencias,
            total_paypal: totalPaypal,
            total_contado: totalContado,
            pagos_realizados: pagosRealizados
        })
    })
    .then(response => {
        // Log para revisar el estado de la respuesta
        console.log('Response status:', response.status);

        if (!response.ok) {
            return Promise.reject('No se pudo guardar el corte de caja');
        }
        return response.json();
    })
    .then(data => {
        // Log para revisar la respuesta JSON
        console.log('Datos recibidos:', data);

        if (data.success) {
            alert("Corte de caja guardado exitosamente.");
            // Puedes redirigir al usuario o actualizar la interfaz si es necesario
        } else {
            alert("Hubo un problema al guardar el corte.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Hubo un error en el proceso.");
    });
}
