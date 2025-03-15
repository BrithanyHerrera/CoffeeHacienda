// Abrir y cerrar el modal del corte de caja
var modal = document.getElementById("miModal");
var btn = document.getElementById("btnAgregarCorte");
var span = document.getElementById("cerrarModal");

btn.onclick = function() {
    modal.style.display = "block";
}

span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Abrir y cerrar el modal para realizar retiro
var modalRetiro = document.getElementById("miModalRetiro");
var btnRetiro = document.getElementById("btnRealizarRetiro");
var spanRetiro = document.getElementById("cerrarModalRetiro");

btnRetiro.onclick = function() {
    modalRetiro.style.display = "block";
}

spanRetiro.onclick = function() {
    modalRetiro.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modalRetiro) {
        modalRetiro.style.display = "none";
    }
}

function buscarUsuario() {
    const nombreUsuario = document.getElementById('buscarUsuario').value.toLowerCase();
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    console.log("Nombre buscado:", nombreUsuario);
    console.log("Fecha inicio:", fechaInicio, "Fecha fin:", fechaFin);

    // Selecciona las filas de la tabla principal
    const filas = document.querySelectorAll('.table tbody tr');
    filas.forEach(fila => {
        const usuarioNombre = fila.querySelector('td:nth-child(7)').textContent.toLowerCase();
        const fechaRegistro = fila.querySelector('td:nth-child(1)').textContent;

        console.log("Usuario actual:", usuarioNombre, "Fecha registro:", fechaRegistro);

        const coincideNombre = !nombreUsuario || usuarioNombre.includes(nombreUsuario);
        const coincideFechaInicio = !fechaInicio || new Date(fechaRegistro) >= new Date(fechaInicio);
        const coincideFechaFin = !fechaFin || new Date(fechaRegistro) <= new Date(fechaFin);

        if (coincideNombre && coincideFechaInicio && coincideFechaFin) {
            fila.style.display = ''; // Muestra la fila
        } else {
            fila.style.display = 'none'; // Oculta la fila
        }
    });
}

function reestablecerFiltros() {
    document.getElementById('buscarUsuario').value = '';
    document.getElementById('fechaInicio').value = '';
    document.getElementById('fechaFin').value = '';

    // Muestra todas las filas nuevamente
    const filas = document.querySelectorAll('.table tbody tr');
    filas.forEach(fila => {
        fila.style.display = ''; // Muestra todas las filas
    });
}
