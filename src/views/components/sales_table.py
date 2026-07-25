import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import config
from dao import order_dao

class SalesHistoryTable(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text=" Lịch Sử Đơn Xuất Kho Gần Đây ", padding=10)
        
        self.setup_ui()
        self.load_orders_table()

    def setup_ui(self):
        # Bộ Lọc
        filter_bar = ttk.Frame(self, padding=(0, 0, 0, 8))
        filter_bar.pack(fill="x")

        ttk.Label(filter_bar, text=" Lọc thời gian:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))

        self.cbo_time_filter = ttk.Combobox(filter_bar, width=18, state="readonly", values=[
            "Tất cả thời gian", "Hôm nay", "Hôm qua", "Tháng này", "Tháng trước",
            "Quý 1 (Tháng 1-3)", "Quý 2 (Tháng 4-6)", "Quý 3 (Tháng 7-9)", "Quý 4 (Tháng 10-12)", "Theo Năm"
        ])
        self.cbo_time_filter.current(0)
        self.cbo_time_filter.pack(side="left", padx=(0, 10))
        self.cbo_time_filter.bind("<<ComboboxSelected>>", lambda e: self.load_orders_table())

        ttk.Label(filter_bar, text="Năm:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
        current_year = datetime.now().year
        self.cbo_year_filter = ttk.Combobox(filter_bar, width=8, state="readonly", values=[str(y) for y in range(current_year, current_year - 5, -1)])
        self.cbo_year_filter.current(0)
        self.cbo_year_filter.pack(side="left", padx=(0, 10))
        self.cbo_year_filter.bind("<<ComboboxSelected>>", lambda e: self.load_orders_table())

        tk.Button(filter_bar, text=" Xóa Đơn", bg=config.COLOR_DANGER, fg="white", font=("Segoe UI", 9, "bold"), padx=8, command=self.delete_selected_order).pack(side="right", padx=(5, 0))
        tk.Button(filter_bar, text=" Tải Lại", bg=config.COLOR_SECONDARY, fg="white", font=("Segoe UI", 9), padx=8, command=self.load_orders_table).pack(side="right")

        # Thống kê
        self.lbl_filter_stats = ttk.Label(
            self,
            text=" Thống kê: 0 đơn | Tổng xuất: 0.0 m³ | Tổng tiền: 0đ | Nợ: 0đ",
            font=("Segoe UI", 9, "bold"),
            foreground=config.COLOR_PRIMARY
        )
        self.lbl_filter_stats.pack(anchor="w", pady=(0, 6))

        # Bảng
        columns = ("code", "time", "customer", "product", "volume", "total", "debt", "driver")
        self.tree_orders = ttk.Treeview(self, columns=columns, show="headings", height=15)

        self.tree_orders.heading("code", text="Mã Đơn")
        self.tree_orders.heading("time", text="Thời Gian")
        self.tree_orders.heading("customer", text="Khách Hàng")
        self.tree_orders.heading("product", text="Vật Liệu")
        self.tree_orders.heading("volume", text="Khối Lượng")
        self.tree_orders.heading("total", text="Tổng Tiền")
        self.tree_orders.heading("debt", text="Còn Nợ")
        self.tree_orders.heading("driver", text="Xe/Tài Xế")

        self.tree_orders.column("code", width=120)
        self.tree_orders.column("time", width=130)
        self.tree_orders.column("customer", width=160)
        self.tree_orders.column("product", width=140)
        self.tree_orders.column("volume", width=90)
        self.tree_orders.column("total", width=110)
        self.tree_orders.column("debt", width=100)
        self.tree_orders.column("driver", width=130)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree_orders.yview)
        self.tree_orders.configure(yscrollcommand=scrollbar.set)

        self.tree_orders.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def get_date_bounds(self, filter_option, selected_year):
        if filter_option == "Tất cả thời gian": return None, None
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        try:
            target_year = int(selected_year)
        except Exception:
            target_year = now.year

        if filter_option == "Hôm nay": return today_str, today_str
        elif filter_option == "Hôm qua": return yesterday_str, yesterday_str
        elif filter_option == "Tháng này":
            start = f"{now.year}-{now.month:02d}-01"
            next_month = now.replace(day=28) + timedelta(days=4)
            end_day = next_month - timedelta(days=next_month.day)
            return start, end_day.strftime("%Y-%m-%d")
        elif filter_option == "Tháng trước":
            prev_month = 12 if now.month == 1 else now.month - 1
            prev_year = now.year - 1 if now.month == 1 else now.year
            start = f"{prev_year}-{prev_month:02d}-01"
            dt = datetime(prev_year, prev_month, 28) + timedelta(days=4)
            end_day = dt - timedelta(days=dt.day)
            return start, end_day.strftime("%Y-%m-%d")
        elif filter_option.startswith("Quý 1"): return f"{target_year}-01-01", f"{target_year}-03-31"
        elif filter_option.startswith("Quý 2"): return f"{target_year}-04-01", f"{target_year}-06-30"
        elif filter_option.startswith("Quý 3"): return f"{target_year}-07-01", f"{target_year}-09-30"
        elif filter_option.startswith("Quý 4"): return f"{target_year}-10-01", f"{target_year}-12-31"
        elif filter_option == "Theo Năm": return f"{target_year}-01-01", f"{target_year}-12-31"
        return None, None

    def load_orders_table(self, search_query=""):
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)

        time_filter = self.cbo_time_filter.get()
        selected_year = self.cbo_year_filter.get()
        start_date, end_date = self.get_date_bounds(time_filter, selected_year)

        orders = order_dao.get_orders_list(search_query=search_query, start_date=start_date, end_date=end_date)
        
        filtered_count = 0
        sum_volume = 0.0
        sum_amount = 0.0
        sum_debt = 0.0

        for o in orders:
            filtered_count += 1
            sum_volume += float(o['total_volume'] or 0)
            sum_amount += float(o['total_amount'] or 0)
            sum_debt += float(o['debt_amount'] or 0)
            self.tree_orders.insert("", "end", values=(
                o['code'], o['created_at'], o['customer_name'] or "Khách lẻ", o['product_name'] or "Vật liệu",
                f"{o['total_volume']:,.1f} m³", f"{o['total_amount']:,.0f}đ", f"{o['debt_amount']:,.0f}đ", f"{o['plate_number']} ({o['driver_name']})"
            ))

        self.lbl_filter_stats.config(
            text=f" Kết quả lọc [{time_filter}]: {filtered_count} đơn | Tổng m³: {sum_volume:,.1f} m³ | Tổng tiền: {sum_amount:,.0f}đ | Nợ: {sum_debt:,.0f}đ"
        )

    def delete_selected_order(self):
        selected_item = self.tree_orders.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần xóa từ danh sách bên dưới!")
            return

        item_values = self.tree_orders.item(selected_item[0])['values']
        order_code = item_values[0]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA đơn hàng {order_code}?\n\n(Lưu ý: Hệ thống sẽ tự động HOÀN TỒN KHO và TRỪ NỢ cho khách)"):
            if order_dao.delete_order(order_code):
                messagebox.showinfo("Thành công", f"Đã xóa thành công đơn hàng {order_code}!")
                self.load_orders_table()
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy đơn hàng {order_code}!")
