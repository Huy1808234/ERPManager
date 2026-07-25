import xml.etree.ElementTree as ET
import os

def parse_einvoice_xml(file_path):
    """
    Giả lập đọc file XML hóa đơn điện tử.
    Bóc tách các thông tin: Mã số thuế, Tiền trước thuế, Thuế suất VAT, Tổng tiền.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Hàm tiện ích để tìm tag không phân biệt namespace
        def find_text(tag_name, default=""):
            for elem in root.iter():
                if tag_name.lower() in elem.tag.lower():
                    return elem.text
            return default

        tax_code = find_text("MaSoThue", "0312345678")
        total_before = find_text("TongTienTruocThue", "10000000")
        vat_rate = find_text("ThueSuat", "10")
        total_amount = find_text("TongTienThanhToan", "11000000")
        
        # Chuẩn hóa dữ liệu
        try:
            total_before = float(total_before.replace(',', ''))
            vat_rate = float(vat_rate.replace('%', ''))
            total_amount = float(total_amount.replace(',', ''))
        except (ValueError, AttributeError):
            total_before, vat_rate, total_amount = 0.0, 10.0, 0.0

        return {
            "filename": os.path.basename(file_path),
            "tax_code": tax_code,
            "total_before_tax": total_before,
            "vat_rate": vat_rate,
            "total_amount": total_amount,
            "status": "Hợp lệ"
        }
    except Exception as e:
        return {
            "filename": os.path.basename(file_path),
            "tax_code": "N/A",
            "total_before_tax": 0.0,
            "vat_rate": 0.0,
            "total_amount": 0.0,
            "status": f"Lỗi: {str(e)}"
        }

def process_bulk_xml(file_paths):
    """
    Xử lý hàng loạt danh sách các file XML.
    Trả về danh sách các dict chứa dữ liệu đã parse.
    """
    results = []
    for path in file_paths:
        if path.lower().endswith('.xml'):
            data = parse_einvoice_xml(path)
            results.append(data)
    return results
