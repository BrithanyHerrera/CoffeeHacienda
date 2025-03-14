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