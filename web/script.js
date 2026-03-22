document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('diagnosis-form');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.querySelector('.loader');
    const btnText = submitBtn.querySelector('span');
    const successMessage = document.getElementById('success-message');
    const resetBtn = document.getElementById('reset-btn');
    const goDashboardBtn = document.getElementById('go-dashboard-btn');
    const deviceIdInput = document.getElementById('device_id');

    // Novedad: Pre-cargar el árbol para que la animación sea instantánea tras enviar el form
    let globalTreeDataIndex = null;
    fetch('https://ramedio-diagnostico-de-pcs.onrender.com/api/ml/tree')
        .then(res => res.json())
        .then(data => { globalTreeDataIndex = data.tree; })
        .catch(err => console.log("Tree no precargado", err));

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

        // Recopilar datos del formulario para obtener deviceId temprano
        const formData = new FormData(form);
        const deviceId = formData.get('device_id');

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
                            // Mostrar la animación del árbol en la página principal
                            diagnosisText.textContent = "Trazando lógica de Inteligencia Artificial...";
                            diagnosisText.style.color = "var(--text-primary)";
                            const treeContainer = document.getElementById('index-tree-chart');
                            treeContainer.style.display = 'block';
                            
                            const idxChart = echarts.init(treeContainer, 'dark');
                            
                            if(globalTreeDataIndex && mlData.decision_path) {
                                idxChart.setOption({
                                    backgroundColor: 'transparent',
                                    series: [{
                                        type: 'tree',
                                        data: [globalTreeDataIndex],
                                        top: '2%', left: '8%', bottom: '2%', right: '20%',
                                        symbolSize: 8, roam: true, initialTreeDepth: 3,
                                        label: { color: '#fff', fontSize: 13, backgroundColor: 'rgba(0,0,0,0.6)', padding: [3,6], borderRadius: 4 },
                                        itemStyle: { color: '#1e90ff', borderColor: '#00f2fe' },
                                        lineStyle: { color: '#555', width: 2, curveness: 0.5 },
                                        animationDuration: 300,
                                        animationDurationUpdate: 500
                                    }]
                                });

                                const pathArray = mlData.decision_path;
                                let step = 0;
                                let clonedTree = JSON.parse(JSON.stringify(globalTreeDataIndex));
                                
                                const animationInterval = setInterval(() => {
                                    if(step >= pathArray.length) {
                                        clearInterval(animationInterval);
                                        // Finalizar la animación: presentar veredicto de forma prominente
                                        diagnosisText.innerHTML = `<strong>Veredicto:</strong> ${mlData.diagnostico_ml}<br><span style="font-size: 0.95em; color: #acc; font-weight: normal; margin-top: 5px; display: inline-block;">💡 ${mlData.solucion}</span>`;
                                        if (mlData.diagnostico_ml === "Sistema Saludable") {
                                            diagnosisText.style.color = "var(--success)";
                                        } else {
                                            diagnosisText.style.color = "#fbbf24";
                                        }
                                        
                                        goDashboardBtn.onclick = () => { window.location.href = `dashboard.html?device_id=${encodeURIComponent(payload.device_id)}`; };
                                        goDashboardBtn.classList.remove('hidden');
                                        return;
                                    }
                                    
                                    const activeNodes = pathArray.slice(0, step + 1);
                                    const currentNodeId = pathArray[step];
                                    
                                    function styleNode(node) {
                                        if (activeNodes.includes(node.node_id)) {
                                            node.itemStyle = Object.assign({}, node.itemStyle || {}, { color: '#ff4757', borderColor: '#ff4757', shadowBlur: 20, shadowColor: '#ff4757' });
                                            node.collapsed = false; 
                                        }
                                        if (node.node_id === currentNodeId) {
                                            node.symbolSize = 20;
                                            node.label = Object.assign({}, node.label || {}, { color: '#ff4757', fontWeight: 'bold', fontSize: 15 });
                                            if (step === pathArray.length - 1) { 
                                                node.label = Object.assign(node.label, { fontSize: 18, backgroundColor: '#ff4757', color: '#fff' });
                                                node.symbolSize = 30;
                                            }
                                        }
                                        if (node.children) {
                                            node.children.forEach(child => {
                                                if (activeNodes.includes(child.node_id)) {
                                                    child.lineStyle = { color: '#ff4757', width: 4, type: 'solid', shadowBlur: 10, shadowColor: '#ff4757' };
                                                }
                                                styleNode(child);
                                            });
                                        }
                                    }
                                    
                                    const frameTree = JSON.parse(JSON.stringify(clonedTree));
                                    styleNode(frameTree);
                                    idxChart.setOption({ series: [{ type: 'tree', data: [frameTree] }] });
                                    step++;
                                }, 800); // velocidad del tracker
                            } else {
                                // Fallback sin animación (por ej. si no cargó el árbol o no llegó el decision_path)
                                diagnosisText.innerHTML = `<strong>Veredicto:</strong> ${mlData.diagnostico_ml}<br><span style="font-size: 0.95em; color: #acc; font-weight: normal; margin-top: 5px; display: inline-block;">💡 ${mlData.solucion}</span>`;
                                if (mlData.diagnostico_ml === "Sistema Saludable") {
                                    diagnosisText.style.color = "var(--success)";
                                } else {
                                    diagnosisText.style.color = "#fbbf24";
                                }
                                goDashboardBtn.onclick = () => { window.location.href = `dashboard.html?device_id=${encodeURIComponent(payload.device_id)}`; };
                                goDashboardBtn.classList.remove('hidden');
                            }
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
        goDashboardBtn.classList.add('hidden');
        form.classList.remove('hidden');

        // Volver a autocompletar el Device ID después del reset
        fetchDeviceId();
    });
});
