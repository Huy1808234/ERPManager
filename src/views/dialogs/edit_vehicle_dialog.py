import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import vehicle_dao

class EditVehicleDialog(tk.Toplevel):
    def __init__(self, parent, vehicle, on_success_callback=None):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.vehicle = vehicle
        
        self.title("Sửa Thông Tin Xe")
        self.geometry("380x340")
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Cập Nhật Thông Tin Xe & Tài Xế", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(self, padding=10)
        form.pack(fill="both", expand=True)

        v = self.vehicle
        fields = [
            ("Biển số xe:", "ent_plate", v['plate_number']),
            ("Họ tên tài xế:", "ent_driver", v['driver_name']),
            ("Số điện thoại:", "ent_phone", v['phone'] or ""),
            ("Dung tích xe (m³):", "ent_cap", str(v['capacity_m3'])),
            ("Thù lao cho tài xế (đ/chuyến):", "ent_pay", str(int(v['pay_per_trip']))),
            ("Định mức xăng dầu (đ/chuyến):", "ent_fuel", str(int(v['fuel_per_trip']))),
        ]

        self.entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=22)
            ent.insert(0, default_val)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            self.entries[var_name] = ent

        tk.Button(self, text=" Cập Nhật Xe", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=self.update_v).pack(pady=10)

    def update_v(self):
        try:
            vehicle_dao.update_vehicle(
                self.vehicle['id'],
                self.entries["ent_plate"].get().strip().upper(),
                self.entries["ent_driver"].get().strip(),
                self.entries["ent_phone"].get().strip(),
                float(self.entries["ent_cap"].get() or config.DEFAULT_VEHICLE_CAPACITY),
                float(self.entries["ent_pay"].get() or 50000),
                float(self.entries["ent_fuel"].get() or 30000)
            )
            messagebox.showinfo("Thành công", f"Đã cập nhật xe {self.entries['ent_plate'].get()}!")
            self.destroy()
            if self.on_success_callback:
                self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật xe: {str(e)}")
