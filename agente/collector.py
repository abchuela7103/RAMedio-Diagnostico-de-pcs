import psutil

#############################   PODEMOS AÑADIR EN ESTA PARTE QUE RECOJA DATOS SOBRE LOS SENSORES DE TEMPERATURA 
#############################   TAMBIEN SENSORES DE ESTADO DE LA BATERIA Y DE VENTILADORES, PERO DEPENDE DEL OS 
#############################   SI SON NULL O SI NOS DECUELVE UN VALOR

def collect_metrics():
    metrics = {
        #obtener uso de CPU
        "cpu": psutil.cpu_percent(interval=1),

        #obtener uso de RAM
        "ram": psutil.virtual_memory().percent,

        #obtener uso de DISCO
        "disk": psutil.disk_usage('/').percent
    }

    return metrics