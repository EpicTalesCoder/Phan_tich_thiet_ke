# BÁO CÁO PHÂN TÍCH THIẾT KẾ HỆ THỐNG
## Hệ thống Quản lý Bán hàng Siêu thị (QLBH)

---

## 1. Tổng quan bài toán

Hệ thống QLBH hỗ trợ công việc bán hàng hằng ngày của một siêu thị: quản lý danh mục mặt hàng, bán hàng trực tiếp tại quầy, bán hàng online và quản lý đăng ký thành viên. Hệ thống có ba tác nhân chính:

- **Nhân viên** — đăng nhập, cập nhật danh mục mặt hàng (thêm/xóa/sửa), trực tiếp thực hiện phiên bán hàng tại quầy.
- **Khách hàng** — đăng ký thành viên, đặt mua hàng online.
- **Hệ thống thanh toán** — tác nhân hệ thống ngoài, xử lý giao dịch thanh toán.

Bài phân tích đi theo trình độ chuẩn: **Use case → Kịch bản → Lớp phân tích → Lớp thiết kế (E-B-C) → Tuần tự → Hoạt động → Trạng thái**.

---

## 2. Xác định yêu cầu — Biểu đồ Use Case tổng quát

*(UC01_QLBH_TongQuan)*

10 use case được nhóm theo chức năng:

| Nhóm | Use case | Quan hệ include |
|---|---|---|
| Quản lý danh mục | Cập nhật danh sách Mặt hàng; Thêm mặt hàng mới; Xóa mặt hàng; Sửa thông tin mặt hàng | Thêm/Xóa/Sửa → include → Cập nhật danh sách; Cập nhật danh sách → include → Đăng nhập |
| Bán hàng tại quầy | Bán hàng trực tiếp tại siêu thị; Tạo hóa đơn bán hàng; Thanh toán | Bán hàng → include → Tạo hóa đơn → include → Thanh toán; Bán hàng → include → Đăng nhập |
| Khách hàng online | Đăng ký thành viên; Đặt mua hàng online | Cả hai → include → Đăng nhập; Đặt mua online → include → Thanh toán |

Điểm thiết kế chính: **Đăng nhập** và **Thanh toán** là use case dùng chung, được tái sử dụng bằng quan hệ `<<include>>` thay vì lặp lại trong từng luồng. Ghi chú trên biểu đồ: Đăng nhập là yêu cầu chung của nhân viên và khách hàng khi truy nhập hệ thống.

---

## 3. Kịch bản use case

Hai use case trọng tâm được đặc tả chi tiết thành bảng kịch bản (bước chính + điều kiện trước/sau + luồng thay thế):

### 3.1 SC_UC01 — Thêm mặt hàng mới

- **Tác nhân chính:** Nhân viên.
- **Điều kiện trước:** đã đăng nhập; có quyền cập nhật danh sách Mặt hàng.
- **Luồng chính (9 bước):** chọn cập nhật danh sách → xem danh sách hiện có → chọn thêm mới → nhập form (mã, tên, đơn vị tính, giá bán, tồn kho) → hệ thống kiểm tra dữ liệu + trùng mã → lưu → cập nhật danh sách → thông báo thành công.
- **Luồng thay thế:** (1) dữ liệu bắt buộc thiếu/không hợp lệ — báo lỗi, nhập lại; (2) mã mặt hàng đã tồn tại — không lưu, nhập lại; (3) không có quyền — kết thúc use case.
- **Điều kiện sau:** mặt hàng mới nằm trong danh sách; dữ liệu lỗi không được lưu; nhật ký hệ thống được ghi.

### 3.2 SC_UC02 — Bán hàng trực tiếp tại siêu thị

- **Tác nhân chính:** Nhân viên.
- **Điều kiện trước:** đã đăng nhập; có quyền bán hàng; còn ít nhất một mặt hàng đang kinh doanh.
- **Luồng chính (9 bước):** tạo phiên bán → quét/chọn mặt hàng → kiểm tra tồn kho → thêm chi tiết + cập nhật tạm tính → lặp lại cho các mặt hàng khác → tính tổng → xác nhận khách hàng + hình thức thanh toán → xác nhận thanh toán thành công → lưu hóa đơn, cập nhật tồn kho, in hóa đơn.
- **Luồng thay thế:** (1) không đủ tồn kho — giảm số lượng hoặc bỏ khỏi giỏ; (2) khách là thành viên — áp dụng ưu đãi, cập nhật tổng tiền; (3) thanh toán thất bại — thử hình thức khác hoặc hủy phiên.
- **Điều kiện sau:** hóa đơn được lưu khi giao dịch thành công; tồn kho trừ đúng số lượng bán; hóa đơn in/gửi khách.

