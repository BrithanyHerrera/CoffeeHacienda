function openModal(id = null, name = '', price = '') {
    document.getElementById('productId').value = id;
    document.getElementById('productName').value = name;
    document.getElementById('productPrice').value = price;
    document.getElementById('modalTitle').innerText = id ? 'Editar Producto' : 'Agregar Producto';
    document.getElementById('productModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('productModal').style.display = 'none';
}

document.getElementById('productForm').addEventListener('submit', function(event) {
    event.preventDefault();
    closeModal();
});

function viewProduct(id, name, price, image) {
    // Establecer el contenido en el modal de ver producto
    document.getElementById('viewProductName').textContent = name;
    document.getElementById('viewProductPrice').textContent = price;
    document.getElementById('viewProductImage').src = image;
    
    // Mostrar el modal de ver producto
    document.getElementById('viewProductModal').style.display = 'flex';
}

function closeViewModal() {
    // Cerrar el modal de ver producto
    document.getElementById('viewProductModal').style.display = 'none';
}

