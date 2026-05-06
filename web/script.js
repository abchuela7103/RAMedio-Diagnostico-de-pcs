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
    fetch('/api/ml/tree')
        .then(res => res.json())
        .then(data => { globalTreeDataIndex = data.tree; })
        .catch(err => console.log("Tree no precargado", err));

    // Función para auto-detectar Device ID desde URL o caché local
    function fetchDeviceId() {
        const urlParams = new URLSearchParams(window.location.search);

        // --- AUTH LOGIC ---
        const urlToken = urlParams.get('token');
        if (urlToken) {
            localStorage.setItem('token', urlToken);
            urlParams.delete('token');
            const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
            window.history.replaceState({}, '', newUrl);
        }

        if (!localStorage.getItem('token')) {
            window.location.href = 'login.html' + window.location.search;
            return;
        }
        // ------------------

        const urlId = urlParams.get('device_id');
        let realId = localStorage.getItem('ramedio_real_device_id');

        // Si la URL provee el equipo actual, guardarlo firmemente en caché
        if (urlId) {
            localStorage.setItem('ramedio_real_device_id', urlId);
            realId = urlId;
        }

        // Siempre cargar el ID real detectado al recargar index.html
        if (realId) {
            deviceIdInput.value = realId;
        } else {
            deviceIdInput.value = "";
        }

        // Bloquear permanentemente su edición para respetar la auto-detección
        deviceIdInput.placeholder = "Detectando ID del equipo...";
        deviceIdInput.setAttribute('readonly', 'true');
        deviceIdInput.style.pointerEvents = 'none';
        deviceIdInput.style.opacity = '0.7';
    }

    // Llamar a la función al cargar la página
    fetchDeviceId();

    // --- Lógica de Paginación ---
    let currentStep = 1;
    const totalSteps = 3;
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtnWrapper = document.getElementById('submit-btn');
    const progressBar = document.getElementById('form-progress-bar');
    const stepIndicator = document.getElementById('step-indicator');
    const stepDesc = document.getElementById('step-desc');

    const stepDescriptions = [
        "Rendimiento y Energía",
        "Pantalla y Sistema",
        "Hardware y Red"
    ];

    function updateStep() {
        // Update Progress Bar
        const progress = (currentStep / totalSteps) * 100;
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }

        // Update Text
        if (stepIndicator) stepIndicator.textContent = `Paso ${currentStep} de ${totalSteps}`;
        if (stepDesc) stepDesc.textContent = stepDescriptions[currentStep - 1];

        // Toggle Steps visibility
        for (let i = 1; i <= totalSteps; i++) {
            const stepEl = document.getElementById(`step-${i}`);
            if (!stepEl) continue;
            if (i === currentStep) {
                stepEl.classList.remove('hidden', 'hidden-left');
                stepEl.classList.add('active');
            } else if (i < currentStep) {
                stepEl.classList.remove('active', 'hidden');
                stepEl.classList.add('hidden-left');
            } else {
                stepEl.classList.remove('active', 'hidden-left');
                stepEl.classList.add('hidden');
            }
        }

        // Toggle Buttons
        if (prevBtn && nextBtn && submitBtnWrapper) {
            if (currentStep === 1) {
                prevBtn.classList.add('hidden');
            } else {
                prevBtn.classList.remove('hidden');
            }

            if (currentStep === totalSteps) {
                nextBtn.classList.add('hidden');
                submitBtnWrapper.classList.remove('hidden');
            } else {
                nextBtn.classList.remove('hidden');
                submitBtnWrapper.classList.add('hidden');
            }
        }
    }

    // Validate current step before proceeding
    function validateStep(stepIndex) {
        const stepEl = document.getElementById(`step-${stepIndex}`);
        if (!stepEl) return true;
        const requiredInputs = stepEl.querySelectorAll('input[required]');

        const groups = new Set();
        requiredInputs.forEach(input => groups.add(input.name));

        let allValid = true;
        groups.forEach(groupName => {
            const checked = stepEl.querySelector(`input[name="${groupName}"]:checked`);
            if (!checked) {
                allValid = false;
                const cards = stepEl.querySelectorAll('.question-card');
                cards.forEach(card => {
                    if (card.querySelector(`input[name="${groupName}"]`)) {
                        card.style.borderColor = '#ef4444';
                        card.style.transform = 'scale(1.02)';
                        setTimeout(() => {
                            card.style.borderColor = '';
                            card.style.transform = '';
                        }, 500);
                    }
                });
            }
        });

        return allValid;
    }

    if (nextBtn && prevBtn) {
        nextBtn.addEventListener('click', () => {
            if (!validateStep(currentStep)) return;
            if (currentStep < totalSteps) {
                currentStep++;
                updateStep();
            }
        });

        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateStep();
            }
        });

        updateStep();
    }

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

            const response = await fetch('/api/symptoms', {
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
                    const mlResponse = await fetch(`/api/diagnostico/${payload.device_id}`);
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

                            if (globalTreeDataIndex && mlData.decision_path) {
                                idxChart.setOption({
                                    backgroundColor: 'transparent',
                                    series: [{
                                        type: 'tree',
                                        data: [globalTreeDataIndex],
                                        top: '2%', left: '8%', bottom: '2%', right: '20%',
                                        symbolSize: 8, roam: true, initialTreeDepth: 3,
                                        label: { color: '#fff', fontSize: 13, backgroundColor: 'rgba(0,0,0,0.6)', padding: [3, 6], borderRadius: 4 },
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
                                    if (step >= pathArray.length) {
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

        // Reset Pagination
        if (typeof currentStep !== "undefined") {
            currentStep = 1;
            updateStep();
        }
    });
});
