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
        const response = await fetch('/api/user/scans', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const scans = data.scans || [];

            grid.innerHTML = ''; // Limpiar loader

            if (scans.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center py-5"><h4 class="text-white">Aún no hay escaneos guardados.</h4><p style="color: #acc;">Lleva a cabo un nuevo diagnóstico para visualizarlo aquí.</p></div>';
                return;
            }

            scans.forEach(scan => {
                const col = document.createElement('div');
                col.className = 'col-md-6 col-lg-4';
                
                const d = new Date(scan.timestamp);
                const dateStr = d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                col.innerHTML = `
                    <div class="card rounded-0 border-secondary p-4 text-center cursor-pointer history-card h-100" style="background-color: #2a2a2a; cursor: pointer; transition: all 0.3s ease;" onclick="window.location.href='dashboard.html?device_id=${encodeURIComponent(scan.device_id)}&symptom_id=${scan.id}'">
                        <div style="font-size: 2.8rem; margin-bottom: 15px;"><i class="fa-solid fa-file-waveform" style="color: var(--primary);"></i></div>
                        <h6 class="text-white mb-2" style="word-break: break-all; font-weight: 600;"><i class="fa-solid fa-desktop"></i> ${scan.device_id}</h6>
                        <p style="color: var(--txt-soft); font-size: 0.9rem; margin-bottom: 10px;"><i class="fa-solid fa-calendar-day"></i> ${dateStr}</p>
                        <div class="mt-3">
                            <span class="badge bg-primary" style="font-size: 0.8rem; padding: 6px 12px;">Ver Resultado &rsaquo;</span>
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
