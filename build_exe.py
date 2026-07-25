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
    db_backup_path = "vlxd_thongnhat_backup.db"
    db_original_path = os.path.join("dist", "VLXD_ThongNhat", "vlxd_thongnhat.db")
    
    # BACKUP DB before pyinstaller deletes the dist folder
    if os.path.exists(db_original_path):
        print(f"[*] Dang sao luu du lieu tu {db_original_path}...")
        try:
            shutil.copy2(db_original_path, db_backup_path)
        except Exception as e:
            print(f"Loi sao luu: {e}")

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
        "--collect-data=tkinterdnd2",
        "--icon=assets/app_icon.ico",
        "--paths=src",
        "--name=VLXD_ThongNhat_SingleFile",
        "src/main.py"
    ]
    subprocess.check_call(cmd_onefile)

    # 3. BUILD FOLDER MODE (--onedir)
    print("\n[2/2] Dang dong goi CHE DO THU MUC (Chay khoi dong sieu nhanh)...")
    cmd_onedir = [
        pyinstaller_bin,
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--hidden-import=plyer.platforms.win.notification",
        "--hidden-import=tkinterdnd2",
        "--collect-data=tkinterdnd2",
        "--icon=assets/app_icon.ico",
        "--paths=src",
        "--name=VLXD_ThongNhat",
        "src/main.py"
    ]
    subprocess.check_call(cmd_onedir)

    # RESTORE DB after pyinstaller finishes
    if os.path.exists(db_backup_path):
        print("\n[*] Dang phuc hoi lai du lieu (Database) vao thu muc vua build...")
        try:
            shutil.copy2(db_backup_path, db_original_path)
            # Optionally remove the backup after restoring
            os.remove(db_backup_path)
            print("[+] Phuc hoi hoan tat!")
        except Exception as e:
            print(f"Loi phuc hoi du lieu: {e}")

    print("\n==================================================")
    print("HOAN TAT DONG GOI CA 2 CHE DO BAN MOI NHAT!")
    print("1. File 1 File duy nhat (khong thu muc phu): dist/VLXD_ThongNhat_SingleFile.exe")
    print("2. File dang thu muc (khoi dong nhanh): dist/VLXD_ThongNhat/VLXD_ThongNhat.exe")
    print("==================================================")

if __name__ == "__main__":
    build_standalone_exe()
