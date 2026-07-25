"""
Contractor Debt & Revenue Management View for VLXD Thống Nhất
Tracks debts, credit limits, payments, and financial history.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
from dao import product_dao, customer_dao, vehicle_dao, order_dao, employee_dao
from utils import num2vietnamese_words

class DebtView(ttk.Frame):
    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent, padding=10)
        self.refresh_callback = refresh_callback
        self.setup_ui()
        self.load_debt_data()

    def setup_ui(self):
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame, text="💳 QUẢN LÝ CÔNG NỢ NHÀ THẦU & THU TIỀN NỢ", font=("Segoe UI", 14, "bold"), foreground="#1e3a8a").pack(side="left")

        # Top Button Bar
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", pady=(0, 10))

        tk.Button(btn_bar, text=" Ghi Nhận Khách Trả Tiền Nợ", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.open_pay_debt_dialog).pack(side="left", padx=(0, 5))
        tk.Button(btn_bar, text=" Tải Lại Sổ Nợ", bg="#64748b", fg="white", font=("Segoe UI", 10), padx=10, pady=5, command=self.load_debt_data).pack(side="right")

        # Debt Table
        columns = ("id", "name", "phone", "address", "type", "debt", "limit", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Khách Hàng / Nhà Thầu")
        self.tree.heading("phone", text="Số Điện Thoại")
        self.tree.heading("address", text="Địa Chỉ / Công Trình")
        self.tree.heading("type", text="Loại Khách")
        self.tree.heading("debt", text="Dư Nợ Hiện Tại")
        self.tree.heading("limit", text="Hạn Mức Nợ")
        self.tree.heading("status", text="Cảnh Báo Nợ")

        self.tree.column("id", width=40)
        self.tree.column("name", width=220)
        self.tree.column("phone", width=110)
        self.tree.column("address", width=240)
        self.tree.column("type", width=100)
        self.tree.column("debt", width=130)
        self.tree.column("limit", width=130)
        self.tree.column("status", width=130)

        # Style tags
        self.tree.tag_configure("overdue", background="#fecaca", foreground="#b91c1c")
        self.tree.tag_configure("normal", background="#ffffff")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_debt_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        customers = customer_dao.get_all_customers()
        for c in customers:
            debt = c['debt']
            limit = c['credit_limit']
            is_contractor = "Nhà thầu/Sỉ" if c['is_contractor'] else "Khách lẻ"

            status = " NỢ CAO" if debt >= limit * 0.8 else " AN TOÀN"
            tag = "overdue" if debt >= limit * 0.8 else "normal"

            self.tree.insert("", "end", values=(
                c['id'],
                c['name'],
                c['phone'] or "",
                c['address'] or "",
                is_contractor,
                f"{debt:,.0f}đ",
                f"{limit:,.0f}đ",
                status
            ), tags=(tag,))

    def open_pay_debt_dialog(self):
        customers = customer_dao.get_all_customers()
        if not customers:
            return

        dlg = tk.Toplevel(self)
        dlg.title("Ghi Nhận Thu Tiền Nợ")
        dlg.geometry("380x250")
        dlg.grab_set()

        ttk.Label(dlg, text="Phiếu Thu Tiền Nợ Khách Hàng", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form = ttk.Frame(dlg, padding=10)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Chọn Khách hàng / Nhà thầu:").grid(row=0, column=0, sticky="w", pady=5)
        cbo_cust = ttk.Combobox(form, width=28, state="readonly", values=[f"{c['name']} (Nợ: {c['debt']:,.0f}đ)" for c in customers])
        cbo_cust.grid(row=0, column=1, pady=5)
        cbo_cust.current(0)

        ttk.Label(form, text="Số tiền khách trả (đ):").grid(row=1, column=0, sticky="w", pady=5)
        ent_pay = ttk.Entry(form, width=28)
        ent_pay.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Bằng chữ:").grid(row=2, column=0, sticky="w", pady=3)
        lbl_pay_words = ttk.Label(form, text="Không đồng", font=("Segoe UI", 9, "italic", "bold"), foreground="#059669")
        lbl_pay_words.grid(row=2, column=1, sticky="w", pady=3)

        def on_pay_change(event=None):
            val = ent_pay.get().strip()
            words = num2vietnamese_words(val)
            lbl_pay_words.config(text=words)

        ent_pay.bind("<KeyRelease>", on_pay_change)

        ttk.Label(form, text="Ghi chú thanh toán:").grid(row=3, column=0, sticky="w", pady=5)
        ent_note = ttk.Entry(form, width=28)
        ent_note.insert(0, "Trả nợ tiền cát đá")
        ent_note.grid(row=3, column=1, pady=5)

        def save_payment():
            try:
                idx = cbo_cust.current()
                cust_id = customers[idx]['id']
                pay_amt = float(ent_pay.get())
                note = ent_note.get()

                if pay_amt <= 0:
                    messagebox.showwarning("Cảnh báo", "Số tiền trả phải lớn hơn 0!")
                    return

                customer_dao.record_debt_payment(cust_id, pay_amt, note)
                messagebox.showinfo("Thành công", f"Đã ghi nhận thu {pay_amt:,.0f}đ từ {customers[idx]['name']}!")
                dlg.destroy()
                self.load_debt_data()
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể ghi nhận thanh toán: {str(e)}")

        tk.Button(dlg, text="Xác Nhận Thu Tiền", bg="#059669", fg="white", font=("Segoe UI", 10, "bold"), command=save_payment).pack(pady=10)
