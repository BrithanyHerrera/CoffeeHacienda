const contenedor = document.querySelector('.container');
const loginBtn = document.querySelector('.login-btn');

// Agregar un evento al botón de inicio de sesión
loginBtn.addEventListener('click', (event) => {
    event.preventDefault(); // Evita el envío del formulario
    contenedor.classList.add('active'); // Agrega la clase para el efecto

    // Espera 600 ms (el tiempo de la animación) antes de redirigir
    setTimeout(() => {
        window.location.href = '/menu'; // Redirige a menu.html
    }, 600); // Este valor debe coincidir con la duración de la animación
});
