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
    const nombreUsuario = document.getElementById('buscarUsuario').value.trim().toLowerCase();
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    console.log("🔍 BUSCANDO...");
    console.log("Nombre ingresado:", nombreUsuario);
    console.log("Fecha inicio:", fechaInicio);
    console.log("Fecha fin:", fechaFin);

    // Obtiene todas las filas de la tabla
    const filas = document.querySelectorAll('.table tbody tr');
    console.log(`Total de filas encontradas: ${filas.length}`);

    filas.forEach(fila => {
        const usuarioNombreCell = fila.querySelector('td:nth-child(1)'); // Usuario está en la primera columna
        const fechaRegistroCell = fila.querySelector('td:nth-child(2)'); // Fecha está en la segunda columna

        if (!usuarioNombreCell || !fechaRegistroCell) {
            console.warn("⚠️ Fila sin datos de usuario o fecha, saltando...");
            return;
        }

        const usuarioNombre = usuarioNombreCell.textContent.trim().toLowerCase();
        const fechaRegistro = fechaRegistroCell.textContent.trim();

        console.log(`Fila actual -> Usuario: ${usuarioNombre}, Fecha: ${fechaRegistro}`);

        // Verifica si el usuario coincide con la búsqueda
        const coincideNombre = nombreUsuario === "" || usuarioNombre.includes(nombreUsuario);
        const coincideFechaInicio = !fechaInicio || new Date(fechaRegistro) >= new Date(fechaInicio);
        const coincideFechaFin = !fechaFin || new Date(fechaRegistro) <= new Date(fechaFin);

        if (coincideNombre && coincideFechaInicio && coincideFechaFin) {
            console.log("✅ Coincidencia encontrada, mostrando fila.");
            fila.style.display = ''; // Muestra la fila
        } else {
            console.log("❌ No coincide, ocultando fila.");
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

    console.log("🔄 Filtros restablecidos. Se muestran todas las filas.");
}


