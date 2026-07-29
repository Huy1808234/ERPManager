r"""
PyInstaller Auto-Build Script for VLXD Thống Nhất
Builds BOTH One-File (Single .exe) and One-Dir modes with clean database setup.
"""

import subprocess
import sys
import os

def build_standalone_exe():
    print("==================================================")
    print("BAT DAU DONG GOI UNG DUNG VLXD THONG NHAT (.EXE)")
    print("==================================================")

    # 1. Kill any running old executable processes to unlock files
    try:
        subprocess.run(["taskkill", "/f", "/im", "VLXD_ThongNhat_SingleFile.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/f", "/im", "VLXD_ThongNhat.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    import shutil
    import time

    # Đã gỡ bỏ đoạn code Backup DB cũ ở đây vì DB hiện tại 
    # luôn được lưu an toàn trong %LOCALAPPDATA%\VLXD_ThongNhat
    # nên không bao giờ bị xóa khi build lại thư mục dist.

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    pyinstaller_bin = os.path.join(scripts_dir, "pyinstaller.exe")
    if not os.path.exists(pyinstaller_bin):
        pyinstaller_bin = "pyinstaller"

    # 2. BUILD SINGLE FILE MODE (--onefile)
    print("\n[1/2] Dang dong goi CHE DO 1 FILE .EXE DUY NHAT (Khong can thu muc _internal)...")
    cmd_onefile = [
        pyinstaller_bin,
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--hidden-import=plyer.platforms.win.notification",
        "--hidden-import=tkinterdnd2",
        "--hidden-import=fitz",
        "--collect-data=tkinterdnd2",
        "--icon=assets/app_icon.ico",
        "--paths=src",
        "--name=VLXD_ThongNhat_SingleFile",
        "src/main.py"
    ]
    subprocess.check_call(cmd_onefile)

    # Fix lỗi WinError 32: Chờ 2 giây để Windows Defender nhả file lock sau khi build bản 1 file
    print("... Dang cho 2 giay de Windows nha file lock ...")
    time.sleep(2)

    # 3. BUILD FOLDER MODE (--onedir)
    print("\n[2/2] Dang dong goi CHE DO THU MUC (Chay khoi dong sieu nhanh)...")
    cmd_onedir = [
        pyinstaller_bin,
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--hidden-import=plyer.platforms.win.notification",
        "--hidden-import=tkinterdnd2",
        "--hidden-import=fitz",
        "--collect-data=tkinterdnd2",
        "--icon=assets/app_icon.ico",
        "--paths=src",
        "--name=VLXD_ThongNhat",
        "src/main.py"
    ]
    subprocess.check_call(cmd_onedir)

    print("\n==================================================")
    print("HOAN TAT DONG GOI CA 2 CHE DO BAN MOI NHAT!")
    print("1. File 1 File duy nhat (khong thu muc phu): dist/VLXD_ThongNhat_SingleFile.exe")
    print("2. File dang thu muc (khoi dong nhanh): dist/VLXD_ThongNhat/VLXD_ThongNhat.exe")
    print("==================================================")

if __name__ == "__main__":
    build_standalone_exe()
