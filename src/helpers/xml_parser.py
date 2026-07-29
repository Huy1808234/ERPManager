import xml.etree.ElementTree as ET
import os

def parse_einvoice_xml(file_path):
    """
    Giả lập đọc file XML/PDF hóa đơn điện tử.
    Bóc tách các thông tin: Mã số thuế, Tiền trước thuế, Thuế suất VAT, Tổng tiền.
    """
    try:
        if file_path.lower().endswith('.xml'):
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Hàm tiện ích để tìm tag không phân biệt namespace
            def find_text(tag_name, default=""):
                for elem in root.iter():
                    if tag_name.lower() in elem.tag.lower():
                        return elem.text
                return default

            invoice_no = find_text("SoHoaDon", "00000000")
            invoice_date = find_text("NgayLap", "2026-06-01")
            tax_code = find_text("MaSoThue", "0312345678")
            total_before = find_text("TongTienTruocThue", "10000000")
            vat_rate = find_text("ThueSuat", "10")
            total_amount = find_text("TongTienThanhToan", "11000000")
        elif file_path.lower().endswith('.pdf'):
            try:
                import fitz
                import re
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                match_inv = re.search(r'Số[^:]*:\s*(\d+)', text, re.IGNORECASE)
                invoice_no = match_inv.group(1).strip() if match_inv else "N/A"

                match_date = re.search(r'Ngày.*?(\d{1,2})\s*tháng.*?(\d{1,2})\s*năm.*?(\d{4})', text, re.IGNORECASE | re.DOTALL)
                if match_date:
                    invoice_date = f"{match_date.group(3)}-{match_date.group(2).zfill(2)}-{match_date.group(1).zfill(2)}"
                else:
                    invoice_date = "N/A"

                match_tax = re.findall(r'Mã số thuế[^:]*:\s*([\d-]+)', text, re.IGNORECASE)
                if match_tax:
                    tax_code = match_tax
                else:
                    tax_code = "N/A"
                
                match_before = re.search(r'Cộng tiền hàng[^:]*:\s*([\d\.,]+)', text, re.IGNORECASE)
                total_before = match_before.group(1).strip() if match_before else "0"
                
                match_vat = re.search(r'Thuế suất GTGT[^:]*:\s*(\d+)\s*%', text, re.IGNORECASE)
                vat_rate = match_vat.group(1).strip() if match_vat else "0"
                
                match_total = re.search(r'Tổng tiền thanh toán[^:]*:\s*([\d\.,]+)', text, re.IGNORECASE)
                total_amount = match_total.group(1).strip() if match_total else "0"
                
            except ImportError:
                # Fallback if fitz is not installed
                invoice_no, invoice_date, tax_code, total_before, vat_rate, total_amount = "N/A", "N/A", "N/A", "0", "0", "0"
                raise Exception("Thiếu thư viện PyMuPDF. Hãy chạy: pip install pymupdf")
        else:
            raise ValueError("Định dạng file không hỗ trợ")

        def parse_vn_number(val_str):
            if not val_str: return 0.0
            s = str(val_str).strip()
            # Remove all characters except digits, dot and comma
            import re
            s = re.sub(r'[^\d\.,]', '', s)
            if not s: return 0.0
            
            # If both exist
            if '.' in s and ',' in s:
                if s.rfind(',') > s.rfind('.'):
                    s = s.replace('.', '').replace(',', '.')
                else:
                    s = s.replace(',', '')
            else:
                if s.count('.') > 1:
                    s = s.replace('.', '')
                elif s.count(',') > 1:
                    s = s.replace(',', '')
                elif s.count('.') == 1 and len(s.split('.')[1]) == 3:
                    s = s.replace('.', '')
                elif s.count(',') == 1 and len(s.split(',')[1]) == 3:
                    s = s.replace(',', '')
                else:
                    s = s.replace(',', '.') # Fallback
            try:
                return float(s)
            except:
                return 0.0

        total_before = parse_vn_number(total_before)
        vat_rate = parse_vn_number(str(vat_rate).replace('%', ''))
        total_amount = parse_vn_number(total_amount)

        vat_amount = (total_before * vat_rate) / 100.0 if vat_rate > 0 else (total_amount - total_before)
        if vat_amount < 0: vat_amount = 0.0

        filename = os.path.basename(file_path)
        full_text_check = (filename + " " + str(tax_code)).lower()
        if any(kw in full_text_check for kw in ["dầu", "dau", "xăng", "xang", "sửa", "sua", "nhớt", "nhot", "lốp", "lop", "bãi", "bai", "điện", "dien", "nước", "nuoc"]):
            category = "Chi phí vận hành"
        else:
            category = "Vật liệu"

        # Fallback tax code if we picked the buyer's tax code
        if isinstance(tax_code, list):
            tax_code = tax_code[0] if tax_code else "N/A"

        return {
            "filename": filename,
            "filepath": os.path.abspath(file_path),
            "invoice_no": invoice_no,
            "invoice_date": invoice_date,
            "tax_code": tax_code,
            "total_before_tax": total_before,
            "vat_rate": vat_rate,
            "vat_amount": vat_amount,
            "total_amount": total_amount,
            "category": category,
            "status": "Hợp lệ (Đã quét PDF)" if file_path.lower().endswith('.pdf') else "Hợp lệ"
        }
    except Exception as e:
        return {
            "filename": os.path.basename(file_path),
            "filepath": os.path.abspath(file_path),
            "invoice_no": "N/A",
            "invoice_date": "N/A",
            "tax_code": "N/A",
            "total_before_tax": 0.0,
            "vat_rate": 0.0,
            "total_amount": 0.0,
            "status": f"Lỗi: {str(e)}"
        }

def process_bulk_xml(file_paths):
    """
    Xử lý hàng loạt danh sách các file XML/PDF.
    Trả về danh sách các dict chứa dữ liệu đã parse.
    """
    results = []
    for path in file_paths:
        if path.lower().endswith('.xml') or path.lower().endswith('.pdf'):
            data = parse_einvoice_xml(path)
            results.append(data)
    return results
