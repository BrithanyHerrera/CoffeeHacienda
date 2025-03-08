// Función para abrir el modal de Edición y Agregar usuario.
function abrirEAModal(id = null, nombre = '', correo = '', tipoPrivilegio = '', fechaRegistro = '', contrasena = '') {
    // Verifica que los valores sean correctos
    console.log('Abrir modal con los siguientes datos:', id, nombre, correo, tipoPrivilegio, fechaRegistro, contrasena);

    // Rellenar los campos del modal con los valores recibidos
    document.getElementById('idUsuario').value = id;
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

// Evitar el comportamiento por defecto del formulario y cerrar el modal.
document.getElementById('formUsuario').addEventListener('submit', function(event) {
    event.preventDefault();
    // Aquí puedes agregar la lógica para guardar el usuario (ya sea agregar o editar)
    // Por ejemplo, enviar los datos a tu servidor mediante AJAX o Fetch API.
    console.log('Usuario guardado:', {
        id: document.getElementById('idUsuario').value,
        nombre: document.getElementById('nombreUsuario').value,
        correo: document.getElementById('correoUsuario').value,
        contrasena: document.getElementById('contrasenaUsuario').value,
        tipoPrivilegio: document.getElementById('tipoPrivilegio').value
    });
    cerrarEAModal(); // Cerrar el modal después de guardar
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