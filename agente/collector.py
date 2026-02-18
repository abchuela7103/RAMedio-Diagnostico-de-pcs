import psutil

def get_battery_info():
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged
            }
    except Exception:
        pass
    return None

def collect_metrics():
    metrics = {
        # Obtener uso de CPU
        "cpu": psutil.cpu_percent(interval=1),

        # Obtener uso de RAM
        "ram": psutil.virtual_memory().percent,

        # Obtener uso de DISCO
        "disk": psutil.disk_usage('/').percent,

        # Obtener estado de la bateria
        "battery": get_battery_info(),
    }

    return metrics