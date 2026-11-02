# Kịch bản: Thêm mặt hàng mới vào danh sách Mặt hàng

- **Mã chức năng:** UC-THem-MH
- **Tác nhân chính:** Nhân viên
- **Điều kiện trước:**
  - Nhân viên đã đăng nhập vào hệ thống QLBH
  - Nhân viên có quyền cập nhật danh sách Mặt hàng

## Luồng sự kiện chính

| Bước | Hành động |
|---:|---|
| 1 | Nhân viên chọn chức năng Cập nhật danh sách Mặt hàng. |
| 2 | Hệ thống hiển thị danh sách Mặt hàng hiện có. |
| 3 | Nhân viên chọn Thêm mặt hàng mới. |
| 4 | Hệ thống hiển thị form nhập thông tin mặt hàng. |
| 5 | Nhân viên nhập mã, tên, đơn vị tính, giá bán và tồn kho ban đầu. |
| 6 | Nhân viên xác nhận lưu mặt hàng mới. |
| 7 | Hệ thống kiểm tra dữ liệu nhập và mã mặt hàng chưa tồn tại. |
| 8 | Hệ thống lưu mặt hàng mới và cập nhật danh sách. |
| 9 | Hệ thống hiển thị thông báo thêm mặt hàng thành công. |

**Điều kiện sau:**

- Mặt hàng mới được lưu vào danh sách Mặt hàng
- Dữ liệu nhập không hợp lệ không được lưu
- Nhật ký cập nhật hệ thống được ghi lại

## Luồng thay thế / ngoại lệ

### Dữ liệu nhập không hợp lệ

1. Tại bước 7, hệ thống phát hiện dữ liệu bắt buộc thiếu hoặc giá trị không hợp lệ.
2. Hệ thống hiển thị thông báo lỗi và yêu cầu nhập lại.
3. Quay lại bước 5.

### Mã mặt hàng đã tồn tại

1. Tại bước 7, hệ thống phát hiện mã mặt hàng đã tồn tại.
2. Hệ thống hiển thị thông báo trùng mã và không lưu bản ghi mới.
3. Quay lại bước 5.

### Nhân viên không có quyền

1. Tại bước 1, hệ thống xác nhận nhân viên không có quyền cập nhật.
2. Hệ thống hiển thị thông báo không có quyền và kết thúc use case.

