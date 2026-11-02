# Kịch bản: Bán hàng trực tiếp tại siêu thị

- **Mã chức năng:** UC-BanHang-TT
- **Tác nhân chính:** Nhân viên
- **Điều kiện trước:**
  - Nhân viên đã đăng nhập vào hệ thống QLBH
  - Nhân viên có quyền bán hàng trực tiếp
  - Có ít nhất một mặt hàng đang kinh doanh

## Luồng sự kiện chính

| Bước | Hành động |
|---:|---|
| 1 | Nhân viên tạo phiên bán hàng mới. |
| 2 | Nhân viên quét mã hoặc chọn mặt hàng cần bán. |
| 3 | Hệ thống hiển thị thông tin và kiểm tra tồn kho của mặt hàng. |
| 4 | Hệ thống thêm mặt hàng vào chi tiết hóa đơn và cập nhật số tiền tạm tính. |
| 5 | Nhân viên lặp lại bước 2 đến 4 cho các mặt hàng khác. |
| 6 | Hệ thống tính tổng tiền cần thanh toán. |
| 7 | Nhân viên xác nhận thông tin khách hàng và hình thức thanh toán. |
| 8 | Hệ thống xác nhận thanh toán thành công. |
| 9 | Hệ thống lưu hóa đơn, cập nhật tồn kho và in hóa đơn. |

**Điều kiện sau:**

- Hóa đơn bán hàng được lưu khi giao dịch thành công
- Tồn kho được cập nhật theo số lượng bán
- Hóa đơn được in hoặc gửi cho khách hàng

## Luồng thay thế / ngoại lệ

### Không đủ tồn kho

1. Tại bước 3, hệ thống phát hiện số lượng bán vượt tồn kho.
2. Hệ thống hiển thị thông báo không đủ hàng.
3. Nhân viên giảm số lượng hoặc loại bỏ mặt hàng khỏi giỏ hàng.

### Khách hàng là thành viên

1. Tại bước 7, nhân viên tra cứu thông tin thành viên.
2. Hệ thống áp dụng ưu đãi tương ứng cho khách hàng.
3. Hệ thống cập nhật tổng tiền phải thanh toán.

### Thanh toán thất bại

1. Tại bước 8, hệ thống không nhận được xác nhận thanh toán.
2. Hệ thống hiển thị thông báo thanh toán thất bại.
3. Nhân viên thử lại hình thức thanh toán khác hoặc hủy phiên bán.

