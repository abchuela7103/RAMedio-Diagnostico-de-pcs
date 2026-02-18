# Sistema Distribuido de Diagnóstico de PCs RAMedio


Hasta ahora se hizo el agente, solo recolecta 3 metricas, disco ram y cpu
se hizo el api para la recoleeccion de datos, hasta ahora el server es local, solo para hacer pruebas de que los datos se envien 
se levanto el server local es necesario activarlo desde su compu con uvicorn api:app
la data se guarda en un archivo json al momento de correr el agente 
el agente toma metricas cada 5s, se corre en el main 


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