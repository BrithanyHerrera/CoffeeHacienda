document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase(); // Obtener el término de búsqueda en minúsculas
    const productos = document.querySelectorAll('.producto'); // Seleccionar todos los productos

    productos.forEach(producto => {
        const nombreProducto = producto.querySelector('h3').textContent.toLowerCase(); // Obtener el nombre del producto
        if (nombreProducto.includes(searchTerm)) {
            producto.style.display = ''; // Mostrar el producto si coincide
        } else {
            producto.style.display = 'none'; // Ocultar el producto si no coincide
        }
    });
});