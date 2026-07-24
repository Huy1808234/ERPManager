r"""
Auto-Reload / Hot-Reload Dev Runner for VLXD Thống Nhất
Monitors .py file changes and automatically restarts main.py in real-time when you save code!
Command to run:
& "$env:LocalAppData\Programs\Python\Python312\python.exe" dev_run.py
"""

import subprocess
import time
import sys
import os

WATCH_DIR = os.path.dirname(os.path.abspath(__file__))

def get_py_files_mtime():
    """Get max modification time across all .py files in project"""
    mtimes = []
    for root, dirs, files in os.walk(WATCH_DIR):
        # Skip __pycache__ and build folders
        if "__pycache__" in root or "build" in root or "dist" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "dev_run.py":
                file_path = os.path.join(root, file)
                try:
                    mtimes.append(os.path.getmtime(file_path))
                except OSError:
                    pass
    return max(mtimes) if mtimes else 0

def start_dev_mode():
    print("==========================================================")
    print(" 🚀 KÍCH HOẠT CHẾ ĐỘ AUTO-RELOAD (TỰ TẢI LẠI KHI SỬA CODE)")
    print(" Đang theo dõi các file code .py trong dự án...")
    print(" Bạn chỉ cần SỬA & LƯU CODE, phần mềm sẽ tự động bật lại!")
    print("==========================================================")

    main_script = os.path.join(WATCH_DIR, "main.py")
    last_mtime = get_py_files_mtime()
    
    # Launch main.py initially
    process = subprocess.Popen([sys.executable, main_script])

    try:
        while True:
            time.sleep(0.5)  # Check every 0.5s
            current_mtime = get_py_files_mtime()

            if current_mtime > last_mtime:
                print("\n🔄 PHÁT HIỆN THAY ĐỔI CODE! Đang tự động nạp lại phần mềm...")
                last_mtime = current_mtime
                
                # Kill running process
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()

                # Restart main.py
                process = subprocess.Popen([sys.executable, main_script])

    except KeyboardInterrupt:
        print("\nĐã dừng chế độ Auto-Reload.")
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    start_dev_mode()
