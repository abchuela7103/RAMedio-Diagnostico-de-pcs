# Sistema Distribuido de Diagnóstico de PCs RAMedio

Hasta ahora se hizo el agente, recolecta 4 metricas: disco, ram, cpu y bateria. El agente toma metricas cada 5s, se corre en el main. La data (json) se envía al servidor.
Se hizo el api (FastAPI) para la recolección de los datos, guardándolos en base de datos (PostgreSQL / local `ramedio.db`). Es necesario activarlo desde su compu con uvicorn api:app.
Adicionalmente, se creó una interfaz web (`web/index.html`) para recolectar los síntomas visuales del usuario.
Finalmente el modelo de ML cruza el hardware (agente) y síntomas (web) para generar un diagnóstico inteligente.

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

El agente recolecta métricas cada 5 segundos.

## Entrenar modelo ML (solo la primera vez)

Desde la raíz del proyecto entrenar árbol de decisión:
python ML/train_model.py

## Interfaz Web de Diagnóstico

Abrir el archivo `web/index.html` en tu navegador, llenar el formulario de síntomas y ver el resultado.