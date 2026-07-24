"""
Customer & Contractor Management View for VLXD Thống Nhất
Stores customer profiles, contact info, contractor status, and full CRUD (Thêm, Sửa, Xóa).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from utils import num2vietnamese_words

class CustomerView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="👥 QUẢN LÝ HỒ SƠ KHÁCH HÀNG & NHÀ THẦU", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Top Control Bar (Add, Edit, Delete)
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text="➕ Thêm Khách Hàng", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_add_customer_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="✏️ Sửa Khách Hàng", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_edit_customer_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="❌ Xóa Khách Hàng", bg="#dc2626", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.delete_selected_customer).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text="🔄 Tải Lại Danh Sách", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_customers).pack(side="right")

        # Customers Table
        columns = ("id", "name", "phone", "address", "is_contractor", "debt", "limit", "created_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Họ Tên Khách Hàng / Nhà Thầu")
        self.tree.heading("phone", text="Số Điện Thoại")
        self.tree.heading("address", text="Địa Chỉ / Công Trình Chi Tiết")
        self.tree.heading("is_contractor", text="Phân Loại")
        self.tree.heading("debt", text="Nợ Hiện Tại")
        self.tree.heading("limit", text="Hạn Mức Cho Nợ")
        self.tree.heading("created_at", text="Ngày Tạo")

        self.tree.column("id", width=40)
        self.tree.column("name", width=220)
        self.tree.column("phone", width=110)
        self.tree.column("address", width=250)
        self.tree.column("is_contractor", width=110)
        self.tree.column("debt", width=120)
        self.tree.column("limit", width=120)
        self.tree.column("created_at", width=140)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_customers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        customers = database.get_all_customers()
        for c in customers:
            type_str = "🏗️ Nhà thầu/Sỉ" if c['is_contractor'] else "🏠 Khách lẻ"
            self.tree.insert("", "end", values=(
                c['id'],
                c['name'],
                c['phone'] or "",
                c['address'] or "",
                type_str,
                f"{c['debt']:,.0f}đ",
                f"{c['credit_limit']:,.0f}đ",
                c['created_at'] or ""
            ))

    def open_add_customer_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm Khách Hàng Mới")
        dlg.geometry("400x340")
        dlg.grab_set()

        ttk.Label(dlg, text="Tạo Hồ Sơ Khách Hàng / Nhà Thầu", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Họ tên Khách / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=3)
        ent_name = ttk.Entry(form, width=25)
        ent_name.grid(row=0, column=1, pady=3)

        ttk.Label(form, text="Số điện thoại:").grid(row=1, column=0, sticky="w", pady=3)
        ent_phone = ttk.Entry(form, width=25)
        ent_phone.grid(row=1, column=1, pady=3)

        ttk.Label(form, text="Địa chỉ / Công trình:").grid(row=2, column=0, sticky="w", pady=3)
        ent_addr = ttk.Entry(form, width=25)
        ent_addr.grid(row=2, column=1, pady=3)

        ttk.Label(form, text="Hạn mức cho nợ (đ):").grid(row=3, column=0, sticky="w", pady=3)
        ent_limit = ttk.Entry(form, width=25)
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

        ttk.Label(form, text="Loại khách hàng:").grid(row=5, column=0, sticky="w", pady=3)
        var_is_contractor = tk.IntVar(value=1)
        r1 = ttk.Radiobutton(form, text="Nhà thầu / Khách sỉ", variable=var_is_contractor, value=1)
        r2 = ttk.Radiobutton(form, text="Khách mua lẻ dân dụng", variable=var_is_contractor, value=0)
        r1.grid(row=5, column=1, sticky="w")
        r2.grid(row=6, column=1, sticky="w")

        def save_customer():
            try:
                name = ent_name.get().strip()
                if not name:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên khách hàng!")
                    return

                database.add_customer(
                    name,
                    ent_phone.get().strip(),
                    ent_addr.get().strip(),
                    float(ent_limit.get() or 50000000),
                    var_is_contractor.get()
                )
                messagebox.showinfo("Thành công", "Đã thêm khách hàng mới!")
                dlg.destroy()
                self.load_customers()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm khách hàng: {str(e)}")

        tk.Button(dlg, text="Lưu Khách Hàng", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), command=save_customer).pack(pady=10)

    def open_edit_customer_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần sửa từ danh sách!")
            return

        values = self.tree.item(selected_item[0])['values']
        cust_id = values[0]

        customers = database.get_all_customers()
        c_list = [c for c in customers if c['id'] == cust_id]
        if not c_list:
            return
        c = c_list[0]

        dlg = tk.Toplevel(self)
        dlg.title("Sửa Thông Tin Khách Hàng")
        dlg.geometry("400x340")
        dlg.grab_set()

        ttk.Label(dlg, text="Cập Nhật Hồ Sơ Khách Hàng", font=("Segoe UI", 12, "bold"), foreground="#d97706").pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Họ tên Khách / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=3)
        ent_name = ttk.Entry(form, width=25)
        ent_name.insert(0, c['name'])
        ent_name.grid(row=0, column=1, pady=3)

        ttk.Label(form, text="Số điện thoại:").grid(row=1, column=0, sticky="w", pady=3)
        ent_phone = ttk.Entry(form, width=25)
        ent_phone.insert(0, c['phone'] or "")
        ent_phone.grid(row=1, column=1, pady=3)

        ttk.Label(form, text="Địa chỉ / Công trình:").grid(row=2, column=0, sticky="w", pady=3)
        ent_addr = ttk.Entry(form, width=25)
        ent_addr.insert(0, c['address'] or "")
        ent_addr.grid(row=2, column=1, pady=3)

        ttk.Label(form, text="Hạn mức cho nợ (đ):").grid(row=3, column=0, sticky="w", pady=3)
        ent_limit = ttk.Entry(form, width=25)
        ent_limit.insert(0, str(int(c['credit_limit'])))
        ent_limit.grid(row=3, column=1, pady=3)

        ttk.Label(form, text="Bằng chữ:").grid(row=4, column=0, sticky="w", pady=3)
        lbl_limit_words = ttk.Label(form, text=num2vietnamese_words(c['credit_limit']), font=("Segoe UI", 9, "italic", "bold"), foreground="#2563eb")
        lbl_limit_words.grid(row=4, column=1, sticky="w", pady=3)

        def on_limit_change(event=None):
            val = ent_limit.get().strip()
            words = num2vietnamese_words(val)
            lbl_limit_words.config(text=words)

        ent_limit.bind("<KeyRelease>", on_limit_change)

        ttk.Label(form, text="Loại khách hàng:").grid(row=5, column=0, sticky="w", pady=3)
        var_is_contractor = tk.IntVar(value=c['is_contractor'])
        r1 = ttk.Radiobutton(form, text="Nhà thầu / Khách sỉ", variable=var_is_contractor, value=1)
        r2 = ttk.Radiobutton(form, text="Khách mua lẻ dân dụng", variable=var_is_contractor, value=0)
        r1.grid(row=5, column=1, sticky="w")
        r2.grid(row=6, column=1, sticky="w")

        def update_cust():
            try:
                name = ent_name.get().strip()
                if not name:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên khách hàng!")
                    return

                database.update_customer(
                    cust_id,
                    name,
                    ent_phone.get().strip(),
                    ent_addr.get().strip(),
                    float(ent_limit.get() or 50000000),
                    var_is_contractor.get()
                )
                messagebox.showinfo("Thành công", f"Đã cập nhật khách hàng [{name}]!")
                dlg.destroy()
                self.load_customers()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật khách hàng: {str(e)}")

        tk.Button(dlg, text="💾 Cập Nhật Khách Hàng", bg="#d97706", fg="white", font=("Segoe UI", 10, "bold"), command=update_cust).pack(pady=10)

    def delete_selected_customer(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần xóa từ danh sách!")
            return

        values = self.tree.item(selected_item[0])['values']
        cust_id = values[0]
        cust_name = values[1]

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA khách hàng [{cust_name}] khỏi hệ thống?"):
            try:
                database.delete_customer(cust_id)
                messagebox.showinfo("Thành công", f"Đã xóa thành công khách hàng [{cust_name}]!")
                self.load_customers()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa khách hàng: {str(e)}")
