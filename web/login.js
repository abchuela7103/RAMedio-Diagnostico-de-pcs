document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const toggleModeBtn = document.getElementById('toggle-mode-btn');
    const formSubtitle = document.getElementById('form-subtitle');
    const btnText = document.getElementById('btn-text');
    const loader = document.getElementById('loader');
    
    let isLogin = true;

    // Obtener parámetros de la URL actual por si llegamos desde el agente u otro lado
    const urlParams = new URLSearchParams(window.location.search);
    
    toggleModeBtn.addEventListener('click', () => {
        isLogin = !isLogin;
        if (isLogin) {
            formSubtitle.textContent = 'Inicia sesión en tu cuenta';
            btnText.textContent = 'Iniciar Sesión';
            toggleModeBtn.textContent = '¿No tienes cuenta? Regístrate aquí';
        } else {
            formSubtitle.textContent = 'Crea una nueva cuenta';
            btnText.textContent = 'Registrarse';
            toggleModeBtn.textContent = '¿Ya tienes cuenta? Inicia Sesión';
        }
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if(!username || !password) return;

        btnText.style.display = 'none';
        loader.classList.remove('hidden');
        
        const endpoint = isLogin ? '/api/login' : '/api/register';
        
        try {
            // El host es el mismo si se sirve estáticamente, pero en dev puede diferir
            const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                            ? 'http://127.0.0.1:8000' : '';
            
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (isLogin) {
                    localStorage.setItem('token', data.token);
                    alert('Inicio de sesión exitoso');
                    
                    // Al login, redirigir al index.html conservando parámetros (como device_id)
                    let redirUrl = "index.html";
                    if(window.location.search) {
                         redirUrl += window.location.search;
                    }
                    window.location.href = redirUrl;
                } else {
                    alert('Registro exitoso, ahora puedes iniciar sesión.');
                    toggleModeBtn.click(); // Cambiar a modo login
                }
            } else {
                alert(data.detail || 'Ocurrió un error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('No se pudo conectar con el servidor.');
        } finally {
            btnText.style.display = 'inline';
            loader.classList.add('hidden');
        }
    });
});
