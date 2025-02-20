const container = document.querySelector('.container');
const loginBtn = document.querySelector('.login-btn');

loginBtn.addEventListener('click', (event) => {
    event.preventDefault(); // Evita el envío del formulario
    container.classList.add('active'); // Agrega la clase para el efecto
    window.location.href = '/menu'; // Redirige a menu.html
});