# 🏗️ PHẦN MỀM BÃI VẬT LIỆU XÂY DỰNG THỐNG NHẤT (TÂN PHƯỚC)

Ứng dụng Desktop chạy nội bộ dành riêng cho **Bãi Cát Đá VLXD Thống Nhất**, xây dựng theo chuẩn kiến trúc **MVC (Model - View - Controller)** bằng Python + SQLite.

## 🌟 Tính Năng Nổi Bật

1. 🛒 **Tạo Đơn Hàng & Máy Tính Khối Lượng:**
   - Tự động áp dụng công thức đặc thù: `Số khối/chuyến x Số chuyến = Tổng m³` (vd: 2.2 m³ x 8 chuyến = 17.6 m³ đá 0x4).
   - Tự động cộng cước vận chuyển xe và tính dư nợ khách hàng.
2. 📦 **Quản Lý Kho VLXD:**
   - Theo dõi tồn kho các loại cát vàng, cát xây, đá 0x4, đá 1x2 xanh, đá mi, xi măng, gạch, sắt...
   - Cảnh báo màu đỏ khi vật tư dưới ngưỡng tối thiểu.
   - Nhập hàng từ mỏ để tăng kho.
3. 🚚 **Điều Phối Xe & Lương Chuyến Tài Xế:**
   - Theo dõi đội xe, đếm số chuyến chạy trong ngày (06:00 - 18:00).
   - Tự động tính tổng tiền thù lao chuyến cho tài xế và định mức xăng dầu.
4. 💳 **Công Nợ Nhà Thầu & Thu Chi:**
   - Quản lý sổ nợ, hạn mức cho nợ của nhà thầu/công trình.
   - Lập phiếu thu tiền nợ.
5. 👥 **Hồ Sơ Khách Hàng & Nhà Thầu:**
   - Lưu thông tin liên lạc, lịch sử mua hàng để áp dụng chiết khấu/giá sỉ.

---

## 🚀 Hướng Dẫn Sử Dụng

### ⚡ Khởi chạy chế độ Lập Trình (Auto-Reload khi sửa code):
Mỗi khi bạn sửa bất kỳ dòng code nào và nhấn `Ctrl + S`, phần mềm sẽ **tự động tắt và bật lại giao diện mới** trong 0.5 giây:
```bash
python dev_run.py
```

### Khởi chạy ứng dụng bình thường:
```bash
python main.py
```

### Đóng gói thành file `.exe` cài đặt cho máy tính công ty:
```bash
python build_exe.py
```
File cài đặt sẽ được tạo ra tại: `dist/VLXD_ThongNhat/VLXD_ThongNhat.exe`.
