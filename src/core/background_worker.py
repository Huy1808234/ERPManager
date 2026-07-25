import threading
import time
from plyer import notification
from dao import invoice_dao
from core.logger import get_logger

logger = get_logger()

class BackgroundWorker:
    def __init__(self, check_interval=3600):
        self.check_interval = check_interval
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("BackgroundWorker started.")

    def stop(self):
        self.running = False
        logger.info("BackgroundWorker stopped.")

    def _run(self):
        # Bắn ngay 1 thông báo demo khi vừa khởi động (sau 3 giây)
        time.sleep(3)
        self.check_vat_thresholds()
        
        while self.running:
            # Sleep in chunks to allow quick stopping
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
            
            if self.running:
                try:
                    self.check_vat_thresholds()
                except Exception as e:
                    logger.error(f"BackgroundWorker error: {e}")

    def check_vat_thresholds(self):
        try:
            summary = invoice_dao.get_tax_summary()
            warnings = []
            for row in summary:
                if row['diff'] < 0:
                    warnings.append(row['product_name'])
                    
            if warnings:
                items_str = ", ".join(warnings)
                logger.warning(f"VAT threshold exceeded for: {items_str}")
                notification.notify(
                    title="Cảnh báo Thuế Đầu Ra!",
                    message=f"VAT đầu ra đang vượt hóa đơn đầu vào cho: {items_str}.",
                    app_name="VLXD Thống Nhất",
                    timeout=10
                )
        except Exception as e:
            logger.error(f"Lỗi khi quét VAT: {e}")
