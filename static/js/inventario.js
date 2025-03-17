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
            
            // Get values from input fields, defaulting to 0 if empty
            const ajusteStock = document.getElementById("agregarStockInventario").value === "" ? 0 : 
                               parseInt(document.getElementById("agregarStockInventario").value) || 0;
            const nuevoStockMin = document.getElementById("agregarStockMinimoInventario").value === "" ? 
                                 stockMinActual : parseInt(document.getElementById("agregarStockMinimoInventario").value) || 0;
            const nuevoStockMax = document.getElementById("agregarStockMaximoInventario").value === "" ? 
                                 stockMaxActual : parseInt(document.getElementById("agregarStockMaximoInventario").value) || 0;
            
            // Calculate new stock value
            const nuevoStock = stockActual + ajusteStock;
            
            // Validate that the new stock is not negative
            if (nuevoStock < 0) {
                alert("El stock no puede ser negativo. Ajuste el valor.");
                return;
            }

            // Check if there are any changes
            if (ajusteStock === 0 && nuevoStockMin === stockMinActual && nuevoStockMax === stockMaxActual) {
                alert("No se realizaron cambios en el inventario");
                cerrarEditarInventario();
                return;
            }

            // Send data to server
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
                    // Usar la función para actualizar la fila con las clases correctas
                    actualizarFilaInventario(idProducto, nuevoStock, nuevoStockMin, nuevoStockMax);
                    
                    alert(data.message);
                    cerrarEditarInventario();
                } else {
                    alert("Error al actualizar inventario: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("Error al comunicarse con el servidor");
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
    
    // Eliminar todas las clases de alerta existentes
    fila.classList.remove("nivel-critico", "nivel-alerta");
    stockCell.classList.remove("texto-critico", "texto-alerta");
    
    // Aplicar las clases de alerta según los nuevos valores
    if (nuevoStock <= nuevoStockMin) {
        // Si el stock es igual o menor al mínimo, es crítico
        fila.classList.add("nivel-critico");
        stockCell.classList.add("texto-critico");
    } else if (nuevoStock <= nuevoStockMin + 5) {
        // Si el stock está entre mínimo+1 y mínimo+5, es crítico
        fila.classList.add("nivel-critico");
        stockCell.classList.add("texto-critico");
    } else if (nuevoStock <= nuevoStockMin + 10) {
        // Si el stock está entre mínimo+6 y mínimo+10, es alerta
        fila.classList.add("nivel-alerta");
        stockCell.classList.add("texto-alerta");
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