---

## 4. Phân tích — Biểu đồ lớp thực thể

*(CD01_LopPhanTich_ThucThe)*

Bảy lớp thực thể cốt lõi:

| Lớp | Thuộc tính chính | Trách nhiệm |
|---|---|---|
| `NhanVien` | maNhanVien, hoTen, vaiTro | đăng nhập, kiểm tra quyền cập nhật/bán hàng |
| `KhachHang` | maKhachHang, hoTen, soDienThoai, email, laThanhVien | đăng ký thành viên, đặt hàng online |
| `MatHang` | maMatHang, tenMatHang, donViTinh, giaBan, tonKho | thêm/xóa/sửa, kiểm tra và giảm tồn kho |
| `HoaDon` | maHoaDon, ngayLap, loaiBan, tongTien | thêm chi tiết, tính tổng, lưu, in |
| `ChiTietHoaDon` | maChiTiet, soLuong, donGiaBan, thanhTien | tính thành tiền của từng dòng bán |
| `DonHangOnline` | maDonHang, ngayDat, diaChiGiaoHang, trangThai | xác nhận đơn, cập nhật trạng thái |
| `DangKyThanhVien` | maDangKy, ngayDangKy, trangThai | xác nhận/từ chối đăng ký |

Các quan hệ chính:

- `HoaDon` **cấu tạo** (composition, 1 → 1..*) `ChiTietHoaDon` — chi tiết hóa đơn không tồn tại độc lập ngoài hóa đơn.
- `HoaDon` **kết tập** (aggregation, 0..* → 0..1) `DonHangOnline` — hóa đơn có thể phát sinh từ một đơn online.
- `NhanVien` cập nhật `MatHang` (1 → 0..*), `NhanVien` lập `HoaDon` (1 → 0..*).
- `KhachHang` đặt `DonHangOnline` (1 → 0..*), đăng ký `DangKyThanhVien` (1 → 0..*).
- `MatHang` được bán trong `ChiTietHoaDon` (1 → 0..*).

---

## 5. Thiết kế — Biểu đồ lớp Entity–Boundary–Control

*(CD02_LopThietKe_Bien_DieuKhien)*

Áp dụng mẫu kiến trúc 3 lớp (E-B-C) cho luồng thêm mặt hàng, bán hàng và đăng nhập — 11 lớp:

| Tầng | Lớp | Vai trò |
|---|---|---|
| Boundary | `UCQuanLyMatHang`, `UCBanHang`, `UCDangNhap` | giao diện: hiển thị danh sách/form/giỏ hàng, nhận input, hiển thị thông báo |
| Control | `CTLQuanLyMatHang`, `CTLBanHang`, `CTLDangNhap` | nghiệp vụ: kiểm quyền, kiểm tra dữ liệu/trùng mã, tạo phiên bán, kiểm tồn, tính tiền, tạo/lưu hóa đơn |
| Entity | `NhanVien`, `KhachHang`, `MatHang`, `HoaDon`, `ChiTietHoaDon` | dữ liệu + thao tác dữ liệu như mục 4 |

Luồng điều khiển: Boundary **gửi yêu cầu** → Control xử lý nghiệp vụ và **dependency** xuống Entity (quản lý/tra cứu/kiểm tra/tạo-lưu). `HoaDon` cấu tạo `ChiTietHoaDon` giữ nguyên từ bước phân tích.

---

## 6. Biểu đồ tuần tự

### 6.1 SQ01 — Thêm mặt hàng mới (10 thông điệp)

`Nhân viên → UCQuanLyMatHang → CTLQuanLyMatHang → MatHang`

1. NV chọn "Thêm mặt hàng mới" → UI hiển thị form → NV nhập mã/tên/giá/tồn kho.
2. UI gọi `guiYeuCauThemMatHang(thongTin)` → Control gọi `kiemTraMaMatHang(maMatHang)` → Entity trả kết quả trùng mã.
3. Control gọi `themMoi(thongTin)` → Entity xác nhận lưu thành công.
4. Control bảo UI cập nhật danh sách → UI hiển thị thông báo thành công.

### 6.2 SQ02 — Bán hàng trực tiếp (16 thông điệp)

`Nhân viên → UCBanHang → CTLBanHang → {MatHang, HoaDon, ChiTietHoaDon}`

