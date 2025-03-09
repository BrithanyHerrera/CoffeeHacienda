// Función para abrir el modal de Edición y Agregar usuario.
function abrirEAModal(id = null, nombre = '', correo = '', tipoPrivilegio = '', fechaRegistro = '', contrasena = '') {
    // Verifica que los valores sean correctos
    console.log('Abrir modal con los siguientes datos:', id, nombre, correo, tipoPrivilegio, fechaRegistro, contrasena);

    // Rellenar los campos del modal con los valores recibidos
    document.getElementById('idUsuario').value = id || '';
    document.getElementById('nombreUsuario').value = nombre;
    document.getElementById('correoUsuario').value = correo;
    document.getElementById('tipoPrivilegio').value = tipoPrivilegio;
    document.getElementById('contrasenaUsuario').value = contrasena;

    // Establecer el título del modal dependiendo si es agregar o editar
    document.getElementById('tituloModal').innerText = id ? 'Editar Usuario' : 'Agregar Usuario';
    
    // Mostrar el modal de agregar/editar usuario
    document.getElementById('usuarioModal').style.display = 'flex';
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
            
            cerrarEAModal();
        });
    }
});

// Función para abrir el modal de ver usuario.
function abrirVerUsuario(id, nombre, correo, tipoPrivilegio, fechaRegistro, contrasena) {
    // Establecer el contenido en el modal de ver usuario
    document.getElementById('verIDUsuario').textContent = id;
    document.getElementById('verNombreUsuario').textContent = nombre;
    document.getElementById('verCorreoUsuario').textContent = correo;
    document.getElementById('verTipoPrivilegio').textContent = tipoPrivilegio;
    document.getElementById('verFechaRegistro').textContent = fechaRegistro;
    document.getElementById('verContrasenaUsuario').textContent = contrasena;
    
    // Mostrar el modal de ver usuario
    document.getElementById('verModalUsuario').style.display = 'flex';
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