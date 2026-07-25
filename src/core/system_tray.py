import pystray
from PIL import Image, ImageDraw
import threading

def create_image():
    # Tạo một icon đơn giản 64x64
    image = Image.new('RGB', (64, 64), color=(30, 58, 138))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
    return image

class SystemTrayApp:
    def __init__(self, root, on_show_alert_callback=None):
        self.root = root
        self.on_show_alert_callback = on_show_alert_callback
        self.icon = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("Mở phần mềm", self.on_show_app),
            pystray.MenuItem("Kiểm tra cảnh báo", self.on_check_alerts),
            pystray.MenuItem("Thoát", self.on_exit)
        )
        self.icon = pystray.Icon("VLXD", create_image(), "VLXD Thống Nhất", menu)
        
        # Pystray requires being run in a separate thread on Windows to avoid blocking tkinter
        threading.Thread(target=self.icon.run, daemon=True).start()

    def on_show_app(self, icon, item):
        self.root.after(0, self.root.deiconify)

    def on_check_alerts(self, icon, item):
        self.root.after(0, self.root.deiconify)
        if self.on_show_alert_callback:
            self.root.after(100, self.on_show_alert_callback)

    def on_exit(self, icon, item):
        self.icon.stop()
        self.root.after(0, self.root.destroy)
        
    def stop(self):
        if self.icon:
            self.icon.stop()
