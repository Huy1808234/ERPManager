"""
Fleet Dispatch & Driver Trip Counter View for VLXD Thống Nhất
Tracks vehicle status, daily trips per driver, trip pay, fuel allowance, and full CRUD.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database

class DispatchView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_dispatch_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="🚚 ĐIỀU PHỐI XE & THỦ LAO TÀI XẾ THEO CHUYẾN", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Operating Hours Banner
        time_info = ttk.Label(title_frame, text="⏱️ Giờ chạy bãi: 06:00 - 18:00 (T2-T7) | 06:00 - 17:00 (CN)", font=("Segoe UI", 9, "bold"), foreground="#059669")
        time_info.pack(side="right")

        # Button Control Bar
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="🚛 Thêm Xe Mới", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_vehicle_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Xe / Tài Xế", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_vehicle_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Xe", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_vehicle).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Danh Sách", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_dispatch_data).pack(side="right")

        # Dispatch Table
        columns = ("id", "plate", "driver", "capacity", "trips", "delivered_vol", "pay_per_trip", "total_pay", "fuel_est")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("plate", text="Biển Số Xe")
        self.tree.heading("driver", text="Tài Xế Phụ Trách")
        self.tree.heading("capacity", text="Sức Chứa (m³)")
        self.tree.heading("trips", text="Tổng Số Chuyến Đã Chạy")
        self.tree.heading("delivered_vol", text="Tổng Khối Lượng Giao")
        self.tree.heading("pay_per_trip", text="Thù Lao/Chuyến")
        self.tree.heading("total_pay", text="Tổng Tiền Lương Chuyến")
        self.tree.heading("fuel_est", text="Định Mức Xăng Dầu")

        self.tree.column("id", width=40)
        self.tree.column("plate", width=120)
        self.tree.column("driver", width=180)
        self.tree.column("capacity", width=100)
        self.tree.column("trips", width=150)
        self.tree.column("delivered_vol", width=140)
        self.tree.column("pay_per_trip", width=120)
        self.tree.column("total_pay", width=140)
        self.tree.column("fuel_est", width=130)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_dispatch_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        dispatch_summary = database.get_driver_trip_summary()
        vehicles = database.get_all_vehicles()
        veh_map = {v['plate_number']: v['id'] for v in vehicles}

        for d in dispatch_summary:
            total_trips = d['total_trips']
            pay_per_trip = d['pay_per_trip']
            fuel_per_trip = d['fuel_per_trip']
            total_pay = total_trips * pay_per_trip
            total_fuel = total_trips * fuel_per_trip
            v_id = veh_map.get(d['plate_number'], 0)

            self.tree.insert("", "end", values=(
                v_id,
                d['plate_number'],
                d['driver_name'],
                f"{d.get('capacity_m3', 2.2):,.1f} m³",
                f"{total_trips} chuyến",
                f"{d['total_volume_delivered']:,.1f} m³",
                f"{pay_per_trip:,.0f}đ",
                f"{total_pay:,.0f}đ",
                f"{total_fuel:,.0f}đ"
            ))

    def open_add_vehicle_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Xe & Tài Xế Bãi")
        dlg.geometry("380x340")
        dlg.grab_set()

        ttk.Label(dlg, text="Đăng Ký Xe & Tài Xế Mới", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Biển số xe (vd: 60C-999.88):", "ent_plate"),
            ("Họ tên tài xế:", "ent_driver"),
            ("Số điện thoại:", "ent_phone"),
            ("Dung tích thùng xe (m³):", "ent_cap"),
            ("Thù lao cho tài xế (đ/chuyến):", "ent_pay"),
            ("Định mức xăng dầu (đ/chuyến):", "ent_fuel"),
        ]

        entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=22)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            entries[var_name] = ent

        entries["ent_cap"].insert(0, "2.2")
        entries["ent_pay"].insert(0, "50000")
        entries["ent_fuel"].insert(0, "30000")

        def save_vehicle():
            try:
                database.add_vehicle(
                    entries["ent_plate"].get().strip().upper(),
                    entries["ent_driver"].get().strip(),
                    entries["ent_phone"].get().strip(),
                    float(entries["ent_cap"].get() or 2.2),
                    float(entries["ent_pay"].get() or 50000),
                    float(entries["ent_fuel"].get() or 30000)
                )
                messagebox.showinfo("Thành công", "Đã đăng ký thêm xe mới!")
                dlg.destroy()
                self.load_dispatch_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm xe: {str(e)}")

        tk.Button(dlg, text="Lưu Đăng Ký Xe", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=save_vehicle).pack(pady=10)

    def open_edit_vehicle_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn xe cần sửa từ danh sách!")
            return

        values = self.tree.item(selected_item[0])['values']
        v_id = values[0]

        vehicles = database.get_all_vehicles()
        v_list = [v for v in vehicles if v['id'] == v_id]
        if not v_list:
            return
        v = v_list[0]

        dlg = tk.Toplevel(self)
        dlg.title("Sửa Thông Tin Xe")
        dlg.geometry("380x340")
        dlg.grab_set()

        ttk.Label(dlg, text="Cập Nhật Thông Tin Xe & Tài Xế", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Biển số xe:", "ent_plate", v['plate_number']),
            ("Họ tên tài xế:", "ent_driver", v['driver_name']),
            ("Số điện thoại:", "ent_phone", v['phone'] or ""),
            ("Dung tích xe (m³):", "ent_cap", str(v['capacity_m3'])),
            ("Thù lao cho tài xế (đ/chuyến):", "ent_pay", str(int(v['pay_per_trip']))),
            ("Định mức xăng dầu (đ/chuyến):", "ent_fuel", str(int(v['fuel_per_trip']))),
        ]

        entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=22)
            ent.insert(0, default_val)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            entries[var_name] = ent

        def update_v():
            try:
                database.update_vehicle(
                    v_id,
                    entries["ent_plate"].get().strip().upper(),
                    entries["ent_driver"].get().strip(),
                    entries["ent_phone"].get().strip(),
                    float(entries["ent_cap"].get() or 2.2),
                    float(entries["ent_pay"].get() or 50000),
                    float(entries["ent_fuel"].get() or 30000)
                )
                messagebox.showinfo("Thành công", f"Đã cập nhật xe {entries['ent_plate'].get()}!")
                dlg.destroy()
                self.load_dispatch_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật xe: {str(e)}")

        tk.Button(dlg, text="💾 Cập Nhật Xe", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=update_v).pack(pady=10)

    def delete_selected_vehicle(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn xe cần xóa!")
            return

        values = self.tree.item(selected_item[0])['values']
        v_id = values[0]
        plate = values[1]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA xe biển số [{plate}] khỏi hệ thống?"):
            try:
                database.delete_vehicle(v_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công xe [{plate}]!")
                self.load_dispatch_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa xe: {str(e)}")
