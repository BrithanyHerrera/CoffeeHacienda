(function configurarProteccionCsrf() {
    'use strict';

    const meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) {
        return;
    }

    const token = meta.getAttribute('content');
    const fetchOriginal = window.fetch.bind(window);
    const metodosSeguros = new Set(['GET', 'HEAD', 'OPTIONS', 'TRACE']);

    window.fetch = function fetchConCsrf(recurso, opciones = {}) {
        const url = recurso instanceof Request ? recurso.url : String(recurso);
        const destino = new URL(url, window.location.href);
        const metodo = String(
            opciones.method || (recurso instanceof Request ? recurso.method : 'GET')
        ).toUpperCase();

        if (destino.origin !== window.location.origin || metodosSeguros.has(metodo)) {
            return fetchOriginal(recurso, opciones);
        }

        const headers = new Headers(
            opciones.headers || (recurso instanceof Request ? recurso.headers : undefined)
        );
        headers.set('X-CSRFToken', token);

        return fetchOriginal(recurso, { ...opciones, headers });
    };
})();
