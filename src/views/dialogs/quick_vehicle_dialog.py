import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import vehicle_dao

def open_quick_vehicle_dialog(parent):
    dlg = tk.Toplevel(parent)
    dlg.title("Thêm Xe Nhanh")
    dlg.geometry("380x300")
    dlg.grab_set()

    ttk.Label(dlg, text="TẠO NHANH THÔNG TIN XE", font=("Segoe UI", 11, "bold"), foreground=config.COLOR_WARNING).pack(pady=10)

    form = ttk.Frame(dlg, padding=10)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="Biển số xe (vd: 60C-999.88):").grid(row=0, column=0, sticky="w", pady=3)
    ent_plate = ttk.Entry(form, width=22)
    ent_plate.grid(row=0, column=1, pady=3)

    ttk.Label(form, text="Tên tài xế phụ trách:").grid(row=1, column=0, sticky="w", pady=3)
    ent_driver = ttk.Entry(form, width=22)
    ent_driver.grid(row=1, column=1, pady=3)

    ttk.Label(form, text="Dung tích xe (m³):").grid(row=2, column=0, sticky="w", pady=3)
    ent_cap = ttk.Entry(form, width=22)
    ent_cap.insert(0, str(config.DEFAULT_VEHICLE_CAPACITY))
    ent_cap.grid(row=2, column=1, pady=3)

    def save_quick_vehicle():
        plate = ent_plate.get().strip().upper()
        driver = ent_driver.get().strip()
        if not plate or not driver:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập biển số xe và tên tài xế!")
            return
        try:
            vehicle_dao.add_vehicle(plate, driver, "", float(ent_cap.get() or config.DEFAULT_VEHICLE_CAPACITY), config.DEFAULT_PAY_PER_TRIP, config.DEFAULT_FUEL_PER_TRIP)
            messagebox.showinfo("Thành công", f"Đã đăng ký xe: {plate}")
            dlg.destroy()
            parent.load_data()
            for i, v in enumerate(parent.vehicles):
                if v['plate_number'] == plate:
                    parent.cbo_vehicle.current(i)
                    parent.on_vehicle_change(None)
                    break
            if parent.refresh_callback:
                parent.refresh_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xe: {str(e)}")

    tk.Button(dlg, text=" LƯU THÔNG TIN XE", bg=config.COLOR_WARNING, fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_vehicle).pack(pady=10)
