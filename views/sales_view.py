"""
Sales & Volume Calculation View for VLXD Thống Nhất
Formula: Số khối/chuyến x Số chuyến = Tổng khối lượng (m³)
Includes Quick Search Input, Quick Create Buttons, and Advanced Date/Quarter/Year Filtering.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database
from utils import num2vietnamese_words

class SalesView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback

        self.products = []
        self.customers = []
        self.vehicles = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Title Banner
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="🛒 TẠO ĐƠN HÀNG & TÍNH KHỐI LƯỢNG VẬT LIỆU", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")
        ttk.Label(title_frame, text="*Công thức: Số khối x Số chuyến = Tổng m³*", font=("Segoe UI", 10, "italic"), foreground="#475569").pack(side="right")

        # 2. Main Layout (Left: Form Entry, Right: Live Summary & History)
        content_box = ttk.Frame(self)
        content_box.pack(fill="both", expand=True)

        # LEFT FORM
        form_frame = ttk.LabelFrame(content_box, text=" Thông Tin Đơn Xuất Hàng ", padding=12)
        form_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))

        # Row 0: SEARCH BAR (Ô TÌM KIẾM NHANH THÔNG TIN)
        search_box = ttk.LabelFrame(form_frame, text=" 🔍 Tìm Kiếm Nhanh (Khách/SĐT/Vật liệu) ", padding=5)
        search_box.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.ent_search = ttk.Entry(search_box, width=32)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_search.bind("<KeyRelease>", self.on_search_key_release)
        ttk.Label(search_box, text="*Gõ để tìm*", font=("Segoe UI", 8, "italic"), foreground="#64748b").pack(side="right")

        # Row 1: Khách hàng / Nhà thầu + Nút Tạo Mới
        ttk.Label(form_frame, text="Khách hàng / Nhà thầu:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        cust_row = ttk.Frame(form_frame)
        cust_row.grid(row=1, column=1, pady=4, sticky="ew")

        self.cbo_customer = ttk.Combobox(cust_row, width=22)
        self.cbo_customer.pack(side="left", fill="x", expand=True)

        tk.Button(
            cust_row, text="➕ Tạo Khách", bg="#2563eb", fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_customer_dialog
        ).pack(side="right", padx=(4, 0))

        # Row 2: Chọn Vật Liệu + Nút Thêm Vật Liệu Mới
        ttk.Label(form_frame, text="Loại Vật liệu (Cát/Đá):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        prod_row = ttk.Frame(form_frame)
        prod_row.grid(row=2, column=1, pady=4, sticky="ew")

        self.cbo_product = ttk.Combobox(prod_row, width=22)
        self.cbo_product.pack(side="left", fill="x", expand=True)
        self.cbo_product.bind("<<ComboboxSelected>>", self.on_product_change)

        tk.Button(
            prod_row, text="➕ Thêm VL", bg="#059669", fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_product_dialog
        ).pack(side="right", padx=(4, 0))

        # Row 3: Chọn Xe giao hàng + Nút Thêm Xe Mới
        ttk.Label(form_frame, text="Xe & Tài xế giao:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        veh_row = ttk.Frame(form_frame)
        veh_row.grid(row=3, column=1, pady=4, sticky="ew")

        self.cbo_vehicle = ttk.Combobox(veh_row, width=22)
        self.cbo_vehicle.pack(side="left", fill="x", expand=True)
        self.cbo_vehicle.bind("<<ComboboxSelected>>", self.on_vehicle_change)

        tk.Button(
            veh_row, text="➕ Thêm Xe", bg="#d97706", fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_vehicle_dialog
        ).pack(side="right", padx=(4, 0))

        ttk.Separator(form_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

        # Row 5: CÔNG THỨC KHỐI LƯỢNG
        calc_box = ttk.LabelFrame(form_frame, text=" 🧮 Phép Tính Khối Lượng Đặc Thù ", padding=8)
        calc_box.grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Label(calc_box, text="Số khối/chuyến (m³):").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_vol_per_trip = ttk.Entry(calc_box, width=12)
        self.ent_vol_per_trip.insert(0, "2.2")
        self.ent_vol_per_trip.grid(row=0, column=1, pady=3, sticky="w")
        self.ent_vol_per_trip.bind("<KeyRelease>", self.calculate_totals)

        ttk.Label(calc_box, text="x   Số chuyến xe:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_trips = ttk.Entry(calc_box, width=12)
        self.ent_trips.insert(0, "1")
        self.ent_trips.grid(row=1, column=1, pady=3, sticky="w")
        self.ent_trips.bind("<KeyRelease>", self.calculate_totals)

        ttk.Label(calc_box, text="=   TỔNG KHỐI LƯỢNG:", font=("Segoe UI", 10, "bold"), foreground="#047857").grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_total_volume = ttk.Label(calc_box, text="2.2 m³", font=("Segoe UI", 11, "bold"), foreground="#047857")
        self.lbl_total_volume.grid(row=2, column=1, sticky="w", pady=4)

        # Row 6: Đơn giá bán & Đọc chữ
        ttk.Label(form_frame, text="Đơn giá bán (đ/m³):").grid(row=6, column=0, sticky="w", pady=2)
        self.ent_price = ttk.Entry(form_frame, width=32)
        self.ent_price.grid(row=6, column=1, pady=2, sticky="ew")
        self.ent_price.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_price_words = ttk.Label(form_frame, text="✍️ Bằng chữ: Không đồng", font=("Segoe UI", 8, "italic", "bold"), foreground="#0369a1")
        self.lbl_price_words.grid(row=7, column=1, sticky="w", pady=(0, 4))

        # Row 8: Cước vận chuyển & Đọc chữ
        ttk.Label(form_frame, text="Cước vận chuyển (đ):").grid(row=8, column=0, sticky="w", pady=2)
        self.ent_shipping = ttk.Entry(form_frame, width=32)
        self.ent_shipping.insert(0, "100000")
        self.ent_shipping.grid(row=8, column=1, pady=2, sticky="ew")
        self.ent_shipping.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_shipping_words = ttk.Label(form_frame, text="✍️ Bằng chữ: Một trăm ngàn đồng", font=("Segoe UI", 8, "italic", "bold"), foreground="#0369a1")
        self.lbl_shipping_words.grid(row=9, column=1, sticky="w", pady=(0, 4))

        # Row 10: Thanh toán & Đọc chữ
        ttk.Label(form_frame, text="Tiền trả ngay (đ):").grid(row=10, column=0, sticky="w", pady=2)
        self.ent_paid = ttk.Entry(form_frame, width=32)
        self.ent_paid.insert(0, "0")
        self.ent_paid.grid(row=10, column=1, pady=2, sticky="ew")
        self.ent_paid.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_paid_words = ttk.Label(form_frame, text="✍️ Bằng chữ: Không đồng", font=("Segoe UI", 8, "italic", "bold"), foreground="#0369a1")
        self.lbl_paid_words.grid(row=11, column=1, sticky="w", pady=(0, 4))

        # Row 12: Ghi chú
        ttk.Label(form_frame, text="Ghi chú đơn hàng:").grid(row=12, column=0, sticky="w", pady=4)
        self.ent_note = ttk.Entry(form_frame, width=32)
        self.ent_note.grid(row=12, column=1, pady=4, sticky="ew")

        # Summary box inside form
        summary_frame = ttk.Frame(form_frame, padding=8)
        summary_frame.grid(row=13, column=0, columnspan=2, sticky="ew", pady=6)

        self.lbl_summary_amount = ttk.Label(summary_frame, text="TỔNG TIỀN: 0 VNĐ", font=("Segoe UI", 12, "bold"), foreground="#b91c1c")
        self.lbl_summary_amount.pack(anchor="w")

        self.lbl_summary_words = ttk.Label(summary_frame, text="✍️ Tổng tiền bằng chữ: Không đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#0369a1")
        self.lbl_summary_words.pack(anchor="w")

        self.lbl_summary_debt = ttk.Label(summary_frame, text="GHI NỢ KHÁCH: 0 VNĐ", font=("Segoe UI", 10, "bold"), foreground="#c2410c")
        self.lbl_summary_debt.pack(anchor="w")

        self.lbl_debt_words = ttk.Label(summary_frame, text="✍️ Tiền nợ bằng chữ: Không đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#b45309")
        self.lbl_debt_words.pack(anchor="w")

        # Button Submit
        btn_submit = tk.Button(form_frame, text="✅ XUẤT ĐƠN HÀNG & TÍNH NỢ", bg="#16a34a", fg="white", font=("Segoe UI", 11, "bold"), pady=8, command=self.submit_order)
        btn_submit.grid(row=14, column=0, columnspan=2, sticky="ew", pady=5)

        # RIGHT: RECENT ORDERS TABLE & FILTER TOOLBAR
        right_frame = ttk.LabelFrame(content_box, text=" Lịch Sử Đơn Xuất Kho Gần Đây ", padding=10)
        right_frame.pack(side="right", fill="both", expand=True)

        # 📅 FILTER TOOLBAR (BỘ LỌC NGÀY / THÁNG / NĂM / QUÝ)
        filter_bar = ttk.Frame(right_frame, padding=(0, 0, 0, 8))
        filter_bar.pack(fill="x")

        ttk.Label(filter_bar, text="📅 Lọc thời gian:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))

        self.cbo_time_filter = ttk.Combobox(filter_bar, width=18, state="readonly", values=[
            "Tất cả thời gian",
            "Hôm nay",
            "Hôm qua",
            "Tháng này",
            "Tháng trước",
            "Quý 1 (Tháng 1-3)",
            "Quý 2 (Tháng 4-6)",
            "Quý 3 (Tháng 7-9)",
            "Quý 4 (Tháng 10-12)",
            "Theo Năm"
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

        tk.Button(filter_bar, text="❌ Xóa Đơn", bg="#dc2626", fg="white", font=("Segoe UI", 9, "bold"), padx=8, command=self.delete_selected_order).pack(side="right", padx=(5, 0))
        tk.Button(filter_bar, text="🔄 Tải Lại", bg="#64748b", fg="white", font=("Segoe UI", 9), padx=8, command=self.load_orders_table).pack(side="right")

        # Live Filter Statistics Banner
        self.lbl_filter_stats = ttk.Label(
            right_frame,
            text="📊 Thống kê: 0 đơn | Tổng xuất: 0.0 m³ | Tổng tiền: 0đ | Nợ: 0đ",
            font=("Segoe UI", 9, "bold"),
            foreground="#1e3a8a"
        )
        self.lbl_filter_stats.pack(anchor="w", pady=(0, 6))

        columns = ("code", "time", "customer", "product", "volume", "total", "debt", "driver")
        self.tree_orders = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)

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

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree_orders.yview)
        self.tree_orders.configure(yscrollcommand=scrollbar.set)

        self.tree_orders.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        self.products = database.get_all_products()
        self.customers = database.get_all_customers()
        self.vehicles = database.get_all_vehicles()

        # Populate combos
        self.cbo_customer["values"] = [f"{c['name']} (Nợ: {c['debt']:,.0f}đ)" for c in self.customers]
        if self.customers and not self.cbo_customer.get():
            self.cbo_customer.current(0)

        self.cbo_product["values"] = [f"{p['name']} ({p['price']:,.0f}đ/{p['unit']})" for p in self.products]
        if self.products and not self.cbo_product.get():
            self.cbo_product.current(0)
            self.on_product_change(None)

        self.cbo_vehicle["values"] = [f"{v['plate_number']} - {v['driver_name']} ({v['capacity_m3']}m³)" for v in self.vehicles]
        if self.vehicles and not self.cbo_vehicle.get():
            self.cbo_vehicle.current(0)
            self.on_vehicle_change(None)

        self.load_orders_table()

    def on_search_key_release(self, event=None):
        query = self.ent_search.get().strip().lower()

        matching_custs = [
            f"{c['name']} (Nợ: {c['debt']:,.0f}đ)"
            for c in self.customers
            if query in c['name'].lower() or query in (c['phone'] or "").lower() or query in (c['address'] or "").lower()
        ]
        if matching_custs:
            self.cbo_customer["values"] = matching_custs
            if len(query) >= 2:
                self.cbo_customer.set(matching_custs[0])
        else:
            self.cbo_customer["values"] = [f"{c['name']} (Nợ: {c['debt']:,.0f}đ)" for c in self.customers]

        self.load_orders_table()

    def on_product_change(self, event):
        idx = self.cbo_product.current()
        if idx >= 0 and idx < len(self.products):
            p = self.products[idx]
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, str(int(p['price'])))
            self.calculate_totals()

    def on_vehicle_change(self, event):
        idx = self.cbo_vehicle.current()
        if idx >= 0 and idx < len(self.vehicles):
            v = self.vehicles[idx]
            self.ent_vol_per_trip.delete(0, tk.END)
            self.ent_vol_per_trip.insert(0, str(v['capacity_m3']))
            self.calculate_totals()

    def calculate_totals(self, event=None):
        try:
            vol_trip = float(self.ent_vol_per_trip.get() or 0)
            trips = int(self.ent_trips.get() or 0)
            total_vol = vol_trip * trips
            self.lbl_total_volume.config(text=f"{total_vol:,.1f} m³")

            price = float(self.ent_price.get() or 0)
            shipping = float(self.ent_shipping.get() or 0)
            paid = float(self.ent_paid.get() or 0)

            # Update per-field Bằng Chữ Labels
            self.lbl_price_words.config(text=f"✍️ Bằng chữ: {num2vietnamese_words(price)}")
            self.lbl_shipping_words.config(text=f"✍️ Bằng chữ: {num2vietnamese_words(shipping)}")
            self.lbl_paid_words.config(text=f"✍️ Bằng chữ: {num2vietnamese_words(paid)}")

            product_amt = total_vol * price
            total_amt = product_amt + shipping
            debt_amt = max(0, total_amt - paid)

            self.lbl_summary_amount.config(text=f"TỔNG TIỀN: {total_amt:,.0f} VNĐ")
            self.lbl_summary_words.config(text=f"✍️ Tổng tiền bằng chữ: {num2vietnamese_words(total_amt)}")
            
            self.lbl_summary_debt.config(text=f"GHI NỢ KHÁCH: {debt_amt:,.0f} VNĐ")
            self.lbl_debt_words.config(text=f"✍️ Tiền nợ bằng chữ: {num2vietnamese_words(debt_amt)}")
        except ValueError:
            pass

    def open_quick_customer_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Khách Hàng Nhanh")
        dlg.geometry("380x300")
        dlg.grab_set()

        ttk.Label(dlg, text="TẠO NHANH HỒ SƠ KHÁCH HÀNG", font=("Segoe UI", 11, "bold"), foreground="#1e3a8a").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Họ tên Khách / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=3)
        ent_name = ttk.Entry(form, width=24)
        ent_name.grid(row=0, column=1, pady=3)
        if self.ent_search.get():
            ent_name.insert(0, self.ent_search.get().strip())

        ttk.Label(form, text="Số điện thoại:").grid(row=1, column=0, sticky="w", pady=3)
        ent_phone = ttk.Entry(form, width=24)
        ent_phone.grid(row=1, column=1, pady=3)

        ttk.Label(form, text="Địa chỉ công trình:").grid(row=2, column=0, sticky="w", pady=3)
        ent_addr = ttk.Entry(form, width=24)
        ent_addr.grid(row=2, column=1, pady=3)

        ttk.Label(form, text="Hạn mức cho nợ (đ):").grid(row=3, column=0, sticky="w", pady=3)
        ent_limit = ttk.Entry(form, width=24)
        ent_limit.insert(0, "50000000")
        ent_limit.grid(row=3, column=1, pady=3)

        ttk.Label(form, text="Bằng chữ:").grid(row=4, column=0, sticky="w", pady=3)
        lbl_limit_words = ttk.Label(form, text="Năm mươi triệu đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#2563eb")
        lbl_limit_words.grid(row=4, column=1, sticky="w", pady=3)

        def on_limit_change(event=None):
            val = ent_limit.get().strip()
            words = num2vietnamese_words(val)
            lbl_limit_words.config(text=words)

        ent_limit.bind("<KeyRelease>", on_limit_change)

        def save_quick_customer():
            name = ent_name.get().strip()
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên khách hàng!")
                return
            try:
                database.add_customer(name, ent_phone.get().strip(), ent_addr.get().strip(), float(ent_limit.get() or 50000000), 1)
                messagebox.showinfo("Thành công", f"Đã tạo khách hàng: {name}")
                dlg.destroy()
                self.load_data()
                for i, c in enumerate(self.customers):
                    if c['name'] == name:
                        self.cbo_customer.current(i)
                        break
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo khách hàng: {str(e)}")

        tk.Button(dlg, text="💾 LƯU KHÁCH HÀNG", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_customer).pack(pady=10)

    def open_quick_product_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Vật Liệu Nhanh")
        dlg.geometry("380x320")
        dlg.grab_set()

        ttk.Label(dlg, text="TẠO NHANH VẬT LIỆU MỚI", font=("Segoe UI", 11, "bold"), foreground="#059669").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("Mã SP (vd: CAT_MO):", "ent_code"),
            ("Tên vật liệu:", "ent_name"),
            ("Đơn vị tính (m³, bao, viên):", "ent_unit"),
            ("Đơn giá bán (đ):", "ent_price"),
            ("Số lượng tồn ban đầu:", "ent_stock"),
        ]

        entries = {}
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=22)
            ent.grid(row=i, column=1, pady=3, sticky="ew")
            entries[var_name] = ent

        entries["ent_unit"].insert(0, "m³")

        def save_quick_product():
            name = entries["ent_name"].get().strip()
            code = entries["ent_code"].get().strip().upper() or f"VL_{name[:3].upper()}"
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên vật liệu!")
                return
            try:
                database.add_product(
                    code, name, entries["ent_unit"].get(),
                    float(entries["ent_price"].get() or 0),
                    float(entries["ent_stock"].get() or 100),
                    20.0, "Tạo nhanh từ màn hình bán hàng"
                )
                messagebox.showinfo("Thành công", f"Đã tạo vật liệu mới: {name}")
                dlg.destroy()
                self.load_data()
                for i, p in enumerate(self.products):
                    if p['name'] == name:
                        self.cbo_product.current(i)
                        self.on_product_change(None)
                        break
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo vật liệu: {str(e)}")

        tk.Button(dlg, text="💾 LƯU VẬT LIỆU", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_product).pack(pady=10)

    def open_quick_vehicle_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Xe Nhanh")
        dlg.geometry("380x300")
        dlg.grab_set()

        ttk.Label(dlg, text="TẠO NHANH THÔNG TIN XE", font=("Segoe UI", 11, "bold"), foreground="#d97706").pack(pady=10)

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
        ent_cap.insert(0, "2.2")
        ent_cap.grid(row=2, column=1, pady=3)

        def save_quick_vehicle():
            plate = ent_plate.get().strip().upper()
            driver = ent_driver.get().strip()
            if not plate or not driver:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập biển số xe và tên tài xế!")
                return
            try:
                database.add_vehicle(plate, driver, "", float(ent_cap.get() or 2.2), 50000, 30000)
                messagebox.showinfo("Thành công", f"Đã đăng ký xe: {plate}")
                dlg.destroy()
                self.load_data()
                for i, v in enumerate(self.vehicles):
                    if v['plate_number'] == plate:
                        self.cbo_vehicle.current(i)
                        self.on_vehicle_change(None)
                        break
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm xe: {str(e)}")

        tk.Button(dlg, text="💾 LƯU THÔNG TIN XE", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), pady=4, command=save_quick_vehicle).pack(pady=10)

    def delete_selected_order(self):
        selected_item = self.tree_orders.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đơn hàng cần xóa từ danh sách bên dưới!")
            return

        item_values = self.tree_orders.item(selected_item[0])['values']
        order_code = item_values[0]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA đơn hàng {order_code}?\n\n(Lưu ý: Hệ thống sẽ tự động HOÀN TỒN KHO và TRỪ NỢ cho khách)"):
            if database.delete_order(order_code):
                messagebox.showinfo("Thành công", f"Đã xóa thành công đơn hàng {order_code}!")
                self.load_data()
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy đơn hàng {order_code}!")

    def submit_order(self):
        try:
            cust_text = self.cbo_customer.get().strip()
            prod_idx = self.cbo_product.current()
            veh_idx = self.cbo_vehicle.current()

            if not cust_text:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập hoặc chọn Khách hàng!")
                return

            if prod_idx < 0:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn Loại vật liệu!")
                return

            if veh_idx < 0:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn Xe & Tài xế giao!")
                return

            cust_idx = self.cbo_customer.current()
            if cust_idx >= 0:
                cust_id = self.customers[cust_idx]['id']
                cust_name = self.customers[cust_idx]['name']
            else:
                existing_cust = [c for c in self.customers if c['name'].lower() == cust_text.lower()]
                if existing_cust:
                    cust_id = existing_cust[0]['id']
                    cust_name = existing_cust[0]['name']
                else:
                    database.add_customer(cust_text, "", "Tự động tạo từ ô nhập đơn", 50000000, 0)
                    all_c = database.get_all_customers()
                    new_c = [c for c in all_c if c['name'] == cust_text]
                    cust_id = new_c[0]['id'] if new_c else all_c[0]['id']
                    cust_name = cust_text

            prod = self.products[prod_idx]
            veh = self.vehicles[veh_idx]

            vol_trip = float(self.ent_vol_per_trip.get())
            trips = int(self.ent_trips.get())

            if vol_trip <= 0 or trips <= 0:
                messagebox.showwarning("Cảnh báo", "Số khối và Số chuyến phải lớn hơn 0!")
                return

            price = float(self.ent_price.get())
            shipping = float(self.ent_shipping.get())
            paid = float(self.ent_paid.get())
            note = self.ent_note.get()

            code, total_vol, total_amt, debt = database.create_order_transaction(
                cust_id, veh['id'], prod['id'], vol_trip, trips, price, shipping, paid, note
            )

            messagebox.showinfo("Thành Công", f"Đã tạo đơn hàng thành công!\nMã đơn: {code}\nKhách hàng: {cust_name}\nTổng xuất: {total_vol:,.1f} m³ {prod['name']}\nTổng tiền: {total_amt:,.0f}đ\nGhi nợ: {debt:,.0f}đ")

            self.load_data()
            if self.refresh_callback:
                self.refresh_callback()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo đơn hàng: {str(e)}")

    def matches_date_filter(self, created_at_str, filter_option, selected_year):
        if not created_at_str or filter_option == "Tất cả thời gian":
            return True

        try:
            dt = datetime.strptime(created_at_str[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return True

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        try:
            target_year = int(selected_year)
        except Exception:
            target_year = dt.year

        if filter_option == "Hôm nay":
            return dt.strftime("%Y-%m-%d") == today_str
        elif filter_option == "Hôm qua":
            return dt.strftime("%Y-%m-%d") == yesterday_str
        elif filter_option == "Tháng này":
            return dt.year == now.year and dt.month == now.month
        elif filter_option == "Tháng trước":
            prev_month = 12 if now.month == 1 else now.month - 1
            prev_year = now.year - 1 if now.month == 1 else now.year
            return dt.year == prev_year and dt.month == prev_month
        elif filter_option.startswith("Quý 1"):
            return dt.year == target_year and dt.month in [1, 2, 3]
        elif filter_option.startswith("Quý 2"):
            return dt.year == target_year and dt.month in [4, 5, 6]
        elif filter_option.startswith("Quý 3"):
            return dt.year == target_year and dt.month in [7, 8, 9]
        elif filter_option.startswith("Quý 4"):
            return dt.year == target_year and dt.month in [10, 11, 12]
        elif filter_option == "Theo Năm":
            return dt.year == target_year
        return True

    def load_orders_table(self):
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)

        search_query = self.ent_search.get().strip().lower()
        time_filter = self.cbo_time_filter.get()
        selected_year = self.cbo_year_filter.get()

        orders = database.get_orders_list()
        
        filtered_count = 0
        sum_volume = 0.0
        sum_amount = 0.0
        sum_debt = 0.0

        for o in orders:
            # 1. Apply Search Filter
            if search_query:
                match_cust = search_query in (o['customer_name'] or "").lower()
                match_prod = search_query in (o['product_name'] or "").lower()
                match_code = search_query in (o['code'] or "").lower()
                match_driver = search_query in (o['driver_name'] or "").lower()
                if not (match_cust or match_prod or match_code or match_driver):
                    continue

            # 2. Apply Date / Quarter / Year Filter
            if not self.matches_date_filter(o['created_at'], time_filter, selected_year):
                continue

            filtered_count += 1
            sum_volume += float(o['total_volume'] or 0)
            sum_amount += float(o['total_amount'] or 0)
            sum_debt += float(o['debt_amount'] or 0)

            self.tree_orders.insert("", "end", values=(
                o['code'],
                o['created_at'],
                o['customer_name'] or "Khách lẻ",
                o['product_name'] or "Vật liệu",
                f"{o['total_volume']:,.1f} m³",
                f"{o['total_amount']:,.0f}đ",
                f"{o['debt_amount']:,.0f}đ",
                f"{o['plate_number']} ({o['driver_name']})"
            ))

        # Update Filter Statistics Header
        self.lbl_filter_stats.config(
            text=f"📊 Kết quả lọc [{time_filter}]: {filtered_count} đơn | Tổng m³: {sum_volume:,.1f} m³ | Tổng tiền: {sum_amount:,.0f}đ | Nợ: {sum_debt:,.0f}đ"
        )
