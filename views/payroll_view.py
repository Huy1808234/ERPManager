"""
Employee Payroll & Salary Management View for VLXD Thống Nhất (Tân Phước)
Calculates base salary, trip pay for drivers, allowances, advances, and net salaries.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from utils import num2vietnamese_words

class PayrollView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_payroll_data()

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
        tk.Button(btn_bar, text="🔄 Tải Lại Bảng Lương", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_payroll_data).pack(side="right")

        # Payroll Table
        columns = ("id", "code", "name", "position", "salary_type", "base_salary", "trips", "trip_pay", "allowance", "gross", "advances", "net")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Mã NV")
        self.tree.heading("name", text="Họ Tên Nhân Viên")
        self.tree.heading("position", text="Vị Trí / Chức Vụ")
        self.tree.heading("salary_type", text="Hình Thức Lương")
        self.tree.heading("base_salary", text="Lương Cứng Tháng")
        self.tree.heading("trips", text="Số Chuyến Đã Chạy")
        self.tree.heading("trip_pay", text="Tổng Lương Chuyến")
        self.tree.heading("allowance", text="Phụ Cấp / Thưởng")
        self.tree.heading("gross", text="TỔNG THU NHẬP")
        self.tree.heading("advances", text="ĐÃ TẠM ỨNG")
        self.tree.heading("net", text="THỰC LĨNH")

        self.tree.column("id", width=35)
        self.tree.column("code", width=80)
        self.tree.column("name", width=160)
        self.tree.column("position", width=160)
        self.tree.column("salary_type", width=110)
        self.tree.column("base_salary", width=120)
        self.tree.column("trips", width=120)
        self.tree.column("trip_pay", width=120)
        self.tree.column("allowance", width=120)
        self.tree.column("gross", width=130)
        self.tree.column("advances", width=110)
        self.tree.column("net", width=130)

        # Style tags
        self.tree.tag_configure("driver", background="#f0fdf4")
        self.tree.tag_configure("staff", background="#ffffff")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_payroll_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        payroll = database.get_payroll_summary()
        total_gross = 0
        total_advances = 0
        total_net = 0

        for p in payroll:
            total_gross += p['gross_salary']
            total_advances += p['advances']
            total_net += p['net_salary']

            tag = "driver" if p['salary_type'] == "Theo chuyến" else "staff"
            trips_str = f"{p['trips_count']} chuyến" if p['salary_type'] == "Theo chuyến" else "-"

            self.tree.insert("", "end", values=(
                p['id'],
                p['code'],
                p['name'],
                p['position'],
                p['salary_type'],
                f"{p['base_salary']:,.0f}đ",
                trips_str,
                f"{p['trip_pay']:,.0f}đ",
                f"{p['allowance']:,.0f}đ",
                f"{p['gross_salary']:,.0f}đ",
                f"{p['advances']:,.0f}đ",
                f"{p['net_salary']:,.0f}đ"
            ), tags=(tag,))

        self.lbl_stats.config(
            text=f"📊 Quỹ Lương: {total_gross:,.0f}đ | Đã ứng: {total_advances:,.0f}đ | THỰC LĨNH: {total_net:,.0f}đ"
        )

    def open_add_employee_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Nhân Viên Mới")
        dlg.geometry("420x420")
        dlg.grab_set()

        ttk.Label(dlg, text="TẠO HỒ SƠ NHÂN VIÊN MỚI", font=("Segoe UI", 12, "bold"), foreground="#1e3a8a").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã nhân viên (vd: NV006):", "ent_code"),
            ("Họ tên nhân viên:", "ent_name"),
            ("Số điện thoại:", "ent_phone"),
            ("Vị trí / Chức vụ:", "cbo_position"),
            ("Hình thức lương:", "cbo_type"),
            ("Lương cứng tháng (đ):", "ent_base"),
            ("Thù lao/chuyến (nếu là tài xế):", "ent_trip"),
            ("Phụ cấp / Thưởng (đ):", "ent_allowance"),
        ]

        entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            if var_name == "cbo_position":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=[
                    "Tài xế xe ben",
                    "Lái xe múc cát/đá",
                    "Kế toán bán hàng",
                    "Quản lý bãi & Bốc xếp",
                    "Bảo vệ bãi"
                ])
                cbo.current(0)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = cbo
            elif var_name == "cbo_type":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=["Theo chuyến", "Lương tháng"])
                cbo.current(0)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = cbo
            else:
                ent = ttk.Entry(form, width=25)
                ent.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = ent

        entries["ent_code"].insert(0, f"NV00{len(database.get_all_employees()) + 1}")
        entries["ent_base"].insert(0, "0")
        entries["ent_trip"].insert(0, "50000")
        entries["ent_allowance"].insert(0, "500000")

        def save_emp():
            try:
                code = entries["ent_code"].get().strip()
                name = entries["ent_name"].get().strip()
                if not name:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên nhân viên!")
                    return

                database.add_employee(
                    code,
                    name,
                    entries["ent_phone"].get().strip(),
                    entries["cbo_position"].get(),
                    entries["cbo_type"].get(),
                    float(entries["ent_base"].get() or 0),
                    float(entries["ent_trip"].get() or 0),
                    float(entries["ent_allowance"].get() or 0)
                )
                messagebox.showinfo("Thành công", f"Đã thêm hồ sơ nhân viên [{name}]!")
                dlg.destroy()
                self.load_payroll_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm nhân viên: {str(e)}")

        tk.Button(dlg, text="💾 LƯU NHÂN VIÊN", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=save_emp).pack(pady=10)

    def open_edit_employee_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần sửa từ danh sách!")
            return

        values = self.tree.item(selected_item[0])['values']
        emp_id = values[0]

        employees = database.get_all_employees()
        e_list = [e for e in employees if e['id'] == emp_id]
        if not e_list:
            return
        e = e_list[0]

        dlg = tk.Toplevel(self)
        dlg.title("Sửa Hồ Sơ Nhân Viên")
        dlg.geometry("420x420")
        dlg.grab_set()

        ttk.Label(dlg, text="CẬP NHẬT LƯƠNG & HỒ SƠ NHÂN VIÊN", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã nhân viên:", "ent_code", e['code']),
            ("Họ tên nhân viên:", "ent_name", e['name']),
            ("Số điện thoại:", "ent_phone", e['phone'] or ""),
            ("Vị trí / Chức vụ:", "cbo_position", e['position']),
            ("Hình thức lương:", "cbo_type", e['salary_type']),
            ("Lương cứng tháng (đ):", "ent_base", str(int(e['base_salary']))),
            ("Thù lao/chuyến (đ):", "ent_trip", str(int(e['pay_per_trip']))),
            ("Phụ cấp / Thưởng (đ):", "ent_allowance", str(int(e['allowance']))),
        ]

        entries = {}
        for i, (label_text, var_name, default_val) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            if var_name == "cbo_position":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=[
                    "Tài xế xe ben",
                    "Lái xe múc cát/đá",
                    "Kế toán bán hàng",
                    "Quản lý bãi & Bốc xếp",
                    "Bảo vệ bãi"
                ])
                cbo.set(default_val)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = cbo
            elif var_name == "cbo_type":
                cbo = ttk.Combobox(form, width=22, state="readonly", values=["Theo chuyến", "Lương tháng"])
                cbo.set(default_val)
                cbo.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = cbo
            else:
                ent = ttk.Entry(form, width=25)
                ent.insert(0, default_val)
                ent.grid(row=i, column=1, pady=3, sticky="ew")
                entries[var_name] = ent

        def update_emp():
            try:
                code = entries["ent_code"].get().strip()
                name = entries["ent_name"].get().strip()
                if not name:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên nhân viên!")
                    return

                database.update_employee(
                    emp_id,
                    code,
                    name,
                    entries["ent_phone"].get().strip(),
                    entries["cbo_position"].get(),
                    entries["cbo_type"].get(),
                    float(entries["ent_base"].get() or 0),
                    float(entries["ent_trip"].get() or 0),
                    float(entries["ent_allowance"].get() or 0)
                )
                messagebox.showinfo("Thành công", f"Đã cập nhật hồ sơ nhân viên [{name}]!")
                dlg.destroy()
                self.load_payroll_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật nhân viên: {str(e)}")

        tk.Button(dlg, text="💾 CẬP NHẬT HỒ SƠ", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=update_emp).pack(pady=10)

    def delete_selected_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return

        values = self.tree.item(selected_item[0])['values']
        emp_id = values[0]
        emp_name = values[2]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA nhân viên [{emp_name}] khỏi hệ thống bảng lương?"):
            try:
                database.delete_employee(emp_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công nhân viên [{emp_name}]!")
                self.load_payroll_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def open_advance_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần tạm ứng lương!")
            return

        values = self.tree.item(selected_item[0])['values']
        emp_id = values[0]
        emp_name = values[2]

        dlg = tk.Toplevel(self)
        dlg.title("Ghi Nhận Tạm Ứng Lương")
        dlg.geometry("400x280")
        dlg.grab_set()

        ttk.Label(dlg, text=f"TẠM ỨNG LƯƠNG: {emp_name.upper()}", font=("Segoe UI", 12, "bold"), foreground="#059669").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Số tiền tạm ứng (đ):").grid(row=0, column=0, sticky="w", pady=5)
        ent_amount = ttk.Entry(form, width=25)
        ent_amount.insert(0, "1000000")
        ent_amount.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Bằng chữ:").grid(row=1, column=0, sticky="w", pady=5)
        lbl_words = ttk.Label(form, text="Một triệu đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#0369a1")
        lbl_words.grid(row=1, column=1, sticky="w", pady=5)

        def on_amount_change(event=None):
            val = ent_amount.get().strip()
            lbl_words.config(text=num2vietnamese_words(val))

        ent_amount.bind("<KeyRelease>", on_amount_change)

        ttk.Label(form, text="Ghi chú lý do ứng:").grid(row=2, column=0, sticky="w", pady=5)
        ent_note = ttk.Entry(form, width=25)
        ent_note.insert(0, "Ứng lương giữa tháng")
        ent_note.grid(row=2, column=1, pady=5)

        def save_advance():
            try:
                amount = float(ent_amount.get() or 0)
                note = ent_note.get()

                database.record_salary_advance(emp_id, amount, note)
                messagebox.showinfo("Thành công", f"Đã ghi nhận tạm ứng {amount:,.0f}đ cho nhân viên {emp_name}!")
                dlg.destroy()
                self.load_payroll_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể ghi nhận tạm ứng: {str(e)}")

        tk.Button(dlg, text="💾 GHI NHẬN TẠM ỨNG", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), command=save_advance).pack(pady=10)
