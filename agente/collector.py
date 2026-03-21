import psutil
import time
import subprocess

def get_disk_active_time():
    try:
        io1 = psutil.disk_io_counters()
        t1 = time.time()
        time.sleep(0.5)
        io2 = psutil.disk_io_counters()
        t2 = time.time()
        
        rt = io2.read_time - io1.read_time
        wt = io2.write_time - io1.write_time
        delta_ms = (t2 - t1) * 1000
        
        if delta_ms > 0:
            active_ratio = ((rt + wt) / delta_ms) * 100
            return min(100.0, active_ratio)
    except Exception:
        pass
    return 0.0

def get_gpu_usage():
    try:
        # Comando para extraer uso de GPU engine 3D en Windows, con timeout para no bloquear
        cmd = "powershell -NoProfile -Command \"(Get-WmiObject Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | Where-Object { $_.Name -match '3D' } | Measure-Object -Property UtilizationPercentage -Sum).Sum\""
        out = subprocess.check_output(cmd, shell=True, timeout=2).decode().strip()
        if out and out.isdigit():
            return float(out)
    except Exception:
        pass
    return 0.0

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
        "cpu": psutil.cpu_percent(interval=0.5),

        # Obtener uso de RAM
        "ram": psutil.virtual_memory().percent,

        # Obtener uso de DISCO (Espacio llenado)
        "disk": psutil.disk_usage('/').percent,

        # Obtener Actividad de DISCO (I/O tiempo activo)
        "disk_active": get_disk_active_time(),
        
        # Obtener uso de GPU
        "gpu": get_gpu_usage(),

        # Obtener estado de la bateria
        "battery": get_battery_info(),
    }

    return metrics