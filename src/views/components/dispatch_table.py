import tkinter as tk
from tkinter import ttk
import config
from dao import vehicle_dao

class DispatchTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        columns = ("id", "plate", "driver", "capacity", "trips", "delivered_vol", "pay_per_trip", "total_pay", "fuel_est")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("plate", text="Biển Số Xe")
        self.tree.heading("driver", text="Tài Xế Phụ Trách")
        self.tree.heading("capacity", text="Sức Chứa (m³)")
        self.tree.heading("trips", text="Tổng Số Chuyến Đã Chạy")
        self.tree.heading("delivered_vol", text="Tổng Khối Lượng Giao")
        self.tree.heading("pay_per_trip", text="Thù Lao/Chuyến")
        self.tree.heading("total_pay", text="Tổng Tiền Lương Chuyến")
        self.tree.heading("fuel_est", text="Định Mức Xăng Dầu")

        self.tree.column("id", width=40)
        self.tree.column("plate", width=120)
        self.tree.column("driver", width=180)
        self.tree.column("capacity", width=100)
        self.tree.column("trips", width=150)
        self.tree.column("delivered_vol", width=140)
        self.tree.column("pay_per_trip", width=120)
        self.tree.column("total_pay", width=140)
        self.tree.column("fuel_est", width=130)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_dispatch_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        dispatch_summary = vehicle_dao.get_driver_trip_summary()
        vehicles = vehicle_dao.get_all_vehicles()
        veh_map = {v['plate_number']: v['id'] for v in vehicles}

        for d in dispatch_summary:
            total_trips = d['total_trips']
            pay_per_trip = d['pay_per_trip']
            fuel_per_trip = d['fuel_per_trip']
            total_pay = total_trips * pay_per_trip
            total_fuel = total_trips * fuel_per_trip
            v_id = veh_map.get(d['plate_number'], 0)

            self.tree.insert("", "end", values=(
                v_id,
                d['plate_number'],
                d['driver_name'],
                f"{d.get('capacity_m3', config.DEFAULT_VEHICLE_CAPACITY):,.1f} m³",
                f"{total_trips} chuyến",
                f"{d['total_volume_delivered']:,.1f} m³",
                f"{pay_per_trip:,.0f}đ",
                f"{total_pay:,.0f}đ",
                f"{total_fuel:,.0f}đ"
            ))

    def get_selected_vehicle(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None
        values = self.tree.item(selected_item[0])['values']
        return values
