import tkinter as tk
from tkinter import ttk
from dao import employee_dao

class PayrollTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
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
        self.tree.column("base_salary", width=120, anchor="e")
        self.tree.column("trips", width=120, anchor="center")
        self.tree.column("trip_pay", width=120, anchor="e")
        self.tree.column("allowance", width=120, anchor="e")
        self.tree.column("gross", width=130, anchor="e")
        self.tree.column("advances", width=110, anchor="e")
        self.tree.column("net", width=130, anchor="e")

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

        payroll = employee_dao.get_payroll_summary()
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

        return total_gross, total_advances, total_net
        
    def get_selected_employee(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        values = self.tree.item(selected_item[0])['values']
        return values
