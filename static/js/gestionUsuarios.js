// Función para abrir el modal de Edición y Agregar usuario.
function abrirEAModal(id = null, nombre = '', correo = '', tipoPrivilegio = '') {
    // Si es edición, obtener los datos completos del usuario incluyendo la contraseña
    if (id) {
        fetch(`/api/usuarios/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Rellenar los campos del modal con los valores recibidos
                    document.getElementById('idUsuario').value = id;
                    document.getElementById('nombreUsuario').value = nombre;
                    document.getElementById('correoUsuario').value = correo;
                    document.getElementById('tipoPrivilegio').value = tipoPrivilegio;
                    document.getElementById('contrasenaUsuario').value = data.usuario.contrasena;
                    
                    // Establecer el título del modal
                    document.getElementById('tituloModal').innerText = 'Editar Usuario';
                    
                    // Mostrar el modal de agregar/editar usuario
                    document.getElementById('usuarioModal').style.display = 'flex';
                } else {
                    mostrarAlerta('Error al obtener los datos del usuario', 'ErrorG');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('Error al obtener los datos del usuario', 'ErrorG');
            });
    } else {
        // Si es agregar nuevo usuario, simplemente mostrar el modal con campos vacíos
        document.getElementById('idUsuario').value = '';
        document.getElementById('nombreUsuario').value = '';
        document.getElementById('correoUsuario').value = '';
        document.getElementById('tipoPrivilegio').value = '';
        document.getElementById('contrasenaUsuario').value = '';
        
        // Establecer el título del modal
        document.getElementById('tituloModal').innerText = 'Agregar Usuario';
        
        // Mostrar el modal de agregar/editar usuario
        document.getElementById('usuarioModal').style.display = 'flex';
    }
}

// Cerrar el modal de edición/agregar
function cerrarEAModal() {
    document.getElementById('usuarioModal').style.display = 'none';
}

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencia al formulario
    const formUsuario = document.getElementById('formUsuario');
    
    if (formUsuario) {
        formUsuario.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const userData = {
                id: document.getElementById('idUsuario').value || null,
                nombre: document.getElementById('nombreUsuario').value,
                correo: document.getElementById('correoUsuario').value,
                contrasena: document.getElementById('contrasenaUsuario').value,
                tipoPrivilegio: document.getElementById('tipoPrivilegio').value
            };
            
            fetch('/api/usuarios/guardar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.require_validation) {
                        // Si requiere validación, mostrar mensaje y redirigir
                        mostrarAlerta(data.message, 'ExitoG');
                        setTimeout(() => {
                            window.location.href = `/validar-usuario?email=${encodeURIComponent(data.email)}`;
                        }, 1500);
                    } else {
                        // Si no requiere validación, mostrar mensaje y recargar
                        mostrarAlerta(data.message, 'ExitoG');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    }
                } else {
                    mostrarAlerta(data.message, 'ErrorG');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarAlerta('Error al guardar el usuario', 'ErrorG');
            });
            
            // No cerramos el modal inmediatamente para permitir ver los errores
            // Solo cerramos si la operación fue exitosa
        });
    }
});

let idUsuarioAEliminar = null; // Variable global para almacenar el ID del usuario a eliminar

function confirmarEliminar(id) {
    idUsuarioAEliminar = id;
    document.getElementById('mensajeConfirmacion').textContent = '¿Estás seguro de que deseas desactivar este usuario?';
    document.getElementById('confirmacionModal').style.display = 'flex';
}

function confirmarEliminacion() {
    fetch(`/gestionUsuarios/eliminar/${idUsuarioAEliminar}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarAlerta('Usuario desactivado exitosamente', 'ExitoG');
            setTimeout(() => {
                location.reload();
            }, 3000);
        } else {
            mostrarAlerta(data.message, 'ErrorG');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al desactivar el usuario', 'ErrorG');
    });

    cerrarConfirmacionModal();
}

function cerrarConfirmacionModal() {
    document.getElementById('confirmacionModal').style.display = 'none'; // Ocultar el modal de confirmación
}

