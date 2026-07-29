import os
import sys
import json

# Define AppData directory for the application
APP_NAME = "VLXD_ThongNhat"

# Xác định thư mục chứa file chạy (.exe hoặc thư mục code)
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

portable_db_path = os.path.join(application_path, "vlxd_thongnhat.db")

if sys.platform == "win32":
    local_app_data = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
    APP_DATA_DIR = os.path.join(local_app_data, APP_NAME)
else:
    APP_DATA_DIR = os.path.join(os.path.expanduser('~'), f".{APP_NAME}")

if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

# CHẾ ĐỘ PORTABLE: Nếu thấy file .db nằm cạnh file .exe thì ưu tiên đọc file đó!
if os.path.exists(portable_db_path):
    DB_PATH = portable_db_path
    SETTINGS_PATH = os.path.join(application_path, "settings.json")
else:
    DB_PATH = os.path.join(APP_DATA_DIR, "vlxd_thongnhat.db")
    SETTINGS_PATH = os.path.join(APP_DATA_DIR, "settings.json")

# Business Defaults
DEFAULT_CREDIT_LIMIT = 50000000.0
DEFAULT_VEHICLE_CAPACITY = 2.2
DEFAULT_PAY_PER_TRIP = 50000.0
DEFAULT_FUEL_PER_TRIP = 30000.0
DEFAULT_MIN_STOCK = 10.0

def load_settings():
    default_settings = {
        "credit_limit": DEFAULT_CREDIT_LIMIT,
        "vehicle_capacity": DEFAULT_VEHICLE_CAPACITY,
        "pay_per_trip": DEFAULT_PAY_PER_TRIP,
        "fuel_per_trip": DEFAULT_FUEL_PER_TRIP,
        "min_stock": DEFAULT_MIN_STOCK,
        "background_worker_interval": 3600
    }
    
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                for k, v in default_settings.items():
                    if k not in settings:
                        settings[k] = v
                return settings
        except Exception:
            pass
            
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)
    except Exception:
        pass
        
    return default_settings

SETTINGS = load_settings()

DEFAULT_CREDIT_LIMIT = SETTINGS.get("credit_limit", DEFAULT_CREDIT_LIMIT)
DEFAULT_VEHICLE_CAPACITY = SETTINGS.get("vehicle_capacity", DEFAULT_VEHICLE_CAPACITY)
DEFAULT_PAY_PER_TRIP = SETTINGS.get("pay_per_trip", DEFAULT_PAY_PER_TRIP)
DEFAULT_FUEL_PER_TRIP = SETTINGS.get("fuel_per_trip", DEFAULT_FUEL_PER_TRIP)
DEFAULT_MIN_STOCK = SETTINGS.get("min_stock", DEFAULT_MIN_STOCK)
BACKGROUND_INTERVAL = SETTINGS.get("background_worker_interval", 3600)

# Theme Colors
COLOR_PRIMARY = "#1e3a8a"      # Blue
COLOR_PRIMARY_DARK = "#172554" # Dark Blue
COLOR_PRIMARY_LIGHT = "#3b82f6" # Light Blue
COLOR_SECONDARY = "#475569"    # Gray
COLOR_SECONDARY_DARK = "#334155" # Dark Gray
COLOR_SUCCESS = "#16a34a"      # Green
COLOR_SUCCESS_DARK = "#047857" # Green Dark
COLOR_WARNING = "#d97706"      # Orange
COLOR_WARNING_DARK = "#b45309" # Orange Dark
COLOR_DANGER = "#dc2626"       # Red
COLOR_DANGER_DARK = "#b91c1c"  # Dark Red
COLOR_INFO = "#0369a1"         # Light Blue
COLOR_DEBT = "#c2410c"         # Orange Red
COLOR_DEBT_WORDS = "#b45309"   # Dark Orange

FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_ITALIC = ("Segoe UI", 9, "italic")
