document.addEventListener("DOMContentLoaded", function () {
    const formProducto = document.getElementById("formProducto");

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
                    // Update the interface
                    const fila = document.querySelector(`tr[data-id="${idProducto}"]`);
                    
                    // Update row attributes
                    fila.setAttribute("data-stock", nuevoStock);
                    fila.setAttribute("data-stock-min", nuevoStockMin);
                    fila.setAttribute("data-stock-max", nuevoStockMax);

                    // Update table cells
                    fila.querySelector(".stockProducto").textContent = nuevoStock;
                    fila.querySelector(".stockMinProducto").textContent = nuevoStockMin;
                    fila.querySelector(".stockMaxProducto").textContent = nuevoStockMax;

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

// Función para abrir el modal con los datos del producto seleccionado
function editarInventario(boton) {
    const fila = boton.closest("tr");

    document.getElementById("idProducto").value = fila.getAttribute("data-id");
    document.getElementById("verNombreProducto").textContent = fila.getAttribute("data-nombre");
    document.getElementById("editarStockInventario").value = fila.getAttribute("data-stock");
    document.getElementById("editarStockMinInventario").value = fila.getAttribute("data-stock-min");
    document.getElementById("editarStockMaxInventario").value = fila.getAttribute("data-stock-max");
    
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
