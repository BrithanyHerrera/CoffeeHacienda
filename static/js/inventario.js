let datosAjustePendiente = null;

document.addEventListener("DOMContentLoaded", function () {
    const formProducto = document.getElementById("formProducto");

    // Agregar estilos CSS para alertas de inventario
    const style = document.createElement('style');
    style.textContent = `
        .nivel-critico {
            background-color: rgba(255, 200, 200, 0.3);
        }
        .nivel-alerta {
            background-color: rgba(255, 243, 205, 0.3);
        }
        .texto-critico {
            color: #dc3545;
            font-weight: bold;
        }
        .texto-alerta {
            color: #fd7e14;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);

    if (formProducto) {
        formProducto.addEventListener("submit", function (event) {
            event.preventDefault();
        
            const idProducto = document.getElementById("idProducto").value;
            const stockActual = parseInt(document.getElementById("editarStockInventario").value) || 0;
            const stockMinActual = parseInt(document.getElementById("editarStockMinInventario").value) || 0;
            const stockMaxActual = parseInt(document.getElementById("editarStockMaxInventario").value) || 0;
        
            const ajusteStock = document.getElementById("agregarStockInventario").value === "" ? 0 : 
                                parseInt(document.getElementById("agregarStockInventario").value) || 0;
            const nuevoStockMin = document.getElementById("agregarStockMinimoInventario").value === "" ? 
                                  stockMinActual : parseInt(document.getElementById("agregarStockMinimoInventario").value) || 0;
            const nuevoStockMax = document.getElementById("agregarStockMaximoInventario").value === "" ? 
                                  stockMaxActual : parseInt(document.getElementById("agregarStockMaximoInventario").value) || 0;
        
            const nuevoStock = stockActual + ajusteStock;
        
            // Validar que el nuevo stock no sea negativo
            if (nuevoStock < 0) {
                mostrarAlerta("El stock no puede ser negativo. Ajuste el valor.", 'ErrorG');
                return;
            }
            
            // Validar que el stock mínimo no sea mayor que el stock máximo
            if (nuevoStockMin > nuevoStockMax) {
                mostrarAlerta("El stock mínimo no puede ser mayor que el stock máximo.", 'ErrorG');
                return;
            }
            
            // Validar que el stock máximo no sea menor que el stock mínimo
            if (nuevoStockMax < nuevoStockMin) {
                mostrarAlerta("El stock máximo no puede ser menor que el stock mínimo.", 'ErrorG');
                return;
            }
        
            // Verificar si hay cambios
            if (ajusteStock === 0 && nuevoStockMin === stockMinActual && nuevoStockMax === stockMaxActual) {
                mostrarAlerta("No se realizaron cambios en el inventario", 'ErrorG');
                cerrarEditarInventario();
                return;
            }

            const nombreElement = document.getElementById("verNombreProducto");
            const nombreProducto = nombreElement ? nombreElement.textContent.trim() : "este producto";

            datosAjustePendiente = {
                id: idProducto,
                stock: nuevoStock,
                stock_min: nuevoStockMin,
                stock_max: nuevoStockMax,
                nombre: nombreProducto
            };

            abrirConfirmacionAjuste(nombreProducto);
        });
    }
});

// Función para abrir modal de confirmación con motivo obligatorio
function abrirConfirmacionAjuste(nombreProducto) {
    const modal = document.getElementById("confirmacionModal");
    const mensaje = document.getElementById("mensajeConfirmacion");
    const motivo = document.getElementById("motivoAjuste");

    if (mensaje) {
        mensaje.textContent = `¿Estás seguro de modificar las existencias/límites de ${nombreProducto}?`;
    }
    if (motivo) {
        motivo.value = "";
    }
    if (modal) {
        modal.style.display = "flex";
        if (motivo) {
            setTimeout(function () {
                motivo.focus();
            }, 50);
        }
    }
}

// Función para confirmar y enviar el ajuste con motivo
function confirmarAjusteInventario() {
    if (!datosAjustePendiente) {
        cerrarConfirmacionModal();
        return;
    }

    const motivoInput = document.getElementById("motivoAjuste");
    const motivo = motivoInput ? motivoInput.value.trim() : "";

    if (!motivo) {
        mostrarAlerta("El motivo del ajuste es obligatorio.", "ErrorG");
        if (motivoInput) {
            motivoInput.focus();
        }
        return;
    }

    const btnConfirmar = document.getElementById("btnConfirmar");
    if (btnConfirmar) {
        btnConfirmar.disabled = true;
    }

    const payload = {
        id: datosAjustePendiente.id,
        stock: datosAjustePendiente.stock,
        stock_min: datosAjustePendiente.stock_min,
        stock_max: datosAjustePendiente.stock_max,
        motivo: motivo
    };

    fetch('/api/inventario/actualizar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json().then(data => ({ ok: response.ok, status: response.status, data })))
    .then(({ ok, data }) => {
        if (data && data.success) {
            actualizarFilaInventario(
                datosAjustePendiente.id,
                datosAjustePendiente.stock,
                datosAjustePendiente.stock_min,
                datosAjustePendiente.stock_max
            );
            mostrarAlerta(data.message);
            cerrarConfirmacionModal();
            cerrarEditarInventario();
            datosAjustePendiente = null;
        } else {
            const mensajeError = (data && data.message) ? data.message : "Error desconocido";
            mostrarAlerta("Error al actualizar inventario: " + mensajeError, 'ErrorG');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta("Error al comunicarse con el servidor", 'ErrorG');
    })
    .finally(() => {
        if (btnConfirmar) {
            btnConfirmar.disabled = false;
        }
    });
}

// Función para cerrar el modal de confirmación
function cerrarConfirmacionModal() {
    const modal = document.getElementById("confirmacionModal");
    if (modal) {
        modal.style.display = "none";
    }
    const motivo = document.getElementById("motivoAjuste");
    if (motivo) {
        motivo.value = "";
    }
}

// Función para actualizar la fila de inventario con las clases de alerta correctas
function actualizarFilaInventario(idProducto, nuevoStock, nuevoStockMin, nuevoStockMax) {
    const fila = document.querySelector(`tr[data-id="${idProducto}"]`);
    if (!fila) return;
    
    // Actualizar atributos de la fila
    fila.setAttribute("data-stock", nuevoStock);
    fila.setAttribute("data-stock-min", nuevoStockMin);
    fila.setAttribute("data-stock-max", nuevoStockMax);

    // Actualizar celdas de la tabla
    const stockCell = fila.querySelector(".stockProducto");
    if (stockCell) stockCell.textContent = nuevoStock;
    const minCell = fila.querySelector(".stockMinProducto");
    if (minCell) minCell.textContent = nuevoStockMin;
    const maxCell = fila.querySelector(".stockMaxProducto");
    if (maxCell) maxCell.textContent = nuevoStockMax;
    
    // Obtener la celda de estado
    const estadoCell = fila.querySelector(".estado-inventario");
    if (estadoCell) {
        estadoCell.classList.remove("estado-critico", "estado-alerta", "estado-aceptable");
        
        // Aplicar las clases de alerta según los nuevos valores
        if (nuevoStock <= nuevoStockMin) {
            estadoCell.classList.add("estado-critico");
            estadoCell.textContent = "CRÍTICO";
        } else if (nuevoStock <= nuevoStockMin + 5) {
            estadoCell.classList.add("estado-critico");
            estadoCell.textContent = "CRÍTICO";
        } else if (nuevoStock <= nuevoStockMin + 10) {
            estadoCell.classList.add("estado-alerta");
            estadoCell.textContent = "ALERTA";
        } else {
            estadoCell.classList.add("estado-aceptable");
            estadoCell.textContent = "ACEPTABLE";
        }
    }
}

// Función para abrir el modal con los datos del producto seleccionado
function editarInventario(boton) {
    const fila = boton.closest("tr");
    if (!fila) return;

    const idProducto = fila.getAttribute("data-id");
    const nombreProducto = fila.getAttribute("data-nombre");
    const stockActual = parseInt(fila.getAttribute("data-stock")) || 0;
    const stockMin = parseInt(fila.getAttribute("data-stock-min")) || 0;
    const stockMax = parseInt(fila.getAttribute("data-stock-max")) || 0;

    document.getElementById("idProducto").value = idProducto;
    document.getElementById("verNombreProducto").textContent = nombreProducto;
    
    const stockInput = document.getElementById("editarStockInventario");
    stockInput.value = stockActual;
    
    // Limpiar clases y estilos anteriores
    stockInput.classList.remove("texto-critico", "texto-alerta");
    stockInput.style.backgroundColor = "";
    
    // Agregar indicador visual del nivel de stock en el modal
    if (stockActual <= stockMin) {
        stockInput.classList.add("texto-critico");
        stockInput.style.backgroundColor = "rgba(255, 200, 200, 0.3)";
    } else if (stockActual <= stockMin + 5) {
        stockInput.classList.add("texto-critico");
        stockInput.style.backgroundColor = "rgba(255, 200, 200, 0.3)";
    } else if (stockActual <= stockMin + 10) {
        stockInput.classList.add("texto-alerta");
        stockInput.style.backgroundColor = "rgba(255, 243, 205, 0.3)";
    }
    
    document.getElementById("editarStockMinInventario").value = stockMin;
    document.getElementById("editarStockMaxInventario").value = stockMax;
    
    // Limpiar campos de ajuste
    document.getElementById("agregarStockInventario").value = "";
    document.getElementById("agregarStockMinimoInventario").value = "";
    document.getElementById("agregarStockMaximoInventario").value = "";

    document.getElementById("editarInventarioModal").style.display = "flex";
}

// Función para cerrar el modal de edición
function cerrarEditarInventario() {
    const modal = document.getElementById("editarInventarioModal");
    if (modal) {
        modal.style.display = "none";
    }
    cerrarConfirmacionModal();
    datosAjustePendiente = null;
}

// Función para filtrar productos por nombre
function filtrarInventario() {
    const buscarNombre = document.getElementById("buscarNombre").value.toLowerCase();
    const filas = document.querySelectorAll("#inventarioLista tr");

    filas.forEach((fila) => {
        const nombreAttr = fila.getAttribute("data-nombre");
        if (nombreAttr) {
            fila.style.display = nombreAttr.toLowerCase().includes(buscarNombre) ? "" : "none";
        }
    });
}

// Función para reestablecer filtros
function reestablecerFiltrosInventario() {
    document.getElementById("buscarNombre").value = "";
    filtrarInventario();
}
