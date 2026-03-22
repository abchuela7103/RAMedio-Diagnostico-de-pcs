# Sistema Distribuido de Diagnóstico de PCs RAMedio

El agente cuenta con una interfaz gráfica y recolecta 5 métricas promediadas (disco, ram, cpu, gpu y bateria). La recolección se hace a petición del usuario y la data (json) se envía al servidor.
Se hizo un API (FastAPI) para la recolección de los datos, guardándolos en base de datos (PostgreSQL / local `ramedio.db`). Es necesario activarlo localmente con `uvicorn api:app`.
Adicionalmente, se creó una interfaz web (`web/index.html`) para recolectar los síntomas visuales del usuario.
Finalmente el modelo de ML cruza el hardware (agente) y la información sintomatológica (web) para generar un diagnóstico inteligente.

## Arquitectura

Agente → API FastAPI → PostgreSQL → ML 

## Instalación

1. Clonar repositorio:

git clone <repo>
cd proyecto_modular

2. Instalar dependencias:

pip install -r requirements.txt

3. Crear archivo .env basado en .env.example

## Ejecutar servidor

cd server
uvicorn api:app

## Ejecutar agente

cd agente
python main.py

Se abrirá una ventana gráfica. Pulsa "Iniciar Recolección", el agente tomará 5 muestras para promediarlas y enviarlas al servidor. Al terminar, aparecerá un botón que te llevará directamente al formulario web.

## Entrenar modelo ML (solo la primera vez)

Desde la raíz del proyecto entrenar árbol de decisión:
python ML/train_model.py

## Interfaz Web de Diagnóstico

Abrir el archivo `web/index.html` en tu navegador, llenar el formulario de síntomas y ver el resultado.