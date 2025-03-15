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
                    alert('Error al obtener los datos del usuario');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al obtener los datos del usuario');
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
            
            console.log('Enviando datos:', userData);
            
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
                    alert(data.message);
                    window.location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al guardar el usuario');
            });
            
            // No cerramos el modal inmediatamente para permitir ver los errores
            // Solo cerramos si la operación fue exitosa
        });
    }
});

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
                
                // Mostrar el modal de ver usuario
                document.getElementById('verModalUsuario').style.display = 'flex';
            } else {
                alert('Error al obtener los datos del usuario');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al obtener los datos del usuario');
        });
}

// Cerrar el modal de ver usuario
function cerrarVerUsuario() {
    document.getElementById('verModalUsuario').style.display = 'none';
}

function toggleContrasena() {
    const contrasenaInput = document.getElementById('contrasenaUsuario');
    const toggleIcon = document.querySelector('.toggleContrasena');

    if (contrasenaInput.type === 'password') {
        contrasenaInput.type = 'text';
        toggleIcon.textContent = '🔒'; // Cambia el ícono a un "ojo cerrado"
    } else {
        contrasenaInput.type = 'password';
        toggleIcon.textContent = '👁️'; // Cambia el ícono a un "ojo abierto"
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
