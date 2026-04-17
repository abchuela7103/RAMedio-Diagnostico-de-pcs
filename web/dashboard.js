document.addEventListener('DOMContentLoaded', async () => {
    // --- AUTH LOGIC ---
    const urlParamsAuth = new URLSearchParams(window.location.search);
    const urlToken = urlParamsAuth.get('token');
    if (urlToken) {
        localStorage.setItem('token', urlToken);
        urlParamsAuth.delete('token');
        const newUrl = window.location.pathname + (urlParamsAuth.toString() ? '?' + urlParamsAuth.toString() : '');
        window.history.replaceState({}, '', newUrl);
    }

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html' + window.location.search;
        return;
    }

    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });
    // ------------------

    // Inicializar contenedores de Gráficos ECharts usando el tema 'dark' predeterminado de echarts
    const hardwareDom = document.getElementById('hardware-chart');
    const accuracyDom = document.getElementById('accuracy-gauge');
    const treeDom = document.getElementById('tree-chart');

    const hardwareChart = echarts.init(hardwareDom, 'dark');
    const accuracyChart = echarts.init(accuracyDom, 'dark');
    const treeChart = echarts.init(treeDom, 'dark');

    // Quitar fondos estáticos propios de ECharts 'dark' para que la transparencia glassmorfsism fluya
    const transparentBg = 'transparent';

    window.globalTreeData = null;
    window.treeChartRef = treeChart;

    window.highlightDecisionPath = function(pathArray) {
        if (!window.globalTreeData || !window.treeChartRef) {
            setTimeout(() => window.highlightDecisionPath(pathArray), 500);
            return;
        }
        const clonedTree = JSON.parse(JSON.stringify(window.globalTreeData));
        const activeNodes = pathArray;
        const currentNodeId = pathArray[pathArray.length - 1]; // El nodo final
        
        function styleNode(node) {
            if (activeNodes.includes(node.node_id)) {
                node.itemStyle = Object.assign({}, node.itemStyle || {}, { color: '#ff4757', borderColor: '#ff4757', shadowBlur: 20, shadowColor: '#ff4757' });
                node.collapsed = false; 
            }
            if (node.node_id === currentNodeId) {
                node.symbolSize = 35;
                node.itemStyle.color = '#fff';
                if (!node.label) node.label = {};
                node.label.color = '#fff';
                node.label.backgroundColor = '#ff4757';
                node.label.fontWeight = 'bold';
                node.label.fontSize = 18;
            } else if (activeNodes.includes(node.node_id)) {
                if (!node.label) node.label = {};
                node.label.color = '#ff4757';
                node.label.fontWeight = 'bold';
                node.label.fontSize = 16;
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
        
        styleNode(clonedTree);
        
        window.treeChartRef.setOption({
            series: [{ type: 'tree', data: [clonedTree] }]
        });
    };

    // 1. Fetch de los datos del ML (Arbol y Precisión) al cargar la página
    try {
        treeChart.showLoading({text: 'Cargando IA...', color: '#4facfe', maskColor: 'rgba(0,0,0,0.4)'});
        accuracyChart.showLoading({text: '', maskColor: 'rgba(0,0,0,0.4)'});
        
        const mlResponse = await fetch('http://40.233.30.180/api/ml/tree');
        if (mlResponse.ok) {
            const mlData = await mlResponse.json();
            
            // Renderizar el Gauge (Medidor de Precisión)
            const gaugeOption = {
                backgroundColor: transparentBg,
                series: [
                    {
                        type: 'gauge',
                        startAngle: 180,
                        endAngle: 0,
                        center: ['50%', '75%'],
                        radius: '100%',
                        min: 0,
                        max: 100,
                        splitNumber: 10,
                        axisLine: {
                            lineStyle: {
                                width: 20,
                                color: [
                                    [0.5, '#ff4757'],  // Rojo (Pobre) >50%
                                    [0.85, '#ffa502'], // Naranja (Aceptable) >85%
                                    [1, '#2ed573']     // Verde (Excelente) >100%
                                ]
                            }
                        },
                        pointer: {
                            icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
                            length: '15%',
                            width: 20,
                            offsetCenter: [0, '-60%'],
                            itemStyle: { color: 'auto' }
                        },
                        axisTick: { length: 15, lineStyle: { color: 'auto', width: 2 } },
                        splitLine: { length: 25, lineStyle: { color: 'auto', width: 5 } },
                        axisLabel: { color: '#ccc', distance: 20, fontSize: 12 },
                        detail: {
                            fontSize: 50,
                            offsetCenter: [0, '0%'],
                            valueAnimation: true,
                            formatter: '{value}%',
                            color: 'inherit',
                            fontWeight: 'bold'
                        },
                        data: [{ value: mlData.accuracy, name: 'Score' }]
                    }
                ]
            };
            accuracyChart.hideLoading();
            accuracyChart.setOption(gaugeOption);

            // Renderizar el Tree Chart (Árbol de Decisión)
            const treeOption = {
                backgroundColor: transparentBg,
                tooltip: {
                    trigger: 'item',
                    triggerOn: 'mousemove'
                },
                series: [
                    {
                        type: 'tree',
                        data: [mlData.tree],
                        top: '5%',
                        left: '10%',
                        bottom: '5%',
                        right: '25%',
                        symbolSize: 12,
                        roam: true, // Habilita Zoom y Paneo con el ratón! IMPORTANTISIMO PARA ARBOLES GRANDES
                        initialTreeDepth: 3, // Nivel por defecto de nodos abiertos (no sobrecargar la vista)
                        label: {
                            position: 'left',
                            verticalAlign: 'middle',
                            align: 'right',
                            fontSize: 14,
                            color: '#fff',
                            backgroundColor: 'rgba(0,0,0,0.6)',
                            padding: [4, 8],
                            borderRadius: 4
                        },
                        leaves: {
                            label: {
                                position: 'right',
                                verticalAlign: 'middle',
                                align: 'left',
                                color: '#00f2fe',
                                fontWeight: 'bold',
                                fontSize: 13,
                                backgroundColor: 'rgba(0,0,0,0.8)',
                            }
                        },
                        expandAndCollapse: true,
                        animationDuration: 550,
                        animationDurationUpdate: 750,
                        itemStyle: {
                            color: '#1e90ff',
                            borderColor: '#00f2fe'
                        },
                        lineStyle: {
                            color: '#555',
                            width: 2,
                            curveness: 0.5
                        }
                    }
                ]
            };
            treeChart.hideLoading();
            treeChart.setOption(treeOption);
            window.globalTreeData = mlData.tree;
        }
    } catch(err) {
        console.error("Error al cargar ML Data:", err);
        treeChart.hideLoading();
        accuracyChart.hideLoading();
    }

    // 2. Fetch y Renderización de la gráfica de Hardware a petición
    const loadHardware = async (deviceId) => {
        hardwareChart.showLoading({text: 'Consultando Dispositivo...', color: '#4facfe', textColor: '#fff', maskColor: 'rgba(0,0,0,0.4)'});
        
        try {
            const res = await fetch(`http://40.233.30.180/api/dashboard/history/${encodeURIComponent(deviceId)}`);
            const data = await res.json();
            
            if(data.timestamps && data.timestamps.length > 0) {
                const hardwareOption = {
                    backgroundColor: transparentBg,
                    tooltip: { 
                        trigger: 'axis',
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        textStyle: { color: '#fff' }
                    },
                    legend: { data: ['CPU %', 'RAM %', 'Disco %', 'Disco Act. %', 'GPU %'], textStyle: { color: '#ddd' } },
                    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: data.timestamps,
                        axisLabel: { color: '#aaa' }
                    },
                    yAxis: {
                        type: 'value',
                        max: 100,
                        axisLabel: { formatter: '{value} %', color: '#aaa' },
                        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
                    },
                    series: [
                        {
                            name: 'CPU %',
                            type: 'line',
                            smooth: true,
                            data: data.cpu,
                            symbol: 'none',
                            lineStyle: { width: 3, color: '#ff4757' }
                        },
                        {
                            name: 'RAM %',
                            type: 'line',
                            smooth: true,
                            data: data.ram,
                            symbol: 'none',
                            lineStyle: { width: 3, color: '#1e90ff' },
                            areaStyle: {
                                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                    { offset: 0, color: 'rgba(30, 144, 255, 0.6)' },
                                    { offset: 1, color: 'rgba(30, 144, 255, 0.0)' }
                                ])
                            }
                        },
                        {
                            name: 'Disco %',
                            type: 'line',
                            smooth: true,
                            data: data.disk,
                            symbol: 'none',
                            lineStyle: { width: 2, color: '#ffa502' }
                        },
                        {
                            name: 'Disco Act. %',
                            type: 'line',
                            smooth: true,
                            data: data.disk_active,
                            symbol: 'none',
                            lineStyle: { width: 2, type: 'dashed', color: '#eccc68' }
                        },
                        {
                            name: 'GPU %',
                            type: 'line',
                            smooth: true,
                            data: data.gpu,
                            symbol: 'none',
                            lineStyle: { width: 3, color: '#2ed573' }
                        }
                    ]
                };
                hardwareChart.setOption(hardwareOption, true);
            } else {
                alert("No se encontraron registros de hardware para este dispositivo. Asegúrate de ejecutar el agente (main.py).");
                hardwareChart.clear();
            }
        } catch(err) {
            console.error("Error cargando historial de hardware:", err);
            alert("No se pudo conectar con el servidor. ¿Está ejecutándose `python server/api.py`?");
        } finally {
            hardwareChart.hideLoading();
        }
    };

    // 3. Fetch y Renderización de Probabilidades ML a petición
    const loadProbas = async (deviceId) => {
        const probaDom = document.getElementById('proba-chart');
        const probaChart = echarts.init(probaDom, 'dark');
        probaChart.showLoading({text: 'Calculando probabilidades...', color: '#4facfe', maskColor: 'rgba(0,0,0,0.4)'});
        
        try {
            const res = await fetch(`http://40.233.30.180/api/diagnostico/${encodeURIComponent(deviceId)}`);
            const data = await res.json();
            
            // Modificar Título principal y Sugerencia
            document.getElementById('current-diagnosis-text').textContent = "Veredicto IA: " + data.diagnostico_ml;
            
            const solEl = document.getElementById('current-solution-text');
            if (data.solucion) {
                solEl.innerHTML = `<strong>💡 Sugerencia:</strong> ${data.solucion}`;
                solEl.style.display = 'block';
            } else {
                solEl.style.display = 'none'; // Hide if no solution
            }
            
            if(data.diagnostico_ml && data.probabilidades) {
                const classes = Object.keys(data.probabilidades);
                const values = Object.values(data.probabilidades);
                
                const probaOption = {
                    backgroundColor: transparentBg,
                    tooltip: { 
                        trigger: 'axis', 
                        axisPointer: { type: 'shadow' },
                        formatter: '{b}: {c}%' 
                    },
                    grid: { left: '3%', right: '10%', bottom: '3%', containLabel: true },
                    xAxis: { 
                        type: 'value', 
                        max: 100, 
                        axisLabel: { formatter: '{value}%', color: '#aaa' },
                        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
                    },
                    yAxis: { 
                        type: 'category', 
                        data: classes, 
                        axisLabel: { color: '#ddd', fontSize: 13, width: 200, overflow: 'break' } 
                    },
                    series: [
                        {
                            name: 'Probabilidad',
                            type: 'bar',
                            data: values,
                            barWidth: '50%',
                            itemStyle: {
                                color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                                    { offset: 0, color: '#00f2fe' },
                                    { offset: 1, color: '#4facfe' }
                                ]),
                                borderRadius: [0, 5, 5, 0]
                            },
                            label: { 
                                show: true, 
                                position: 'right', 
                                formatter: '{c}%', 
                                color: '#fff',
                                fontWeight: 'bold'
                            }
                        }
                    ]
                };
                probaChart.setOption(probaOption, true);
                window.addEventListener('resize', () => probaChart.resize());
                
                // Ejecutar Resaltado del path si el backend lo retornó!
                if(data.decision_path) {
                    window.highlightDecisionPath(data.decision_path);
                }
                
            } else {
                document.getElementById('current-diagnosis-text').textContent = "No hay diagnóstico disponible. Llena el formulario primero.";
            }
        } catch(err) {
            console.error("Error cargando probabilidades ML:", err);
            document.getElementById('current-diagnosis-text').textContent = "Error de conexión con el servidor ML.";
        } finally {
            probaChart.hideLoading();
        }
    };

    // Listeners del HTML
    document.getElementById('load_metrics_btn').addEventListener('click', () => {
        const devId = document.getElementById('dashboard_device_id').value.trim();
        if(devId) {
            loadHardware(devId);
            loadProbas(devId);
            localStorage.setItem('ramedio_real_device_id', devId);
            document.getElementById('return-link').href = `index.html?device_id=${encodeURIComponent(devId)}`;
        } else {
            alert('Por favor ingresa un ID de equipo.');
        }
    });

    // Petición inicial vacía u opcional de hardware.
    hardwareChart.setOption({
        backgroundColor: transparentBg,
        title: { text: "Esperando ID de Dispositivo...", textStyle: { color: "#555" }, left: 'center', top:'center' }
    });

    // Auto-Cargar si venimos redireccionados desde el formulario (index.html)
    const urlParams = new URLSearchParams(window.location.search);
    const originDeviceId = urlParams.get('device_id');
    if (originDeviceId) {
        document.getElementById('dashboard_device_id').value = originDeviceId;
        loadHardware(originDeviceId);
        loadProbas(originDeviceId);
        localStorage.setItem('ramedio_real_device_id', originDeviceId);
        const returnLink = document.getElementById('return-link');
        if (returnLink) {
            returnLink.href = `index.html?device_id=${encodeURIComponent(originDeviceId)}`;
        }
    }

    // --- CARGAR EQUIPOS DEL USUARIO ---
    async function cargarEquipos() {
         const listContainer = document.getElementById('device-list');
         try {
             const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://127.0.0.1:8000' : '';
             const res = await fetch(`${API_BASE}/api/user/devices`, {
                 headers: { 'Authorization': `Bearer ${token}` }
             });
             
             if (res.ok) {
                 const data = await res.json();
                 listContainer.innerHTML = '';
                 if (data.devices && data.devices.length > 0) {
                     data.devices.forEach(dev => {
                         const btn = document.createElement('button');
                         btn.textContent = dev;
                         btn.className = 'secondary-btn';
                         btn.style.width = '100%';
                         btn.style.margin = '0';
                         btn.style.padding = '10px';
                         if (originDeviceId === dev) {
                             btn.style.background = 'rgba(79, 172, 254, 0.3)';
                             btn.style.borderColor = '#00f2fe';
                         }
                         btn.onclick = () => {
                             window.location.href = `dashboard.html?device_id=${encodeURIComponent(dev)}`;
                         };
                         listContainer.appendChild(btn);
                     });
                 } else {
                     listContainer.innerHTML = '<p style="color: #acc; text-align: center; font-size: 0.9rem;">No tienes equipos vinculados.</p>';
                 }
             } else {
                 listContainer.innerHTML = '<p style="color: #ff4757; text-align: center; font-size: 0.8rem;">Sesión expirada o inválida</p>';
             }
         } catch(e) {
             console.error("Error obteniendo equipos", e);
             listContainer.innerHTML = '<p style="color: #ff4757; text-align: center; font-size: 0.9rem;">Error de red</p>';
         }
    }
    cargarEquipos();
    // ----------------------------------

    // Hacer todos los gráficos responsivos comunes
    window.addEventListener('resize', () => {
        hardwareChart.resize();
        accuracyChart.resize();
        treeChart.resize();
    });
});
