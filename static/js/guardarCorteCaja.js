let corteCalculado = false;

document.getElementById('btnRealizarCorte').addEventListener('click', function () {
    realizarCorte();
});

function realizarCorte() {

    if (!corteCalculado) {
        mostrarAlerta("Primero debes presionar calcular corte para verificar los totales.", 'ErrorG');
        return; // Detiene la ejecución aquí mismo
    }

    // Recoger los datos del formulario
    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;
    
    const totalVentas = parseFloat(document.getElementById('total2').value);
    const totalContado = parseFloat(document.getElementById('total').value);
    const totalEfectivo = parseFloat(document.getElementById('calculado').value);
    const totalTransferencias = parseFloat(document.getElementById('calculadoCheque').value);
    const totalPaypal = parseFloat(document.getElementById('calculadoVales').value);
    const pagosRealizados = parseFloat(document.getElementById('pagos_realizados').value);
    const fondo = parseFloat(document.getElementById('fondo').value);


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
            pagos_realizados: pagosRealizados,
            fondo: fondo
        })
    })
    .then(response => {

        if (!response.ok) {
            return Promise.reject('No se pudo guardar el corte de caja');
        }
        return response.json();
    })
    .then(data => {

        if (data.success) {
            // Generar y guardar PDF del corte
            generarPDFCorte(fechaDesde, fechaHasta, totalVentas, totalContado, 
                           totalEfectivo, totalTransferencias, totalPaypal, 
                           pagosRealizados, fondo);
            setTimeout(() => location.reload(), 1000);
        } else {
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/**
 * Genera un PDF del corte de caja y lo guarda en el servidor.
 * Nombre: CorteCaja_{Vendedor}_{FechaInicio}_a_{FechaCierre}.pdf
 */
function generarPDFCorte(fechaDesde, fechaHasta, totalVentas, totalContado, 
                         totalEfectivo, totalTransferencias, totalPaypal, 
                         pagosRealizados, fondo) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const margenIzquierdo = 10;
    let posicionY = 10;
    const vendedor = nombreUsuario || "No especificado";

    // Título
    doc.setFont("times", "bold");
    doc.setFontSize(18);
    doc.text("CORTE DE CAJA", 105, posicionY, { align: "center" });
    posicionY += 8;
    doc.setFontSize(11);
    doc.setFont("times", "normal");
    doc.text("Cafetería La Hacienda", 105, posicionY, { align: "center" });
    posicionY += 10;

    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Datos generales
    doc.setFontSize(12);
    doc.text(`Vendedor: ${vendedor}`, margenIzquierdo, posicionY);
    posicionY += 7;

    // Formatear fechas para mostrar
    const fechaDesdeFormateada = fechaDesde.replace('T', ' ');
    const fechaHastaFormateada = fechaHasta.replace('T', ' ');
    doc.text(`Periodo: ${fechaDesdeFormateada}  →  ${fechaHastaFormateada}`, margenIzquierdo, posicionY);
    posicionY += 7;
    doc.text(`Fecha de generación: ${new Date().toLocaleString()}`, margenIzquierdo, posicionY);
    posicionY += 12;

    // Línea separadora
    doc.setLineWidth(0.3);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Tabla de desglose
    doc.setFont("times", "bold");
    doc.text("Desglose de Ventas:", margenIzquierdo, posicionY);
    posicionY += 8;

    const columnas = ["Concepto", "Contado", "Calculado"];
    const filas = [
        ["Efectivo", `$${totalContado.toFixed(2)}`, `$${totalEfectivo.toFixed(2)}`],
        ["Transferencias", "-", `$${totalTransferencias.toFixed(2)}`],
        ["Tarjeta", "-", `$${totalPaypal.toFixed(2)}`],
        ["TOTAL", `$${totalContado.toFixed(2)}`, `$${totalVentas.toFixed(2)}`]
    ];

    doc.autoTable({
        startY: posicionY,
        head: [columnas],
        body: filas,
        theme: "striped",
        styles: { fontSize: 10, cellPadding: 4 },
        headStyles: { fillColor: [45, 36, 24], textColor: [255, 255, 255] },
        footStyles: { fontStyle: 'bold' }
    });

    posicionY = doc.lastAutoTable.finalY + 12;

    // Resumen
    doc.setFont("times", "bold");
    doc.setFontSize(12);
    doc.text(`Fondo de Caja: $${fondo.toFixed(2)}`, margenIzquierdo, posicionY);
    posicionY += 7;
    doc.text(`Pagos Realizados: $${pagosRealizados.toFixed(2)}`, margenIzquierdo, posicionY);
    posicionY += 7;
    doc.text(`Total Ventas: $${totalVentas.toFixed(2)}`, margenIzquierdo, posicionY);
    posicionY += 12;

    // Línea final
    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);

    // Generar nombre estructurado
    const vendedorLimpio = vendedor.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]/g, '').replace(/\s+/g, '_');
    const fechaDesdeLimpia = fechaDesde.slice(0, 10); // 2026-05-04
    const fechaHastaLimpia = fechaHasta.slice(0, 10);
    
    let nombreArchivo;
    if (fechaDesdeLimpia === fechaHastaLimpia) {
        nombreArchivo = `CorteCaja_${vendedorLimpio}_${fechaDesdeLimpia}.pdf`;
    } else {
        nombreArchivo = `CorteCaja_${vendedorLimpio}_${fechaDesdeLimpia}_a_${fechaHastaLimpia}.pdf`;
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
            tipo: 'corte'
        })
    }).catch(err => console.error('Error al guardar PDF de corte en servidor:', err));
}
