document.addEventListener("DOMContentLoaded", function () {
    const formProducto = document.getElementById("formProducto");

    if (formProducto) {
        formProducto.addEventListener("submit", function (event) {
            event.preventDefault();

            const idProducto = document.getElementById("idProducto").value;
            const agregarStock = parseInt(document.getElementById("agregarStockInventario").value) || 0;
            const nuevoStockMinimo = parseInt(document.getElementById("agregarStockMinimoInventario").value) || 0;
            const nuevoStockMaximo = parseInt(document.getElementById("agregarStockMaximoInventario").value) || 0;

            const fila = document.querySelector(`tr[data-id="${idProducto}"]`);
            const stockActual = parseInt(fila.getAttribute("data-stock"));
            const nuevoStock = stockActual + agregarStock;

            // Actualizar los atributos de la fila
            fila.setAttribute("data-stock", nuevoStock);
            fila.setAttribute("data-stock-min", nuevoStockMinimo);
            fila.setAttribute("data-stock-max", nuevoStockMaximo);

            // Actualizar la tabla
            fila.querySelector(".stockProducto").textContent = nuevoStock;
            fila.querySelector(".stockMinProducto").textContent = nuevoStockMinimo;
            fila.querySelector(".stockMaxProducto").textContent = nuevoStockMaximo;

            alert("Inventario actualizado correctamente.");
            cerrarEditarInventario();
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