1. Tạo phiên bán: `taoPhienBanHang()`.
2. Mỗi mặt hàng: `themMatHang(maMatHang, soLuong)` → `kiemTraTonKho(soLuong)` → `taoChiTietHoaDon(soLuong, donGia)` → `themChiTiet(chiTiet)` → UI cập nhật tổng tiền tạm tính.
3. Thanh toán: `xacNhanThanhToan()` → Control `tinhTongTien(); luuHoaDon()` lên `HoaDon` và `giamTonKho()` lên `MatHang` → trả kết quả giao dịch → UI hiển thị và in hóa đơn.

Hai biểu đồ tuần tự minh họa đúng phân vai E-B-C: boundary chỉ nói chuyện với control, control điều phối entity, không có gọi chéo.

---

## 7. Biểu đồ hoạt động

### 7.1 AC01 — Thêm mặt hàng mới (2 swimlane: Nhân viên / Hệ thống QLBH)

Đăng nhập → chọn cập nhật danh sách → **[Có quyền cập nhật?]** — không quyền → thông báo, kết thúc. Có quyền → hiển thị form → NV nhập thông tin → **[Dữ liệu hợp lệ?]** — lỗi → hiển thị lỗi, kết thúc. Hợp lệ → **[Mã mặt hàng chưa tồn tại?]** — trùng → báo lỗi, kết thúc. Chưa trùng → lưu vào danh sách → cập nhật giao diện → thông báo thành công.

### 7.2 AC02 — Bán hàng trực tiếp

Đăng nhập → tạo phiên bán → **vòng lặp repeat**: quét/chọn mặt hàng → **[Đủ tồn kho?]** — đủ: thêm chi tiết + cập nhật tạm tính; thiếu: cảnh báo → lặp khi "Khách còn chọn mặt hàng". Sau vòng lặp: xác nhận khách hàng + hình thức thanh toán → tính tổng → thực hiện thanh toán → **[Thanh toán thành công?]** — thành công: lưu hóa đơn, cập nhật tồn kho, in hóa đơn; thất bại: hiển thị lỗi cho phép thử lại.

---

## 8. Biểu đồ trạng thái — Đơn hàng online

*(ST01_TrangThaiDonHangOnline)*

```
● → Chờ duyệt → Đã duyệt → Đang giao → Hoàn thành ◉
      │             │
      │ hủy đơn     │ hủy đơn [chưa bắt đầu giao hàng]
      │ [khách hủy  │
      │  hoặc hết   │
      │  hàng]      │
      ▼             ▼
    Đã hủy ◉ ◄─────┘
```

- **Chờ duyệt → Đã duyệt:** hệ thống xác nhận đơn.
- **Đã duyệt → Đang giao:** bắt đầu giao hàng.
- **Đang giao → Hoàn thành:** khách nhận hàng.
- **Hủy:** chỉ được hủy trước khi bắt đầu giao — từ Chờ duyệt (khách hủy hoặc hàng không còn) và từ Đã duyệt (chưa bắt đầu giao hàng). Sau khi đang giao, đơn không thể hủy.

---

## 9. Công cụ thực hiện

Toàn bộ biểu đồ trong báo cáo được sinh từ định nghĩa JSON bằng công cụ `qldbh_diagram_tools` trong repo này (chi tiết kỹ thuật xem [README](README.md)):

1. Định nghĩa biểu đồ bằng JSON có schema (`ai_tools/diagram_tool_schema.json`) — nguồn duy nhất, sửa một chỗ là regenerate được toàn bộ.
2. Tool validate cấu trúc, sinh nguồn PlantUML (biểu đồ) và Markdown (kịch bản) với phong cách Visual Paradigm.
3. GitHub Actions tự render PNG mỗi khi định nghĩa thay đổi — quy trình lặp lại được, không vẽ tay, không lệch ký hiệu giữa các biểu đồ.

---

## 10. Danh mục sản phẩm

| Sản phẩm | Vị trí |
|---|---|
| Biểu đồ use case tổng quát | `output/UC01_QLBH_TongQuan.png` |
| Kịch bản use case (2) | `output/sources/SC_UC01_ThemMatHang.md`, `SC_UC02_BanHangTrucTiep.md` |
| Biểu đồ lớp phân tích | `output/CD01_LopPhanTich_ThucThe.png` |
| Biểu đồ lớp thiết kế E-B-C | `output/CD02_LopThietKe_Bien_DieuKhien.png` |
| Biểu đồ tuần tự (2) | `output/SQ01_ThemMatHang.png`, `SQ02_BanHangTrucTiep.png` |
| Biểu đồ hoạt động (2) | `output/AC01_ThemMatHang.png`, `AC02_BanHangTrucTiep.png` |
| Biểu đồ trạng thái | `output/ST01_TrangThaiDonHangOnline.png` |
