import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import threading
import time
import config
from dao import invoice_dao, product_dao
from helpers.xml_parser import process_bulk_xml
from tkinterdnd2 import DND_FILES

class TaxReportView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.products = []
        self.file_paths = {} # Lưu trữ đường dẫn file gốc của từng dòng
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text=" BÁO CÁO THUẾ & HÓA ĐƠN ĐẦU VÀO", font=("Segoe UI", 14, "bold"), foreground=config.COLOR_PRIMARY_DARK).pack(side="left")
        ttk.Label(title_frame, text="*Theo dõi chênh lệch Khối lượng nhập (Hóa đơn) và xuất (Bán thực tế)*", font=("Segoe UI", 10, "italic"), foreground=config.COLOR_SECONDARY_DARK).pack(side="right")

        content_box = ttk.Frame(self)
        content_box.pack(fill="both", expand=True)

        # LEFT FORM: Nhập hóa đơn đầu vào
        form_frame = ttk.LabelFrame(content_box, text=" Nhập Hóa Đơn Mua Vật Liệu (Đầu Vào) ", padding=12)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form_frame, text="Số Hóa Đơn (vd: HD0123):").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_code = ttk.Entry(form_frame, width=22)
        self.ent_code.grid(row=0, column=1, pady=4, sticky="ew")

        ttk.Label(form_frame, text="Ngày Nhập (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_date = ttk.Entry(form_frame, width=22)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.grid(row=1, column=1, pady=4, sticky="ew")

        ttk.Label(form_frame, text="Loại Hóa Đơn:").grid(row=2, column=0, sticky="w", pady=4)
        self.cbo_inv_category = ttk.Combobox(form_frame, width=20, state="readonly", values=["Vật liệu (Cấn trừ m³)", "Chi phí vận hành (Dầu/Sửa xe)"])
        self.cbo_inv_category.current(0)
        self.cbo_inv_category.grid(row=2, column=1, pady=4, sticky="ew")

        ttk.Label(form_frame, text="Vật Liệu Khấu Trừ:").grid(row=3, column=0, sticky="w", pady=4)
        self.cbo_product = ttk.Combobox(form_frame, width=20, state="readonly")
        self.cbo_product.grid(row=3, column=1, pady=4, sticky="ew")

        ttk.Label(form_frame, text="Khối Lượng Mua (m³):").grid(row=4, column=0, sticky="w", pady=4)
        self.ent_volume = ttk.Entry(form_frame, width=22)
        self.ent_volume.grid(row=4, column=1, pady=4, sticky="ew")

        ttk.Label(form_frame, text="Tổng Tiền Hóa Đơn (đ):").grid(row=5, column=0, sticky="w", pady=4)
        self.ent_amount = ttk.Entry(form_frame, width=22)
        self.ent_amount.grid(row=5, column=1, pady=4, sticky="ew")
        
        self.lbl_amount_text = tk.Label(form_frame, text="", font=("Segoe UI", 9, "italic"), fg="#059669")
        self.lbl_amount_text.grid(row=5, column=2, sticky="w", padx=5)
        
        def on_amount_change(e=None):
            from utils import num2vietnamese_words
            val = self.ent_amount.get().replace(",", "")
            self.lbl_amount_text.config(text=num2vietnamese_words(val))
        self.ent_amount.bind("<KeyRelease>", on_amount_change)

        ttk.Label(form_frame, text="Ghi Chú:").grid(row=6, column=0, sticky="w", pady=4)
        self.ent_note = ttk.Entry(form_frame, width=22)
        self.ent_note.grid(row=6, column=1, pady=4, sticky="ew")

        def on_category_select(e=None):
            if self.cbo_inv_category.current() == 1: # Chi phí vận hành
                self.cbo_product.configure(state="disabled")
                self.ent_volume.delete(0, tk.END)
                self.ent_volume.insert(0, "0")
                self.ent_volume.configure(state="disabled")
            else:
                self.cbo_product.configure(state="readonly")
                self.ent_volume.configure(state="normal")
        self.cbo_inv_category.bind("<<ComboboxSelected>>", on_category_select)

        tk.Button(form_frame, text=" LƯU HÓA ĐƠN", bg=config.COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), pady=6, command=self.save_invoice).grid(row=7, column=0, columnspan=2, sticky="ew", pady=15)

        # RIGHT: Bảng Thống kê Thuế
        right_frame = ttk.Frame(content_box)
        right_frame.pack(side="right", fill="both", expand=True)

        # Thanh lọc thời gian
        filter_bar = ttk.Frame(right_frame, padding=(0, 0, 0, 8))
        filter_bar.pack(fill="x")

        ttk.Label(filter_bar, text=" Lọc thời gian:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
        self.cbo_time_filter = ttk.Combobox(filter_bar, width=15, state="readonly", values=[
            "Tháng này", "Tháng trước", "Quý 1", "Quý 2", "Quý 3", "Quý 4", "Năm nay", "Tất cả"
        ])
        self.cbo_time_filter.current(0)
        self.cbo_time_filter.pack(side="left", padx=(0, 10))
        self.cbo_time_filter.bind("<<ComboboxSelected>>", lambda e: self.load_summary())

        tk.Button(filter_bar, text=" Tải Lại Báo Cáo", bg=config.COLOR_SECONDARY, fg="white", padx=8, command=self.load_summary).pack(side="right")

        # Bảng Tổng Hợp Chênh Lệch
        summary_frame = ttk.LabelFrame(right_frame, text=" Bảng Đối Chiếu Nhập Xuất (Khối Lượng) ", padding=10)
        summary_frame.pack(fill="both", expand=True)

        cols = ("product", "total_in", "total_out", "diff")
        self.tree_summary = ttk.Treeview(summary_frame, columns=cols, show="headings", height=10)
        self.tree_summary.heading("product", text="Tên Vật Liệu")
        self.tree_summary.heading("total_in", text="Tổng Nhập (Có HĐ)")
        self.tree_summary.heading("total_out", text="Tổng Xuất Bán")
        self.tree_summary.heading("diff", text="Chênh Lệch (Tồn Kho HĐ)")

        self.tree_summary.column("product", width=200)
        self.tree_summary.column("total_in", width=150, anchor="e")
        self.tree_summary.column("total_out", width=150, anchor="e")
        self.tree_summary.column("diff", width=180, anchor="e")

        self.tree_summary.tag_configure('danger', foreground='red', font=("Segoe UI", 9, "bold"))
        self.tree_summary.tag_configure('safe', foreground='green', font=("Segoe UI", 9, "bold"))

        self.tree_summary.pack(side="left", fill="both", expand=True)

        # Cảnh báo
        self.lbl_warning = ttk.Label(right_frame, text="", font=("Segoe UI", 10, "bold"), foreground=config.COLOR_DANGER)
        self.lbl_warning.pack(fill="x", pady=(5, 5))

        # THẺ THỐNG KÊ KHẤU TRỪ THUẾ & CHI PHÍ TNDN (NEW)
        vat_card_frame = ttk.LabelFrame(right_frame, text=" Tổng Hợp Thuế VAT Khấu Trừ & Chi Phí TNDN ", padding=8)
        vat_card_frame.pack(fill="x", pady=(0, 5))

        card_inner = ttk.Frame(vat_card_frame)
        card_inner.pack(fill="x")

        self.lbl_vat_mat = tk.Label(card_inner, text="📦 VAT Vật Liệu: 0 đ", font=("Segoe UI", 9, "bold"), fg="#1e40af", bg="#eff6ff", padx=10, pady=4)
        self.lbl_vat_mat.pack(side="left", expand=True, fill="x", padx=2)

        self.lbl_vat_exp = tk.Label(card_inner, text="🚚 VAT Chi Phí (Dầu/Sửa): 0 đ", font=("Segoe UI", 9, "bold"), fg="#b45309", bg="#fffbeb", padx=10, pady=4)
        self.lbl_vat_exp.pack(side="left", expand=True, fill="x", padx=2)

        self.lbl_vat_total = tk.Label(card_inner, text="🛡️ TỔNG VAT KHẤU TRỪ: 0 đ", font=("Segoe UI", 9, "bold"), fg="#047857", bg="#ecfdf5", padx=10, pady=4)
        self.lbl_vat_total.pack(side="left", expand=True, fill="x", padx=2)

        self.lbl_exp_total = tk.Label(card_inner, text="💼 Chi Phí TNDN: 0 đ", font=("Segoe UI", 9, "bold"), fg="#6b21a8", bg="#faf5ff", padx=10, pady=4)
        self.lbl_exp_total.pack(side="left", expand=True, fill="x", padx=2)

        # BULK XML UPLOAD & DATA GRID (NEW)
        bulk_frame = ttk.LabelFrame(self, text=" Xử Lý Hóa Đơn Điện Tử Hàng Loạt (XML/PDF) ", padding=10)
        bulk_frame.pack(fill="both", expand=True, pady=10)
        
        bulk_toolbar = ttk.Frame(bulk_frame)
        bulk_toolbar.pack(fill="x", pady=(0, 5))
        
        tk.Button(bulk_toolbar, text="📂 Chọn File XML / PDF", bg="#475569", fg="white", font=("Segoe UI", 9, "bold"), command=self.select_xml_files).pack(side="left", padx=5)
        tk.Label(bulk_toolbar, text="Phím tắt: [Ctrl+Shift+S] Lưu toàn bộ lưới | [F4] Danh sách chi phí chờ").pack(side="right", padx=5)
        
        cols_xml = ("filename", "invoice_no", "invoice_date", "tax_code", "category", "hs_code", "total_before", "vat_rate", "total_amount", "status")
        self.grid_xml = ttk.Treeview(bulk_frame, columns=cols_xml, show="headings", height=6)
        self.grid_xml.heading("filename", text="Tên File")
        self.grid_xml.heading("invoice_no", text="Số HĐ")
        self.grid_xml.heading("invoice_date", text="Ngày Lập")
        self.grid_xml.heading("tax_code", text="Mã Số Thuế")
        self.grid_xml.heading("category", text="Loại HĐ")
        self.grid_xml.heading("hs_code", text="Mã VL (Gõ vào)")
        self.grid_xml.heading("total_before", text="Trước Thuế")
        self.grid_xml.heading("vat_rate", text="VAT (%)")
        self.grid_xml.heading("total_amount", text="Tổng Tiền")
        self.grid_xml.heading("status", text="Trạng Thái")
        
        self.grid_xml.column("filename", width=90)
        self.grid_xml.column("invoice_no", width=70)
        self.grid_xml.column("invoice_date", width=80)
        self.grid_xml.column("tax_code", width=90)
        self.grid_xml.column("category", width=110)
        self.grid_xml.column("hs_code", width=90)
        self.grid_xml.column("total_before", width=95, anchor="e")
        self.grid_xml.column("vat_rate", width=55, anchor="center")
        self.grid_xml.column("total_amount", width=105, anchor="e")
        self.grid_xml.column("status", width=160)
        
        self.grid_xml.pack(side="left", fill="both", expand=True)
        
        scroll_xml = ttk.Scrollbar(bulk_frame, orient="vertical", command=self.grid_xml.yview)
        self.grid_xml.configure(yscrollcommand=scroll_xml.set)
        scroll_xml.pack(side="right", fill="y")
        
        # Binds for Grid Edit and Hotkeys
        self.grid_xml.bind("<Double-1>", self.on_grid_double_click)
        
        # To make global hotkeys work even if the tab is just visible, we bind to the toplevel window
        # But we need to ensure they only trigger when this tab is active. We will do a generic bind on the app root in a real scenario,
        # For simplicity here, we bind to self, but tk requires focus.
        self.bind("<Control-S>", lambda e: self.save_bulk_invoices())
        self.bind("<Control-s>", lambda e: self.save_bulk_invoices())
        self.bind("<F4>", lambda e: self.show_pending_invoices())
        
        # Bind Focus In to ensure tab grabs hotkeys
        self.bind("<Visibility>", lambda e: self.focus_set())
        
        # ENABLE DRAG AND DROP
        getattr(self.grid_xml, "drop_target_register")(DND_FILES)
        getattr(self.grid_xml, "dnd_bind")('<<Drop>>', self.on_files_dropped)

    def get_date_bounds(self):
        filter_opt = self.cbo_time_filter.get()
        now = datetime.now()
        year = now.year

        if filter_opt == "Tất cả": return None, None
        if filter_opt == "Tháng này":
            start = f"{year}-{now.month:02d}-01"
            next_month = now.replace(day=28) + timedelta(days=4)
            end = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")
            return start, end
        if filter_opt == "Tháng trước":
            pm = 12 if now.month == 1 else now.month - 1
            py = year - 1 if now.month == 1 else year
            start = f"{py}-{pm:02d}-01"
            dt = datetime(py, pm, 28) + timedelta(days=4)
            end = (dt - timedelta(days=dt.day)).strftime("%Y-%m-%d")
            return start, end
        if filter_opt == "Quý 1": return f"{year}-01-01", f"{year}-03-31"
        if filter_opt == "Quý 2": return f"{year}-04-01", f"{year}-06-30"
        if filter_opt == "Quý 3": return f"{year}-07-01", f"{year}-09-30"
        if filter_opt == "Quý 4": return f"{year}-10-01", f"{year}-12-31"
        if filter_opt == "Năm nay": return f"{year}-01-01", f"{year}-12-31"
        return None, None

    def load_data(self):
        self.products = product_dao.get_all_products()
        self.cbo_product["values"] = [p['name'] for p in self.products]
        if self.products:
            self.cbo_product.current(0)
        self.load_summary()

    def load_summary(self):
        for item in self.tree_summary.get_children():
            self.tree_summary.delete(item)

        start, end = self.get_date_bounds()
        summary = invoice_dao.get_tax_summary(start, end)
        
        has_warning = False
        warning_msg = " CẢNH BÁO ĐỎ: Cửa hàng đang xuất bán nhiều hơn số lượng hóa đơn nhập vào đối với các mặt hàng: "
        warning_items = []

        for row in summary:
            diff = row['diff']
            tag = 'safe' if diff >= 0 else 'danger'
            
            if diff < 0:
                has_warning = True
                warning_items.append(f"{row['product_name']} ({diff:,.1f} m³)")

            self.tree_summary.insert("", "end", values=(
                row['product_name'],
                f"{row['total_in']:,.1f}",
                f"{row['total_out']:,.1f}",
                f"{diff:,.1f}"
            ), tags=(tag,))

        if has_warning:
            self.lbl_warning.config(text=warning_msg + ", ".join(warning_items) + ".\n Cần mua thêm hóa đơn đầu vào ngay để tránh phạt Thuế!")
        else:
            self.lbl_warning.config(text=" Mọi thứ an toàn. Khối lượng hóa đơn đầu vào hiện tại đủ bao phủ lượng xuất kho.", foreground=config.COLOR_SUCCESS)

        # Load VAT Deductions Summary
        vat_sum = invoice_dao.get_vat_deduction_summary(start, end)
        self.lbl_vat_mat.config(text=f"📦 VAT Vật Liệu: {vat_sum['vat_materials']:,.0f} đ")
        self.lbl_vat_exp.config(text=f"🚚 VAT Chi Phí (Dầu/Sửa): {vat_sum['vat_expenses']:,.0f} đ")
        self.lbl_vat_total.config(text=f"🛡️ TỔNG VAT KHẤU TRỪ: {vat_sum['total_vat_input']:,.0f} đ")
        self.lbl_exp_total.config(text=f"💼 Chi Phí TNDN: {vat_sum['total_expense_amount']:,.0f} đ")

    def save_invoice(self):
        code = self.ent_code.get().strip()
        date = self.ent_date.get().strip()
        cat_idx = self.cbo_inv_category.current()
        category = "Chi phí vận hành" if cat_idx == 1 else "Vật liệu"
        
        idx = self.cbo_product.current()
        vol = self.ent_volume.get().strip()
        amt = self.ent_amount.get().strip()
        note = self.ent_note.get().strip()

        if not code or not date or not amt:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ Số HĐ, Ngày và Tổng tiền!")
            return

        try:
            amt = float(amt.replace(",", ""))
            vat_amount = amt * 0.1 # Giả định 10% VAT
            
            if category == "Vật liệu":
                if idx < 0 or not vol:
                    messagebox.showwarning("Thiếu thông tin", "Hóa đơn Vật liệu cần chọn Loại vật liệu và Khối lượng!")
                    return
                vol = float(vol)
                pid = self.products[idx]['id']
            else:
                vol = 0.0
                pid = None

            if invoice_dao.add_invoice(code, date, pid, vol, amt, note, category=category, vat_amount=vat_amount):
                messagebox.showinfo("Thành công", f"Đã lưu hóa đơn {category} [{code}] thành công!")
                self.ent_code.delete(0, tk.END)
                self.ent_amount.delete(0, tk.END)
                self.load_summary()
            else:
                messagebox.showerror("Lỗi", f"Hóa đơn {code} đã tồn tại trong hệ thống!")
        except ValueError:
            messagebox.showerror("Lỗi", "Khối lượng và Tổng tiền phải là số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    # --- ADVANCED BULK PROCESSING FEATURES ---
    
    def select_xml_files(self):
        files = filedialog.askopenfilenames(
            title="Chọn các file Hóa Đơn Điện Tử (XML / PDF)",
            filetypes=[("Hóa đơn", "*.xml *.pdf"), ("XML files", "*.xml"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if files:
            # Show a processing status (in a real app, use a progress bar)
            for item in self.grid_xml.get_children():
                self.grid_xml.delete(item)
                
            parsed_data = process_bulk_xml(files)
            for data in parsed_data:
                item_id = self.grid_xml.insert("", "end", values=(
                    data["filename"],
                    data["invoice_no"],
                    data["invoice_date"],
                    data["tax_code"],
                    data.get("category", "Vật liệu"),
                    "---", # HS Code initially empty
                    f"{data['total_before_tax']:,.0f}",
                    f"{data['vat_rate']}",
                    f"{data['total_amount']:,.0f}",
                    data["status"]
                ))
                self.file_paths[item_id] = data.get("filepath", "")
                
    def split_dnd_files(self, data):
        # Handle spaced paths wrapped in braces from tkinterdnd2
        import re
        paths = re.findall(r'\{.*?\}|\S+', data)
        return [p.strip('{}') for p in paths if p.strip('{}').lower().endswith(('.xml', '.pdf'))]
        
    def on_files_dropped(self, event):
        files = self.split_dnd_files(event.data)
        if files:
            for item in self.grid_xml.get_children():
                self.grid_xml.delete(item)
                
            parsed_data = process_bulk_xml(files)
            for data in parsed_data:
                item_id = self.grid_xml.insert("", "end", values=(
                    data["filename"],
                    data["invoice_no"],
                    data["invoice_date"],
                    data["tax_code"],
                    data.get("category", "Vật liệu"),
                    "---",
                    f"{data['total_before_tax']:,.0f}",
                    f"{data['vat_rate']}",
                    f"{data['total_amount']:,.0f}",
                    data["status"]
                ))
                self.file_paths[item_id] = data.get("filepath", "")
    
    def on_grid_double_click(self, event):
        """Allows inline editing of the HS Code to trigger the Mock API"""
        region = self.grid_xml.identify("region", event.x, event.y)
        if region != "cell": return
        column = self.grid_xml.identify_column(event.x)
        item = self.grid_xml.focus()
        
        # Column #5 is Category, Column #6 is hs_code
        if column == "#5":
            curr_val = self.grid_xml.set(item, column)
            new_val = "Chi phí vận hành" if curr_val == "Vật liệu" else "Vật liệu"
            self.grid_xml.set(item, column, new_val)
        elif column == "#6":
            x, y, width, height = self.grid_xml.bbox(item, column)
            
            entry = ttk.Entry(self.grid_xml, width=int(width))
            entry.place(x=x, y=y, width=width, height=height)
            
            def save_edit(e):
                new_val = entry.get().strip()
                if new_val:
                    # Update Treeview immediately
                    self.grid_xml.set(item, column, new_val)
                    self.grid_xml.set(item, "#10", "Đang tra cứu API thuế suất...")
                    # Call API non-blocking
                    threading.Thread(target=self.mock_hs_api_call, args=(item, new_val), daemon=True).start()
                entry.destroy()
                
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: entry.destroy())
            entry.focus_set()

    def mock_hs_api_call(self, item, hs_code):
        """Simulates a fast API call that doesn't freeze the UI"""
        time.sleep(0.5) # Fake network delay
        
        # Fake logic
        if "DA" in hs_code.upper():
            vat = 8.0
        elif "CAT" in hs_code.upper():
            vat = 10.0
        else:
            vat = 5.0
            
        # Update UI back in the main thread using after()
        def update_ui():
            try:
                self.grid_xml.set(item, "#8", f"{vat}")
                self.grid_xml.set(item, "#10", "Đã cập nhật thuế suất thành công")
            except Exception:
                pass # Item might have been deleted
                
        self.after(0, update_ui)

    def save_bulk_invoices(self):
        """Handles the Ctrl+Shift+S hotkey"""
        children = self.grid_xml.get_children()
        if not children:
            messagebox.showinfo("Thông báo", "Lưới dữ liệu trống. Không có gì để lưu.")
            return
        
        import os
        import shutil
        invoices_dir = os.path.join(config.APP_DATA_DIR, "invoices")
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)

        success_count = 0
        import random
        for item in children:
            vals = self.grid_xml.item(item, "values")
            filename, inv_no, inv_date, tax_code, category, hs_code, total_before, vat_rate, total_amount, status = vals
            
            filepath = self.file_paths.get(item)
            if filepath and os.path.exists(filepath):
                try:
                    filename = os.path.basename(filepath)
                    dest = os.path.join(invoices_dir, filename)
                    shutil.copy2(filepath, dest)
                except Exception:
                    pass

            try:
                # Clean numbers
                tb = float(total_before.replace(",", ""))
                vr = float(vat_rate)
                ta = float(total_amount.replace(",", ""))
                vat_amt = (tb * vr) / 100.0 if vr > 0 else (ta - tb)
                if vat_amt < 0: vat_amt = 0.0

                code = inv_no if inv_no and inv_no != "N/A" else f"HD{random.randint(1000, 9999)}"
                date = inv_date if inv_date and inv_date != "N/A" else datetime.now().strftime("%Y-%m-%d")
                
                pid = None
                vol = 0.0
                if category == "Vật liệu":
                    # Pick first product if available for demo matching
                    if self.products:
                        pid = self.products[0]['id']
                    vol = 10.0 # Default fallback volume for bulk XML

                invoice_dao.add_invoice(
                    code=code,
                    import_date=date,
                    product_id=pid,
                    volume=vol,
                    amount=ta,
                    note=f"Hóa đơn {category} ({filename})",
                    category=category,
                    vat_amount=vat_amt,
                    seller_tax_code=tax_code
                )
                success_count += 1
                self.grid_xml.set(item, "#10", "Đã lưu DB & Cấn trừ VAT!")
            except Exception as e:
                self.grid_xml.set(item, "#10", f"Lỗi lưu DB: {str(e)}")
        
        messagebox.showinfo("Lưu Thành Công", f"Đã tự động cấn trừ thuế VAT và ghi nhận DB cho {success_count} hóa đơn!\nFile gốc lưu tại: {invoices_dir}")
        self.load_summary()

    def show_pending_invoices(self):
        """Handles the F4 hotkey"""
        messagebox.showinfo("Danh Sách Chờ Hóa Đơn (F4)", "Tính năng mở nhanh:\n\n1. Hợp đồng NK012: Thiếu 20 triệu VAT\n2. Hợp đồng Cát San Lấp: Thiếu 15 triệu VAT\n\nHệ thống đang chờ hóa đơn bù vào!")
