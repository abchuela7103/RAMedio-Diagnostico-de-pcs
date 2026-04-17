document.addEventListener('DOMContentLoaded', async () => {
    // Autenticación Base
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });

    const grid = document.getElementById('history-grid');

    try {
        const response = await fetch('/api/user/devices', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const devices = data.devices || [];

            grid.innerHTML = ''; // Limpiar loader

            if (devices.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center py-5"><h4 class="text-white">Aún no hay equipos diagnosticados.</h4><p style="color: #acc;">Descarga y ejecuta el agente de escritorio en tu PC para comenzar.</p></div>';
                return;
            }

            devices.forEach(device => {
                const col = document.createElement('div');
                col.className = 'col-md-6 col-lg-4';
                
                // Redirigir al dashboard con la MAC o UUID del equipo
                col.innerHTML = `
                    <div class="glass-panel p-4 text-center cursor-pointer history-card h-100" style="cursor: pointer; transition: all 0.3s ease; border: 1px solid rgba(255,255,255,0.05);" onclick="window.location.href='dashboard.html?device_id=${encodeURIComponent(device)}'">
                        <div style="font-size: 2.8rem; margin-bottom: 15px;">🖥️</div>
                        <h5 class="text-white mb-2" style="word-break: break-all; font-weight: 600;">${device}</h5>
                        <div class="mt-3">
                            <span class="badge bg-primary" style="font-size: 0.8rem; padding: 6px 12px;">Abrir Dashboard &rsaquo;</span>
                        </div>
                    </div>
                `;
                grid.appendChild(col);
            });
        } else {
            console.error("Error fetching devices");
            if(response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
            }
            grid.innerHTML = '<div class="col-12 text-center text-danger"><p>Error al cargar el historial. Código: HTTP ' + response.status + '</p></div>';
        }
    } catch (err) {
        console.error(err);
        grid.innerHTML = '<div class="col-12 text-center text-danger"><p>Problema de conexión con el servidor. Intenta actualizar.</p></div>';
    }
});
