"""
Fleet Dispatch & Driver Trip Counter View for VLXD Thống Nhất
Refactored into Component-based UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dao import vehicle_dao

from views.components.dispatch_table import DispatchTable
from views.dialogs.add_vehicle_dialog import AddVehicleDialog
from views.dialogs.edit_vehicle_dialog import EditVehicleDialog

class DispatchView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="🚚 ĐIỀU PHỐI XE & THÙ LAO TÀI XẾ THEO CHUYẾN", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Operating Hours Banner
        time_info = ttk.Label(title_frame, text="⏱️ Giờ chạy bãi: 06:00 - 18:00 (T2-T7) | 06:00 - 17:00 (CN)", font=("Segoe UI", 9, "bold"), foreground="#059669")
        time_info.pack(side="right")

        # Button Control Bar
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="➕ Thêm Xe Mới", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_vehicle_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Xe / Tài Xế", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_vehicle_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Xe", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_vehicle).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Danh Sách", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_data).pack(side="right")

        # Dispatch Table Component
        self.dispatch_table = DispatchTable(self)
        self.dispatch_table.pack(fill="both", expand=True)

    def load_data(self):
        self.dispatch_table.load_dispatch_data()

    def on_dialog_success(self):
        self.load_data()
        if self.refresh_callback:
            self.refresh_callback()

    def open_add_vehicle_dialog(self):
        AddVehicleDialog(self, on_success_callback=self.on_dialog_success)

    def open_edit_vehicle_dialog(self):
        veh = self.dispatch_table.get_selected_vehicle()
        if not veh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn xe cần sửa từ danh sách!")
            return

        v_id = veh[0]
        vehicles = vehicle_dao.get_all_vehicles()
        v_list = [v for v in vehicles if v['id'] == v_id]
        if not v_list:
            return
            
        EditVehicleDialog(self, vehicle=v_list[0], on_success_callback=self.on_dialog_success)

    def delete_selected_vehicle(self):
        veh = self.dispatch_table.get_selected_vehicle()
        if not veh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn xe cần xóa!")
            return

        v_id = veh[0]
        plate = veh[1]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA xe biển số [{plate}] khỏi hệ thống?"):
            try:
                vehicle_dao.delete_vehicle(v_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công xe [{plate}]!")
                self.on_dialog_success()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa xe: {str(e)}")
