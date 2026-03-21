import psutil
import time
import subprocess

def test_disk():
    io1 = psutil.disk_io_counters()
    t1 = time.time()
    time.sleep(1)
    io2 = psutil.disk_io_counters()
    t2 = time.time()
    rt = io2.read_time - io1.read_time
    wt = io2.write_time - io1.write_time
    delta_ms = (t2 - t1) * 1000
    active = ((rt + wt) / delta_ms) * 100
    print(f"Disk Active: {min(100.0, active):.2f}%")

def test_gpu_wmi():
    try:
        out = subprocess.check_output("wmic path win32_VideoController get loadpercentage", shell=True).decode()
        print("WMIC GPU Load:", out.strip())
    except Exception as e:
        print("WMIC error:", e)

if __name__ == "__main__":
    test_disk()
    test_gpu_wmi()
