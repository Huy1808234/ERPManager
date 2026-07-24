r"""
PyInstaller Auto-Build Script for VLXD Thống Nhất
Builds BOTH One-File (Single .exe) and One-Dir modes.
"""

import subprocess
import sys
import os

def build_standalone_exe():
    print("==================================================")
    print("BAT DAU DONG GOI UNG DUNG VLXD THONG NHAT (.EXE)")
    print("==================================================")

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

    # 1. BUILD SINGLE FILE MODE (--onefile): NO _internal FOLDER NEEDED!
    print("\n[1/2] Dang dong goi CHE DO 1 FILE .EXE DUY NHAT (Khong can thu muc _internal)...")
    cmd_onefile = [
        pyinstaller_bin,
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=VLXD_ThongNhat_SingleFile",
        "--add-data=vlxd_thongnhat.db;.",
        "main.py"
    ]
    subprocess.check_call(cmd_onefile)

    # 2. BUILD FOLDER MODE (--onedir)
    print("\n[2/2] Dang dong goi CHE DO THU MUC (Chay khoi dong sieu nhanh)...")
    cmd_onedir = [
        pyinstaller_bin,
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=VLXD_ThongNhat",
        "--add-data=vlxd_thongnhat.db;.",
        "main.py"
    ]
    subprocess.check_call(cmd_onedir)

    print("\n==================================================")
    print("HOAN TAT DONG GOI CA 2 CHE DO!")
    print("1. File 1 File duy nhat (khong thu muc phu): dist/VLXD_ThongNhat_SingleFile.exe")
    print("2. File dang thu muc (khoi dong nhanh): dist/VLXD_ThongNhat/VLXD_ThongNhat.exe")
    print("==================================================")

if __name__ == "__main__":
    build_standalone_exe()
