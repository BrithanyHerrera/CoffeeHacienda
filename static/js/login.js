

// Selecciona los elementos necesarios
const togglePassword = document.querySelector('#togglePassword');
const passwordInput = document.querySelector('#passwordInput');

// Agrega el evento al icono
togglePassword.addEventListener('click', () => {
    // Cambia el tipo del input entre 'password' y 'text'
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';

    // Cambia el emoji según el estado
    togglePassword.textContent = isPassword ? '🔒' : '👁️';
});

