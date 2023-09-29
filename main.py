import subprocess
import psutil
import time
import os

while True:
    last_time = os.path.getmtime("audio_visualizer.config")
    cmd = ["/home/mxfxm/.pyenv/versions/3.8.15/bin/python", "/home/mxfxm/Repositories/led_wall_simulator/audio_visualizer.py"]
    process  = subprocess.Popen(cmd)

    while True:
        time.sleep(0.1)

        running = False
        for proc in psutil.process_iter():
            if proc.pid == process.pid:
                if proc.status() != psutil.STATUS_ZOMBIE:
                    running = True
                    break
                else:
                    print("killing zombie")
                    os.system(f"sudo kill -9 {process.pid}")
        if not running:
            print("restart not running")
            break

        if os.path.getmtime("audio_visualizer.config") != last_time:
            os.system(f"sudo kill -9 {process.pid}")
            print("restart modified config")
            break