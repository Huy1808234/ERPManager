import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import customer_dao, product_dao, vehicle_dao, order_dao
from utils import num2vietnamese_words

class SalesForm(ttk.LabelFrame):
    def __init__(self, parent, on_order_created=None):
        super().__init__(parent, text=" Thông Tin Đơn Xuất Hàng ", padding=12)
        self.on_order_created = on_order_created
        self.products = []
        self.customers = []
        self.vehicles = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # SEARCH BAR
        search_box = ttk.LabelFrame(self, text=" 🔍 Tìm Kiếm Nhanh (Khách/SĐT/Vật liệu) ", padding=5)
        search_box.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.ent_search = ttk.Entry(search_box, width=32)
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_search.bind("<KeyRelease>", self.on_search_key_release)
        ttk.Label(search_box, text="*Gõ để tìm*", font=("Segoe UI", 8, "italic"), foreground="#64748b").pack(side="right")

        # Khách hàng
        ttk.Label(self, text="Khách hàng / Nhà thầu:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        cust_row = ttk.Frame(self)
        cust_row.grid(row=1, column=1, pady=4, sticky="ew")

        self.cbo_customer = ttk.Combobox(cust_row, width=22)
        self.cbo_customer.pack(side="left", fill="x", expand=True)

        tk.Button(
            cust_row, text="➕ Tạo Khách", bg=config.COLOR_PRIMARY, fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_customer_dialog
        ).pack(side="right", padx=(4, 0))

        # Vật Liệu
        ttk.Label(self, text="Loại Vật liệu (Cát/Đá):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        prod_row = ttk.Frame(self)
        prod_row.grid(row=2, column=1, pady=4, sticky="ew")

        self.cbo_product = ttk.Combobox(prod_row, width=22)
        self.cbo_product.pack(side="left", fill="x", expand=True)
        self.cbo_product.bind("<<ComboboxSelected>>", self.on_product_change)

        tk.Button(
            prod_row, text="➕ Thêm VL", bg=config.COLOR_SUCCESS_DARK, fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_product_dialog
        ).pack(side="right", padx=(4, 0))

        # Xe & Tài xế
        ttk.Label(self, text="Xe & Tài xế giao:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        veh_row = ttk.Frame(self)
        veh_row.grid(row=3, column=1, pady=4, sticky="ew")

        self.cbo_vehicle = ttk.Combobox(veh_row, width=22)
        self.cbo_vehicle.pack(side="left", fill="x", expand=True)
        self.cbo_vehicle.bind("<<ComboboxSelected>>", self.on_vehicle_change)

        tk.Button(
            veh_row, text="➕ Thêm Xe", bg=config.COLOR_WARNING, fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, command=self.open_quick_vehicle_dialog
        ).pack(side="right", padx=(4, 0))

        ttk.Separator(self, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

        # CÔNG THỨC
        calc_box = ttk.LabelFrame(self, text="  Phép Tính Khối Lượng Đặc Thù ", padding=8)
        calc_box.grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Label(calc_box, text="Số khối/chuyến (m³):").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_vol_per_trip = ttk.Entry(calc_box, width=12)
        self.ent_vol_per_trip.insert(0, str(config.DEFAULT_VEHICLE_CAPACITY))
        self.ent_vol_per_trip.grid(row=0, column=1, pady=3, sticky="w")
        self.ent_vol_per_trip.bind("<KeyRelease>", self.calculate_totals)

        ttk.Label(calc_box, text="x   Số chuyến xe:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_trips = ttk.Entry(calc_box, width=12)
        self.ent_trips.insert(0, "1")
        self.ent_trips.grid(row=1, column=1, pady=3, sticky="w")
        self.ent_trips.bind("<KeyRelease>", self.calculate_totals)

        ttk.Label(calc_box, text="=   TỔNG KHỐI LƯỢNG:", font=("Segoe UI", 10, "bold"), foreground=config.COLOR_SUCCESS_DARK).grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_total_volume = ttk.Label(calc_box, text="2.2 m³", font=("Segoe UI", 11, "bold"), foreground=config.COLOR_SUCCESS_DARK)
        self.lbl_total_volume.grid(row=2, column=1, sticky="w", pady=4)

        # Đơn giá
        ttk.Label(self, text="Đơn giá bán (đ/m³):").grid(row=6, column=0, sticky="w", pady=2)
        self.ent_price = ttk.Entry(self, width=32)
        self.ent_price.grid(row=6, column=1, pady=2, sticky="ew")
        self.ent_price.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_price_words = ttk.Label(self, text=" Bằng chữ: Không đồng", font=("Segoe UI", 8, "italic", "bold"), foreground=config.COLOR_PRIMARY_LIGHT)
        self.lbl_price_words.grid(row=7, column=1, sticky="w", pady=(0, 4))

        # Cước VC
        ttk.Label(self, text="Cước vận chuyển (đ):").grid(row=8, column=0, sticky="w", pady=2)
        self.ent_shipping = ttk.Entry(self, width=32)
        self.ent_shipping.insert(0, "100000")
        self.ent_shipping.grid(row=8, column=1, pady=2, sticky="ew")
        self.ent_shipping.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_shipping_words = ttk.Label(self, text=" Bằng chữ: Một trăm ngàn đồng", font=("Segoe UI", 8, "italic", "bold"), foreground=config.COLOR_PRIMARY_LIGHT)
        self.lbl_shipping_words.grid(row=9, column=1, sticky="w", pady=(0, 4))

        # Tiền trả
        ttk.Label(self, text="Tiền trả ngay (đ):").grid(row=10, column=0, sticky="w", pady=2)
        self.ent_paid = ttk.Entry(self, width=32)
        self.ent_paid.insert(0, "0")
        self.ent_paid.grid(row=10, column=1, pady=2, sticky="ew")
        self.ent_paid.bind("<KeyRelease>", self.calculate_totals)

        self.lbl_paid_words = ttk.Label(self, text=" Bằng chữ: Không đồng", font=("Segoe UI", 8, "italic", "bold"), foreground=config.COLOR_PRIMARY_LIGHT)
        self.lbl_paid_words.grid(row=11, column=1, sticky="w", pady=(0, 4))

        # Ghi chú
        ttk.Label(self, text="Ghi chú đơn hàng:").grid(row=12, column=0, sticky="w", pady=4)
        self.ent_note = ttk.Entry(self, width=32)
        self.ent_note.grid(row=12, column=1, pady=4, sticky="ew")

        # Summary box
        summary_frame = ttk.Frame(self, padding=8)
        summary_frame.grid(row=13, column=0, columnspan=2, sticky="ew", pady=6)

        self.lbl_summary_amount = ttk.Label(summary_frame, text="TỔNG TIỀN: 0 VNĐ", font=("Segoe UI", 12, "bold"), foreground=config.COLOR_DANGER)
        self.lbl_summary_amount.pack(anchor="w")
        self.lbl_summary_words = ttk.Label(summary_frame, text=" Tổng tiền bằng chữ: Không đồng", font=("Segoe UI", 9, "italic", "bold"), foreground=config.COLOR_PRIMARY_LIGHT)
        self.lbl_summary_words.pack(anchor="w")

        self.lbl_summary_debt = ttk.Label(summary_frame, text="GHI NỢ KHÁCH: 0 VNĐ", font=("Segoe UI", 10, "bold"), foreground=config.COLOR_WARNING)
        self.lbl_summary_debt.pack(anchor="w")
        self.lbl_debt_words = ttk.Label(summary_frame, text=" Tiền nợ bằng chữ: Không đồng", font=("Segoe UI", 9, "italic", "bold"), foreground=config.COLOR_WARNING_DARK)
        self.lbl_debt_words.pack(anchor="w")

        # Nút submit
        btn_submit = tk.Button(self, text=" XUẤT ĐƠN HÀNG & TÍNH NỢ", bg=config.COLOR_SUCCESS, fg="white", font=("Segoe UI", 11, "bold"), pady=8, command=self.submit_order)
        btn_submit.grid(row=14, column=0, columnspan=2, sticky="ew", pady=5)

    def load_data(self):
        self.products = product_dao.get_all_products()
        self.customers = customer_dao.get_all_customers()
        self.vehicles = vehicle_dao.get_all_vehicles()

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

    def on_product_change(self, event):
        idx = self.cbo_product.current()
        if 0 <= idx < len(self.products):
            p = self.products[idx]
            self.ent_price.delete(0, tk.END)
            self.ent_price.insert(0, str(int(p['price'])))
            self.calculate_totals()

    def on_vehicle_change(self, event):
        idx = self.cbo_vehicle.current()
        if 0 <= idx < len(self.vehicles):
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

            self.lbl_price_words.config(text=f" Bằng chữ: {num2vietnamese_words(price)}")
            self.lbl_shipping_words.config(text=f" Bằng chữ: {num2vietnamese_words(shipping)}")
            self.lbl_paid_words.config(text=f" Bằng chữ: {num2vietnamese_words(paid)}")

            product_amt = total_vol * price
            total_amt = product_amt + shipping
            debt_amt = max(0, total_amt - paid)

            self.lbl_summary_amount.config(text=f"TỔNG TIỀN: {total_amt:,.0f} VNĐ")
            self.lbl_summary_words.config(text=f" Tổng tiền bằng chữ: {num2vietnamese_words(total_amt)}")
            
            self.lbl_summary_debt.config(text=f"GHI NỢ KHÁCH: {debt_amt:,.0f} VNĐ")
            self.lbl_debt_words.config(text=f" Tiền nợ bằng chữ: {num2vietnamese_words(debt_amt)}")
        except ValueError:
            pass

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
                    customer_dao.add_customer(cust_text, "", "Tự động tạo từ ô nhập đơn", config.DEFAULT_CREDIT_LIMIT, 0)
                    all_c = customer_dao.get_all_customers()
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

            code, total_vol, total_amt, debt = order_dao.create_order_transaction(
                cust_id, veh['id'], prod['id'], vol_trip, trips, price, shipping, paid, note
            )

            messagebox.showinfo("Thành Công", f"Đã tạo đơn hàng thành công!\nMã đơn: {code}\nKhách hàng: {cust_name}\nTổng xuất: {total_vol:,.1f} m³ {prod['name']}\nTổng tiền: {total_amt:,.0f}đ\nGhi nợ: {debt:,.0f}đ")

            self.load_data()
            if self.on_order_created:
                self.on_order_created()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo đơn hàng: {str(e)}")

    # Delegate quick dialogs to modules
    def open_quick_customer_dialog(self):
        from views.dialogs.quick_customer_dialog import open_quick_customer_dialog
        self.refresh_callback = self.load_data  # Dialogs expect parent.refresh_callback
        open_quick_customer_dialog(self)

    def open_quick_product_dialog(self):
        from views.dialogs.quick_product_dialog import open_quick_product_dialog
        self.refresh_callback = self.load_data
        open_quick_product_dialog(self)

    def open_quick_vehicle_dialog(self):
        from views.dialogs.quick_vehicle_dialog import open_quick_vehicle_dialog
        self.refresh_callback = self.load_data
        open_quick_vehicle_dialog(self)
