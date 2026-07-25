"""
Employee Payroll & Salary Management View for VLXD Thống Nhất (Tân Phước)
Refactored into Component-based UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dao import employee_dao

from views.components.payroll_table import PayrollTable
from views.dialogs.add_employee_dialog import AddEmployeeDialog
from views.dialogs.edit_employee_dialog import EditEmployeeDialog
from views.dialogs.salary_advance_dialog import SalaryAdvanceDialog

class PayrollView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="💵 QUẢN LÝ BẢNG LƯƠNG & TẠM ỨNG LƯƠNG NHÂN VIÊN", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Live Statistics Summary Banner
        self.lbl_stats = ttk.Label(title_frame, text="📊 Đang tính toán quỹ lương...", font=("Segoe UI", 10, "bold"), foreground="#047857")
        self.lbl_stats.pack(side="right")

        # Top Control Bar (Add, Edit, Delete, Advance)
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="➕ Thêm Nhân Viên", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_employee_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Nhân Viên / Lương", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_employee_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Nhân Viên", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_employee).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="💵 Ghi Nhận Tạm Ứng", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_advance_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Bảng Lương", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_data).pack(side="right")

        # Payroll Table Component
        self.payroll_table = PayrollTable(self)
        self.payroll_table.pack(fill="both", expand=True)

    def load_data(self):
        total_gross, total_advances, total_net = self.payroll_table.load_payroll_data()
        self.lbl_stats.config(
            text=f"📊 Quỹ Lương: {total_gross:,.0f}đ | Đã ứng: {total_advances:,.0f}đ | THỰC LĨNH: {total_net:,.0f}đ"
        )

    def on_dialog_success(self):
        self.load_data()
        if self.refresh_callback:
            self.refresh_callback()

    def open_add_employee_dialog(self):
        AddEmployeeDialog(self, on_success_callback=self.on_dialog_success)

    def open_edit_employee_dialog(self):
        emp = self.payroll_table.get_selected_employee()
        if not emp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần sửa từ danh sách!")
            return

        emp_id = emp[0]
        employees = employee_dao.get_all_employees()
        e_list = [e for e in employees if e['id'] == emp_id]
        if not e_list:
            return
            
        EditEmployeeDialog(self, employee=e_list[0], on_success_callback=self.on_dialog_success)

    def delete_selected_employee(self):
        emp = self.payroll_table.get_selected_employee()
        if not emp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return

        emp_id = emp[0]
        emp_name = emp[2]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA nhân viên [{emp_name}] khỏi hệ thống bảng lương?"):
            try:
                employee_dao.delete_employee(emp_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công nhân viên [{emp_name}]!")
                self.on_dialog_success()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def open_advance_dialog(self):
        emp = self.payroll_table.get_selected_employee()
        if not emp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần tạm ứng lương!")
            return

        emp_id = emp[0]
        emp_name = emp[2]
        
        SalaryAdvanceDialog(self, emp_id=emp_id, emp_name=emp_name, on_success_callback=self.on_dialog_success)
