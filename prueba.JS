{% extends "sidebar.html" %}

{% block title %}Gestión Productos{% endblock %}

{% block content %}
<main class="contenidoGeneral">
    <!-- Asegúrate de que el botón de agregar producto tenga la clase correcta -->
    <div class="contenedorTitulo">
        <h1>Gestión de Productos</h1>
        <button class="btnAgregarProducto" onclick="abrirEAModal()">➕ Agregar Producto</button>
    </div>
    
    <div class="contenedorGestionProductos">
        <section class="listaProductos">
            <table>
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Tamaño</th>
                        <th>Precio</th>
                        <th>Stock</th>
                        <th>Categoría</th>
                        <th>Imagen</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody id="productosLista">
                    {% for producto in productos %}
                    <tr>
                        <td>{{ producto.nombre_producto }}</td>
                        <td class="tamano-producto" data-producto-id="{{ producto.Id }}">
                            <span class="cargando">Cargando...</span>
                        </td>
                        <td>${{ producto.precio }}</td>
                        <td>{{ producto.stock }}</td>
                        <td>{{ producto.categoria }}</td>
                        <td>
                            {% if producto.ruta_imagen %}
                            <img src="{{ producto.ruta_imagen }}" alt="{{ producto.nombre_producto }}" class="imagenProducto">
                            {% else %}
                            <img src="/static/images/default-product.jpg" alt="Sin imagen" class="imagenProducto">
                            {% endif %}
                        </td>
                        <td>
                            <button class="btnVerProducto" onclick="abrirVerProducto(
                                {{ producto.Id }}, 
                                '{{ producto.nombre_producto }}', 
                                '{{ producto.descripcion|default('', true) }}', 
                                {{ producto.precio }}, 
                                {{ producto.stock }}, 
                                {{ producto.stock_minimo }}, 
                                {{ producto.stock_maximo }}, 
                                '{{ producto.categoria }}', 
                                '{{ producto.ruta_imagen|default('', true) }}'
                            )">👁️</button>
                            <button class="btnEditarProducto" onclick="abrirEAModal(
                                {{ producto.Id }}, 
                                '{{ producto.nombre_producto }}', 
                                '{{ producto.descripcion|default('', true) }}', 
                                {{ producto.precio }}, 
                                {{ producto.stock }}, 
                                {{ producto.stock_minimo }}, 
                                {{ producto.stock_maximo }}, 
                                {{ producto.categoria_id }}, 
                                '{{ producto.ruta_imagen|default('', true) }}'
                            )">✏️</button>
                            <button class="btnEliminarProducto" onclick="eliminarProducto({{ producto.Id }})">🗑️</button>                            
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>

        <!-- Modal de Agregar/Editar Producto -->
        <section class="modal" id="productoModal">
            <section class="contenedorModal">
                <span class="cerrar" onclick="cerrarEAModal()">&times;</span>
                <h3 class="tituloModal" id="tituloModal">Agregar Producto</h3>
                <form id="formProducto" enctype="multipart/form-data" onsubmit="guardarProducto(event)">
                    <input type="hidden" id="idProducto" name="id">
                    
                    <div class="form-group">
                        <label for="nombreProducto">Nombre:</label>
                        <input type="text" id="nombreProducto" name="nombre" required>
                    </div>
        
                    <div class="form-group">
                        <label for="descripcionProducto">Descripción:</label>
                        <textarea id="descripcionProducto" name="descripcion" rows="3"></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group half">
                            <label for="precioProducto">Precio Base:</label>
                            <input type="number" id="precioProducto" name="precio" step="0.01" required>
                        </div>
                        
                        <div class="form-group half">
                            <label for="stockProducto">Stock:</label>
                            <input type="number" id="stockProducto" name="stock" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group half">
                            <label for="stockMinProducto">Stock Mínimo:</label>
                            <input type="number" id="stockMinProducto" name="stockMin" value="10">
                        </div>
                        
                        <div class="form-group half">
                            <label for="stockMaxProducto">Stock Máximo:</label>
                            <input type="number" id="stockMaxProducto" name="stockMax" value="100">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="categoriaProducto">Categoría:</label>
                        <select id="categoriaProducto" name="categoria" required>
                            <option value="">Seleccione una categoría</option>
                            {% for categoria in categorias %}
                            <option value="{{ categoria.Id }}">{{ categoria.categoria }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <!-- Reemplazar la sección de precios por tamaño con un selector de tamaño -->
                    <div class="form-group">
                        <label for="tamanoProducto">Tamaño:</label>
                        <select id="tamanoProducto" name="tamano" required>
                            <option value="">Seleccione un tamaño</option>
                            {% for tamano in tamanos %}
                            <option value="{{ tamano.Id }}">{{ tamano.tamano }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="imagenProducto">Imagen:</label>
                        <input type="file" id="imagenProducto" name="imagen" accept="image/*" onchange="mostrarImagenPreview(event)">
                        <div class="imagen-container">
                            <img id="imagenActual" class="imagenProducto" src="" alt="Imagen Actual" style="display: none; max-width: 200px; margin-top: 10px;">
                            <img id="imagenPreview" class="imagenProducto" src="" alt="Vista previa" style="display: none; max-width: 200px; margin-top: 10px;">
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="cancelarBtn" onclick="cerrarEAModal()">Cancelar</button>
                        <button class="guardarBtn" type="submit">Guardar</button>
                    </div>
                </form>
            </section>
        </section>
        
        <!-- Modal de Ver Producto -->
        <section class="modal" id="verModalProducto">
            <section class="contenedorModal">
                <span class="cerrar" onclick="cerrarVerProducto()">&times;</span>
                <h3 id="verTituloModal">Ver Producto</h3>

                <!-- En el modal de Ver Producto -->
                <section id="verDetallesProducto">
                    <p><strong>ID:</strong> <span id="verIDProducto"></span></p>
                    <p><strong>Nombre:</strong> <span id="verNombreProducto"></span></p>
                    <p><strong>Descripción:</strong> <span id="verDescripcionProducto"></span></p>
                    <p><strong>Precio:</strong> $<span id="verPrecioProducto"></span></p>
                    <p><strong>Stock:</strong> <span id="verStockProducto"></span></p>
                    <p><strong>Stock Mínimo:</strong> <span id="verStockMinProducto"></span></p>
                    <p><strong>Stock Máximo:</strong> <span id="verStockMaxProducto"></span></p>
                    <p><strong>Categoría:</strong> <span id="verCategoriaProducto"></span></p>
                    <p><strong>Tamaño:</strong> <span id="verTamanoProducto"></span></p>
                    
                    <p><strong>Imagen:</strong></p>
                    <img id="verImagenProducto" class="imagenProducto" alt="Imagen del Producto" style="max-width: 300px;">
                </section>
            </section>
        </section>
    </div>
    
    <script src="{{ url_for('static', filename='js/gestionProductos.js') }}"></script>
</main>
{% endblock %}