/**
 * utilidades comunes de interfaz de usuario
 */

// unificación de todas las variantes de escaparHtml (escaparHtmlMenu, escaparHtmlOrdenes, etc)
function escaparHtml(valor) {
    if (typeof valor !== 'string') return valor;
    return valor
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// crea el contenedor de alertas dinámico si no existe
function crearContenedorAlertas() {
    let contenedor = document.getElementById('alert-container');
    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.id = 'alert-container';
        contenedor.style.position = 'fixed';
        contenedor.style.top = '20px';
        contenedor.style.right = '20px';
        contenedor.style.zIndex = '9999';
        document.body.appendChild(contenedor);
    }
    return contenedor;
}

// mostrar alerta unificada (reemplaza a múltiples versiones en archivos individuales)
function mostrarAlerta(mensaje, tipo = 'ExitoG') {
    const contenedor = crearContenedorAlertas();

    const alerta = document.createElement('div');
    alerta.className = `alerta ${tipo === 'ExitoG' ? 'alerta-exito' : 'alerta-error'}`;
    alerta.style.display = 'flex';
    alerta.style.justifyContent = 'space-between';
    alerta.style.alignItems = 'center';
    alerta.style.marginBottom = '10px';
    alerta.style.padding = '15px';
    alerta.style.borderRadius = '5px';
    alerta.style.color = '#fff';
    alerta.style.backgroundColor = tipo === 'ExitoG' ? '#28a745' : '#dc3545';
    alerta.style.boxShadow = '0px 4px 6px rgba(0,0,0,0.1)';
    alerta.style.minWidth = '250px';

    const texto = document.createElement('span');
    texto.innerText = mensaje;
    alerta.appendChild(texto);

    const botonCerrar = document.createElement('button');
    botonCerrar.innerHTML = '&times;';
    botonCerrar.style.background = 'none';
    botonCerrar.style.border = 'none';
    botonCerrar.style.color = '#fff';
    botonCerrar.style.fontSize = '20px';
    botonCerrar.style.cursor = 'pointer';
    botonCerrar.style.marginLeft = '15px';
    botonCerrar.onclick = () => alerta.remove();
    
    alerta.appendChild(botonCerrar);
    contenedor.appendChild(alerta);

    setTimeout(() => {
        if (alerta.parentElement) alerta.remove();
    }, 5000);
}

// unificación de formato de fecha
function formatearFecha(fechaStr) {
    if (!fechaStr) return "N/A";
    const opciones = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    return new Date(fechaStr).toLocaleDateString('es-ES', opciones);
}
