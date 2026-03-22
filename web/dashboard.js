document.addEventListener('DOMContentLoaded', async () => {
    // Inicializar contenedores de Gráficos ECharts usando el tema 'dark' predeterminado de echarts
    const hardwareDom = document.getElementById('hardware-chart');
    const accuracyDom = document.getElementById('accuracy-gauge');
    const treeDom = document.getElementById('tree-chart');

    const hardwareChart = echarts.init(hardwareDom, 'dark');
    const accuracyChart = echarts.init(accuracyDom, 'dark');
    const treeChart = echarts.init(treeDom, 'dark');

    // Quitar fondos estáticos propios de ECharts 'dark' para que la transparencia glassmorfsism fluya
    const transparentBg = 'transparent';

    // 1. Fetch de los datos del ML (Arbol y Precisión) al cargar la página
    try {
        treeChart.showLoading({text: 'Cargando IA...', color: '#4facfe', maskColor: 'rgba(0,0,0,0.4)'});
        accuracyChart.showLoading({text: '', maskColor: 'rgba(0,0,0,0.4)'});
        
        const mlResponse = await fetch('http://localhost:8000/api/ml/tree');
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
            const res = await fetch(`http://localhost:8000/api/dashboard/history/${encodeURIComponent(deviceId)}`);
            const data = await res.json();
            
            if(data.timestamps && data.timestamps.length > 0) {
                const hardwareOption = {
                    backgroundColor: transparentBg,
                    tooltip: { 
                        trigger: 'axis',
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        textStyle: { color: '#fff' }
                    },
                    legend: { data: ['CPU %', 'RAM %'], textStyle: { color: '#ddd' } },
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

    // Listeners del HTML
    document.getElementById('load_metrics_btn').addEventListener('click', () => {
        const devId = document.getElementById('dashboard_device_id').value.trim();
        if(devId) {
            loadHardware(devId);
        } else {
            alert('Por favor ingresa un ID de equipo.');
        }
    });

    // Petición inicial vacía u opcional de hardware.
    // Opcional: Para efecto visual bonito de carga, la gráfica hardware inicia limpia
    hardwareChart.setOption({
        backgroundColor: transparentBg,
        title: { text: "Esperando ID de Dispositivo...", textStyle: { color: "#555" }, left: 'center', top:'center' }
    });

    // Hacer todos los gráficos responsivos
    window.addEventListener('resize', () => {
        hardwareChart.resize();
        accuracyChart.resize();
        treeChart.resize();
    });
});