// Función para abrir el modal de ver usuario.
function abrirVerUsuario(id, nombre, correo, tipoPrivilegio, fechaRegistro) {
    // Obtener la contraseña del usuario por su ID
    fetch(`/api/usuarios/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Establecer el contenido en el modal de ver usuario
                document.getElementById('verIDUsuario').textContent = id;
                document.getElementById('verNombreUsuario').textContent = nombre;
                document.getElementById('verCorreoUsuario').textContent = correo;
                document.getElementById('verTipoPrivilegio').textContent = tipoPrivilegio;
                document.getElementById('verFechaRegistro').textContent = fechaRegistro;
                document.getElementById('verContrasenaUsuario').textContent = data.usuario.contrasena;
                
                // Establecer inicial del avatar
                const avatar = document.getElementById('avatarUsuario');
                avatar.textContent = nombre.charAt(0).toUpperCase();
                
                // Mostrar el modal de ver usuario
                document.getElementById('verModalUsuario').style.display = 'flex';
            } else {
                mostrarAlerta('Error al obtener los datos del usuario', 'ErrorG');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al obtener los datos del usuario', 'ErrorG');
        });
}

// Cerrar el modal de ver usuario
function cerrarVerUsuario() {
    document.getElementById('verModalUsuario').style.display = 'none';
}

function toggleContrasena() {
    const contrasenaInput = document.getElementById('contrasenaUsuario');
    const toggleIcon = document.querySelector('.toggleContrasena i');

    if (contrasenaInput.type === 'password') {
        contrasenaInput.type = 'text';
        toggleIcon.className = 'bx bx-hide';
    } else {
        contrasenaInput.type = 'password';
        toggleIcon.className = 'bx bx-show';
    }
}

// Función para filtrar usuarios automáticamente
function buscarUsuario() {
    const nombreUsuario = document.getElementById('buscarUsuario').value.toLowerCase();
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    // Filtra las filas en la tabla
    const filas = document.querySelectorAll('.listaUsuarios tbody tr');
    filas.forEach(fila => {
        const usuarioNombre = fila.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const fechaRegistro = fila.querySelector('td:nth-child(4)').textContent;

        // Comprueba si coincide con el nombre y las fechas
        const coincideNombre = nombreUsuario === '' || usuarioNombre.includes(nombreUsuario);
        const coincideFechaInicio = fechaInicio === '' || new Date(fechaRegistro) >= new Date(fechaInicio);
        const coincideFechaFin = fechaFin === '' || new Date(fechaRegistro) <= new Date(fechaFin);

        if (coincideNombre && coincideFechaInicio && coincideFechaFin) {
            fila.style.display = ''; // Muestra la fila
        } else {
            fila.style.display = 'none'; // Oculta la fila
        }
    });
}

// Función para reestablecer los filtros y mostrar todos los registros
function reestablecerFiltros() {
    document.getElementById('buscarUsuario').value = '';
    document.getElementById('fechaInicio').value = '';
    document.getElementById('fechaFin').value = '';

    // Muestra todas las filas nuevamente
    const filas = document.querySelectorAll('.listaUsuarios tbody tr');
    filas.forEach(fila => {
        fila.style.display = ''; // Muestra todas las filas
    });
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

    setTimeout(() => alerta.remove(), 5000); // Eliminar después de 5s
}


function crearContenedorAlertas() {
    const contenedor = document.createElement('div');
    contenedor.className = 'contenedorAlertas';
    document.body.appendChild(contenedor);
    return contenedor;
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


// Función para guardar usuario
function guardarUsuario() {
    // Obtener datos del formulario
    const id = document.getElementById('idUsuario').value;
    const nombre = document.getElementById('nombreUsuario').value;
    const contrasena = document.getElementById('contrasenaUsuario').value;
    const correo = document.getElementById('correoUsuario').value;
    const tipoPrivilegio = document.getElementById('tipoPrivilegio').value;
    
    // Validar campos obligatorios
    if (!nombre || !correo || !tipoPrivilegio) {
        mostrarAlerta('Por favor, complete todos los campos obligatorios', 'danger');
        return;
    }
    
    // Si es un nuevo usuario, la contraseña es obligatoria
    if (!id && !contrasena) {
        mostrarAlerta('La contraseña es obligatoria para nuevos usuarios', 'danger');
        return;
    }
    
    // Enviar datos al servidor
    fetch('/api/usuarios/guardar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            nombre: nombre,
            contrasena: contrasena,
            correo: correo,
            tipoPrivilegio: tipoPrivilegio
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.require_validation) {
                // Si requiere validación, mostrar mensaje y redirigir
                mostrarAlerta(data.message, 'success');
                setTimeout(() => {
                    window.location.href = `/validar-usuario?email=${encodeURIComponent(data.email)}`;
                }, 1500);
            } else {
                // Si no requiere validación, mostrar mensaje y recargar
                mostrarAlerta(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            }
        } else {
            mostrarAlerta(data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar usuario', 'danger');
    });
}


