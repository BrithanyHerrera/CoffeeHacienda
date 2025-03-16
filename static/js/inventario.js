const productos = [
    { Id: 1, nombre_producto: "Producto A", stock: 50, stock_minimo: 10, stock_maximo: 100 },
    { Id: 2, nombre_producto: "Producto B", stock: 30, stock_minimo: 5, stock_maximo: 50 },
];

// Mostrar productos en la tabla
function mostrarProductos() {
    const inventarioLista = document.getElementById("inventarioLista");
    inventarioLista.innerHTML = ""; // Limpia la tabla antes de renderizar

    productos.forEach((producto) => {
        const fila = document.createElement("tr");

        const nombre = document.createElement("td");
        nombre.textContent = producto.nombre_producto;

        const stock = document.createElement("td");
        stock.textContent = producto.stock;

        const stockMin = document.createElement("td");
        stockMin.textContent = producto.stock_minimo;

        const stockMax = document.createElement("td");
        stockMax.textContent = producto.stock_maximo;

        const acciones = document.createElement("td");
        const btnEditar = document.createElement("button");
        btnEditar.className = "btnEditarInventario";
        btnEditar.textContent = "✏️";
        btnEditar.addEventListener("click", () => editarInventario(producto.Id));
        acciones.appendChild(btnEditar);

        fila.appendChild(nombre);
        fila.appendChild(stock);
        fila.appendChild(stockMin);
        fila.appendChild(stockMax);
        fila.appendChild(acciones);

        inventarioLista.appendChild(fila);
    });
}

// Filtrar productos por nombre
function filtrarInventario() {
    const filtroNombre = document.getElementById("buscarNombre").value.toLowerCase();
    const productosFiltrados = productos.filter((producto) =>
        producto.nombre_producto.toLowerCase().includes(filtroNombre)
    );

    // Actualizar la tabla con los productos filtrados
    mostrarProductosFiltrados(productosFiltrados);
}

// Mostrar productos filtrados
function mostrarProductosFiltrados(productosFiltrados) {
    const inventarioLista = document.getElementById("inventarioLista");
    inventarioLista.innerHTML = "";

    productosFiltrados.forEach((producto) => {
        const fila = document.createElement("tr");

        const nombre = document.createElement("td");
        nombre.textContent = producto.nombre_producto;

        const stock = document.createElement("td");
        stock.textContent = producto.stock;

        const stockMin = document.createElement("td");
        stockMin.textContent = producto.stock_minimo;

        const stockMax = document.createElement("td");
        stockMax.textContent = producto.stock_maximo;

        const acciones = document.createElement("td");
        const btnEditar = document.createElement("button");
        btnEditar.className = "btnEditarInventario";
        btnEditar.textContent = "✏️";
        btnEditar.addEventListener("click", () => editarInventario(producto.Id));
        acciones.appendChild(btnEditar);

        fila.appendChild(nombre);
        fila.appendChild(stock);
        fila.appendChild(stockMin);
        fila.appendChild(stockMax);
        fila.appendChild(acciones);

        inventarioLista.appendChild(fila);
    });
}

// Abrir modal de edición
function editarInventario(productoId) {
    const producto = productos.find((prod) => prod.Id === productoId);
    if (producto) {
        document.getElementById("idProducto").value = producto.Id;
        document.getElementById("verNombreProducto").textContent = producto.nombre_producto;
        document.getElementById("editarStockInventario").value = producto.stock;
        document.getElementById("agregarStockInventario").value = "";
        document.getElementById("editarStockMinInventario").value = producto.stock_minimo;
        document.getElementById("editarStockMaxInventario").value = producto.stock_maximo;

        document.getElementById("editarInventarioModal").style.display = "block";
    }
}

// Guardar cambios
document.getElementById("formProducto").addEventListener("submit", (e) => {
    e.preventDefault();

    const productoId = parseInt(document.getElementById("idProducto").value);
    const agregarStock = parseInt(document.getElementById("agregarStockInventario").value) || 0;
    const nuevoStockMinimo = parseInt(document.getElementById("editarStockMinInventario").value);
    const nuevoStockMaximo = parseInt(document.getElementById("editarStockMaxInventario").value);

    const producto = productos.find((prod) => prod.Id === productoId);
    if (producto) {
        producto.stock += agregarStock;
        producto.stock_minimo = nuevoStockMinimo;
        producto.stock_maximo = nuevoStockMaximo;
        mostrarProductos();
        cerrarEditarInventario();
    }
});

// Cerrar modal
function cerrarEditarInventario() {
    document.getElementById("editarInventarioModal").style.display = "none";
}

// Inicializar
document.addEventListener("DOMContentLoaded", mostrarProductos);
