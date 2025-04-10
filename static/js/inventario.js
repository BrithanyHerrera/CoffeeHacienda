document.addEventListener("DOMContentLoaded", function () {
    const formProducto = document.getElementById("formProducto");

    // Add CSS styles for inventory alerts
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
        
            // Verificar si hay cambios
            if (ajusteStock === 0 && nuevoStockMin === stockMinActual && nuevoStockMax === stockMaxActual) {
                mostrarAlerta("No se realizaron cambios en el inventario", 'ErrorG');
                cerrarEditarInventario();
                return;
            }
        
            // Enviar datos al servidor
            fetch('/api/inventario/actualizar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: idProducto,
                    stock: nuevoStock,
                    stock_min: nuevoStockMin,
                    stock_max: nuevoStockMax
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    actualizarFilaInventario(idProducto, nuevoStock, nuevoStockMin, nuevoStockMax);
                    mostrarAlerta(data.message); // Mostrar mensaje de éxito
                    cerrarEditarInventario();
                } else {
                    mostrarAlerta("Error al actualizar inventario: " + data.message, 'ErrorG'); // Mostrar mensaje de error
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta("Error al comunicarse con el servidor", 'ErrorG'); // Mostrar mensaje de error
            });
        });
    }
});

// Función para actualizar la fila de inventario con las clases de alerta correctas
function actualizarFilaInventario(idProducto, nuevoStock, nuevoStockMin, nuevoStockMax) {
    const fila = document.querySelector(`tr[data-id="${idProducto}"]`);
    
    // Update row attributes
    fila.setAttribute("data-stock", nuevoStock);
    fila.setAttribute("data-stock-min", nuevoStockMin);
    fila.setAttribute("data-stock-max", nuevoStockMax);

    // Update table cells
    const stockCell = fila.querySelector(".stockProducto");
    stockCell.textContent = nuevoStock;
    fila.querySelector(".stockMinProducto").textContent = nuevoStockMin;
    fila.querySelector(".stockMaxProducto").textContent = nuevoStockMax;
    
    // Obtener la celda de estado
    const estadoCell = fila.querySelector(".estado-inventario");
    estadoCell.classList.remove("estado-critico", "estado-alerta", "estado-aceptable");
    
    // Aplicar las clases de alerta según los nuevos valores
    if (nuevoStock <= nuevoStockMin) {
        // Si el stock es igual o menor al mínimo, es crítico
        estadoCell.classList.add("estado-critico");
        estadoCell.textContent = "CRÍTICO";
    } else if (nuevoStock <= nuevoStockMin + 5) {
        // Si el stock está entre mínimo+1 y mínimo+5, es crítico
        estadoCell.classList.add("estado-critico");
        estadoCell.textContent = "CRÍTICO";
    } else if (nuevoStock <= nuevoStockMin + 10) {
        // Si el stock está entre mínimo+6 y mínimo+10, es alerta
        estadoCell.classList.add("estado-alerta");
        estadoCell.textContent = "ALERTA";
    } else {
        // Si el stock es mayor que mínimo+10, es aceptable
        estadoCell.classList.add("estado-aceptable");
        estadoCell.textContent = "ACEPTABLE";
    }
}

// Función para abrir el modal con los datos del producto seleccionado
function editarInventario(boton) {
    const fila = boton.closest("tr");

    const idProducto = fila.getAttribute("data-id");
    const nombreProducto = fila.getAttribute("data-nombre");
    const stockActual = parseInt(fila.getAttribute("data-stock"));
    const stockMin = parseInt(fila.getAttribute("data-stock-min"));
    const stockMax = parseInt(fila.getAttribute("data-stock-max"));

    document.getElementById("idProducto").value = idProducto;
    document.getElementById("verNombreProducto").textContent = nombreProducto;
    
    const stockInput = document.getElementById("editarStockInventario");
    stockInput.value = stockActual;
    
    // Limpiar clases y estilos anteriores
    stockInput.classList.remove("texto-critico", "texto-alerta");
    stockInput.style.backgroundColor = "";
    
    // Add visual indicator for stock level in the modal
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
    
    // Reset adjustment fields to empty
    document.getElementById("agregarStockInventario").value = "";
    document.getElementById("agregarStockMinimoInventario").value = "";
    document.getElementById("agregarStockMaximoInventario").value = "";

    document.getElementById("editarInventarioModal").style.display = "flex";
}

// Función para cerrar el modal de edición
function cerrarEditarInventario() {
    document.getElementById("editarInventarioModal").style.display = "none";
}

// Función para filtrar productos por nombre
function filtrarInventario() {
    const buscarNombre = document.getElementById("buscarNombre").value.toLowerCase();
    const filas = document.querySelectorAll("#inventarioLista tr");

    filas.forEach((fila) => {
        const nombreProducto = fila.getAttribute("data-nombre").toLowerCase();
        fila.style.display = nombreProducto.includes(buscarNombre) ? "" : "none";
    });
}

// Función para reestablecer filtros
function reestablecerFiltrosInventario() {
    document.getElementById("buscarNombre").value = "";
    filtrarInventario();
}

function mostrarAlerta(mensaje, tipo = 'ExitoG') {
    const contenedor = document.querySelector('.contenedorAlertas') || crearContenedorAlertas();

    const alerta = document.createElement('div');
    alerta.className = `alertaGeneral alerta-${tipo}`;

    // Configurar icono y título según el tipo de alerta
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

    // Aumentar el tiempo de espera a 10 segundos
    setTimeout(() => alerta.remove(), 3000); // Eliminar después de 10s
}


function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
}