document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('diagnosis-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.querySelector('.loader');
    const btnText = submitBtn.querySelector('span');
    const successMessage = document.getElementById('success-message');
    const resetBtn = document.getElementById('reset-btn');
    const deviceIdInput = document.getElementById('device_id');

    // Función para auto-detectar Device ID desde URL o caché local
    function fetchDeviceId() {
        const urlParams = new URLSearchParams(window.location.search);
        const urlId = urlParams.get('device_id');
        const cachedId = localStorage.getItem('ramedio_device_id');

        if (urlId) {
            deviceIdInput.value = urlId;
            deviceIdInput.setAttribute('readonly', 'true');
        } else if (cachedId) {
            deviceIdInput.value = cachedId;
            // No readonly so they can clear it if they want
        } else {
            deviceIdInput.value = "";
            deviceIdInput.placeholder = "Escribe el nombre de tu equipo (Ej. LAPTOP-BRYAN)";
            deviceIdInput.removeAttribute('readonly');
        }
    }

    // Llamar a la función al cargar la página
    fetchDeviceId();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Feedback: Loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Procesando...';
        loader.classList.remove('hidden');

        // Recopilar datos del formulario
        const formData = new FormData(form);
        const deviceId = formData.get('device_id');

        // Guardar el ID en caché para el futuro (así no tienen que volver a teclearlo)
        if (deviceId) {
            localStorage.setItem('ramedio_device_id', deviceId);
        }

        // Estructurar el payload final para ML / Backend
        const payload = {
            device_id: deviceId,
            timestamp: new Date().toISOString(),
            symptoms: {
                is_slow: formData.get('is_slow') === 'true',
                random_restarts: formData.get('random_restarts') === 'true',
                weird_noises: formData.get('weird_noises') === 'true',
                overheating: formData.get('overheating') === 'true',
                bsod_errors: formData.get('bsod_errors') === 'true',
                screen_flicker: formData.get('screen_flicker') === 'true',
                apps_crashing: formData.get('apps_crashing') === 'true',
                battery_issue: formData.get('battery_issue') === 'true',
                burnt_smell: formData.get('burnt_smell') === 'true',
                visual_artifacts: formData.get('visual_artifacts') === 'true',
                system_freezes: formData.get('system_freezes') === 'true',
                usb_disconnects: formData.get('usb_disconnects') === 'true',
                network_drops: formData.get('network_drops') === 'true',
                slow_boot: formData.get('slow_boot') === 'true',
                file_corruption: formData.get('file_corruption') === 'true'
            }
        };

        try {
            console.log("Enviando datos al servidor...");
            console.log(JSON.stringify(payload, null, 2));

            const response = await fetch('https://ramedio-diagnostico-de-pcs.onrender.com/api/symptoms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                // Ocultar formulario de inmediato y mostrar mensaje base
                form.classList.add('hidden');
                successMessage.classList.remove('hidden');

                // Mostrar "Analizando..."
                const diagnosisBox = document.getElementById('diagnosis-box');
                const diagnosisText = document.getElementById('diagnosis-text');
                diagnosisBox.classList.remove('hidden');
                diagnosisText.textContent = "Analizando con Inteligencia Artificial...";

                try {
                    // Segundo Fetch: Pedir el Diagnóstico al modelo predictivo
                    const mlResponse = await fetch(`https://ramedio-diagnostico-de-pcs.onrender.com/api/diagnostico/${payload.device_id}`);
                    if (mlResponse.ok) {
                        const mlData = await mlResponse.json();

                        if (mlData.error) {
                            diagnosisText.textContent = mlData.error;
                            diagnosisText.style.color = "var(--danger)";
                        } else {
                            // ¡Éxito! Mostrar el resultado
                            diagnosisText.textContent = mlData.diagnostico_ml;

                            // Cambiar color dependiendo de la gravedad (opcional pero bonito)
                            if (mlData.diagnostico_ml === "Sistema Saludable") {
                                diagnosisText.style.color = "var(--success)";
                            } else {
                                diagnosisText.style.color = "#fbbf24"; // Amarillo advertencia
                            }

                            // Redirigir al dashboard para ver los análisis visuales de ML y de Hardware reales
                            setTimeout(() => {
                                window.location.href = `dashboard.html?device_id=${encodeURIComponent(payload.device_id)}`;
                            }, 1500);
                        }
                    } else {
                        diagnosisText.textContent = "Error al calcular diagnóstico.";
                    }
                } catch (mlErr) {
                    console.error("Error obteniendo el diagnóstico ML:", mlErr);
                    diagnosisText.textContent = "No se pudo conectar con el motor de IA.";
                }

            } else {
                alert("Hubo un error al guardar los datos en el servidor.");
            }
        } catch (error) {
            console.error("Error contactando al servidor:", error);
            alert("No se pudo conectar con el servidor FastAPI.");
        } finally {
            // Restaurar botón (por si acaso vuelve atrás)
            submitBtn.disabled = false;
            btnText.textContent = 'Enviar Datos de Diagnóstico';
            loader.classList.add('hidden');
        }
    });

    // Botón para resetear y enviar otro reporte
    resetBtn.addEventListener('click', () => {
        form.reset();
        successMessage.classList.add('hidden');
        form.classList.remove('hidden');

        // Volver a autocompletar el Device ID después del reset
        fetchDeviceId();
    });
});
