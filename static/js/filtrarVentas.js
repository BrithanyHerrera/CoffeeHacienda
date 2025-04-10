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

    if (diferenciaCheque < 0) {
        diffChequeInput.style.color = 'white';
        diffChequeInput.style.backgroundColor = '#e74c3c';
        diferenciasNegativas = true;
    }

    if (diferenciaVales < 0) {
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
});


document.getElementById('btnRealizarCorte').addEventListener('click', function (event) {
    event.preventDefault();  // Prevenir el comportamiento predeterminado (como redirección o descarga)

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

    // Validaciones de campos
    if (!fechaDesde || !fechaHasta) {
        alert("Por favor, selecciona las fechas de inicio y cierre.");
        return;
    }

    if (
        isNaN(totalVentas) || isNaN(totalContado) || isNaN(totalEfectivo) ||
        isNaN(totalTransferencias) || isNaN(totalPaypal) ||
        isNaN(pagosRealizados) || isNaN(fondo)
    ) {
        alert("Por favor, asegúrate de que todos los campos numéricos estén completos y sean válidos.");
        return;
    }

    // Verificación de que los pagos no exceden el fondo disponible
    const totalDisponible = totalVentas + fondo;
    if (pagosRealizados > totalDisponible) {
        alert(`❌ No se puede realizar el corte.\nLos pagos realizados (${pagosRealizados}) superan el total disponible (${totalDisponible}).`);
        
        return;  // Terminar la función sin continuar con la descarga o envío
    }

    // Si los pagos realizados no superan el total disponible, continuar con la lógica de guardado
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

    // Lógica para enviar los datos y generar el PDF (solo si los pagos son válidos)
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
    .then(response => response.json())  // Manejo de respuesta JSON
    .then(data => {
        if (data.success) {
           // Mostrar mensaje de éxito
           mostrarNotificacion('Venta registrada exitosamente', 'success');
            
           // Generar PDF solo si la venta fue exitosa
           generarCorteCajaPDF();
            location.reload();  // Recargar la página
        } else {
            alert("Error al realizar el corte: " + data.error);
        }
    })
    .catch(error => {
        alert('Error al guardar el corte de caja: ' + error);
    });
});

function generarCorteCajaPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Verificar si autoTable está cargado correctamente
    if (!doc.autoTable) {
        console.error("autoTable no está cargado correctamente.");
        alert("Error al generar el PDF. Asegúrate de incluir la librería jsPDF.");
        return;
    }

    const margenIzquierdo = 10;
    let posicionY = 10;

    const fechaHora = new Date().toLocaleString();
    const nombreVendedor = "Administrador"; // Puedes hacerlo dinámico si tienes login

    doc.setFont("times", "normal");

    doc.setFontSize(16);
    doc.text("CORTE DE CAJA", 105, posicionY, { align: "center" });
    posicionY += 10;

    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    doc.setFontSize(12);
    doc.text(`Fecha y Hora: ${fechaHora}`, margenIzquierdo, posicionY);
    posicionY += 6;
    doc.text(`Vendedor: ${nombreVendedor}`, margenIzquierdo, posicionY);
    posicionY += 6;

    doc.setLineWidth(0.5);
    doc.line(margenIzquierdo, posicionY, 200, posicionY);
    posicionY += 10;

    // Obtener los valores de los pagos y datos
    const efectivo = document.getElementById('contado').value;
    const calculadoEfectivo = document.getElementById('calculado').value;
    const diferenciaEfectivo = document.getElementById('diferencia').value;

    const transferencia = document.getElementById('cheque').value;
    const calculadoTransf = document.getElementById('calculadoCheque').value;
    const diferenciaTransf = document.getElementById('diferenciaCheque').value;

    const paypal = document.getElementById('vales').value;
    const calculadoPaypal = document.getElementById('calculadoVales').value;
    const diferenciaPaypal = document.getElementById('diferenciaVales').value;

    const total = document.getElementById('total').value;
    const total2 = document.getElementById('total2').value;
    const totalDiferencia = document.getElementById('totalDiferencia').value;

    const fondo = document.getElementById('fondo') ? document.getElementById('fondo').value : '0';
    const pagosRealizados = document.getElementById('pagos_realizados').value;

    // Crear la tabla de corte de caja
    const columnas = ["Método", "Contado", "Calculado", "Diferencia"];
    const filas = [
        ["Efectivo", `$${efectivo}`, `$${calculadoEfectivo}`, `$${diferenciaEfectivo}`],
        ["Transferencias", `$${transferencia}`, `$${calculadoTransf}`, `$${diferenciaTransf}`],
        ["Tarjeta", `$${paypal}`, `$${calculadoPaypal}`, `$${diferenciaPaypal}`],
        ["TOTAL", `$${total}`, `$${total2}`, `$${totalDiferencia}`],
        ["", "", "", ""],
        ["FONDO", `$${fondo}`, "", ""],
        ["PAGOS REALIZADOS", `$${pagosRealizados}`, "", ""]
    ];

    // Crear la tabla en el PDF
    doc.autoTable({
        startY: posicionY,
        head: [columnas],
        body: filas,
        styles: {
            halign: 'center',
        },
        headStyles: {
            fillColor: [189, 215, 238], // Azul claro
            textColor: 0,
            fontStyle: 'bold'
        }
    });

    // Guardar el PDF
    doc.save("corte_de_caja.pdf");
}

function verDetallesCorte(id) {
    fetch(`/api/corteCaja/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const corte = data.corte;

                // Rellenar los campos del modal con la información del corte
                document.getElementById('verIdCorte').textContent = corte.Id;
                document.getElementById('detalleFechaInicio').textContent = corte.fecha_hora_inicio || '---';
                document.getElementById('detalleFechaCierre').textContent = corte.fecha_hora_cierre || '---';
                document.getElementById('detalleFondo').textContent = corte.fondo.toFixed(2);
                document.getElementById('detalleContado').textContent = corte.total_contado.toFixed(2);
                document.getElementById('detalleCalculado').textContent = corte.total_ventas.toFixed(2);
                document.getElementById('detalleEfectivo').textContent = corte.total_efectivo.toFixed(2);
                document.getElementById('detalleTransferencias').textContent = corte.total_transferencias.toFixed(2);
                document.getElementById('detallePaypal').textContent = corte.total_paypal.toFixed(2);
                document.getElementById('detallePagosRealizados').textContent = corte.pagos_realizados.toFixed(2);

                // Mostrar el modal con Bootstrap
                const modal = new bootstrap.Modal(document.getElementById('modalDetallesCorte'));
                modal.show();
            } else {
                alert("No se pudo obtener la información del corte.");
            }
        })
        .catch(error => {
            console.error('Error al obtener los detalles del corte:', error);
            alert("Ocurrió un error.");
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
