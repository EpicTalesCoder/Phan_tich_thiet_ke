# Phan_tich_thiet_ke — QLBH Diagram Tools

Bộ công cụ sinh tự động biểu đồ UML cho bài tập môn **Phân tích Thiết kế Hệ thống** (đề quản lý bán hàng siêu thị — QLBH): biểu đồ được định nghĩa bằng JSON, tool sinh nguồn PlantUML/Markdown và render PNG theo phong cách biểu đồ vẽ trong **Visual Paradigm** (nền trắng, viền/mũi tên đen, Arial, đường vuông góc `ortho` cho biểu đồ lớp/trạng thái).

Render chạy hoàn toàn trên **GitHub Actions** — không cần cài Java/PlantUML trên máy.

## Kết cấu

```
qldbh_diagram_tools/
├── ai_tools/            # manual + JSON schema cho AI đọc
├── bin/qldbh-diagrams   # CLI entrypoint
├── definitions/         # exam_diagrams.json — nguồn chân lý của toàn bộ biểu đồ
├── qldbh_diagrams/      # mã Python: cli.py, generator.py, validate.py
├── output/              # PNG + .puml do CI render (không sửa tay)
└── vendor/              # plantuml.jar (gitignored, CI tự tải)
```

## Bộ biểu đồ bài QLBH (10 định nghĩa)

| ID | Loại | Nội dung |
|---|---|---|
| `UC01_QLBH_TongQuan` | Use case | 3 tác nhân (Nhân viên, Khách hàng, Hệ thống thanh toán), 10 use case, quan hệ include (Đăng nhập, Cập nhật Mặt hàng, Tạo hóa đơn, Thanh toán) |
| `SC_UC01_ThemMatHang` | Kịch bản use case | Thêm mặt hàng mới — 9 bước chính, 3 luồng thay thế (dữ liệu lỗi, trùng mã, không đủ quyền) |
| `SC_UC02_BanHangTrucTiep` | Kịch bản use case | Bán hàng trực tiếp — 9 bước chính, 3 luồng thay thế (hết tồn kho, thành viên, thanh toán thất bại) |
| `CD01_LopPhanTich_ThucThe` | Lớp phân tích | 7 lớp thực thể: NhanVien, KhachHang, MatHang, HoaDon, ChiTietHoaDon, DonHangOnline, DangKyThanhVien — kèm đa lượng, cấu tạo (HoaDon ◆— ChiTietHoaDon), kết tập |
| `CD02_LopThietKe_Bien_DieuKhien` | Lớp thiết kế | 11 lớp Entity–Boundary–Control, đúng mô hình 3 lớp của ICONIX/RUP |
| `SQ01_ThemMatHang` | Tuần tự | Thêm mặt hàng: NV → boundary → control → entity, 10 thông điệp có đánh số |
| `SQ02_BanHangTrucTiep` | Tuần tự | Bán hàng: tạo phiên → quét hàng → kiểm tồn → tạo chi tiết → thanh toán → giảm tồn kho (16 thông điệp) |
| `AC01_ThemMatHang` | Hoạt động | Swimlane Nhân viên / Hệ thống: kiểm quyền → nhập liệu → kiểm tra dữ liệu + trùng mã → lưu, 4 điểm kết thúc |
| `AC02_BanHangTrucTiep` | Hoạt động | Vòng lặp quét hàng (repeat/while), nhánh đủ/thiếu tồn kho, nhánh thanh toán thành công/thất bại |
| `ST01_TrangThaiDonHangOnline` | Trạng thái | Chờ duyệt → Đã duyệt → Đang giao → Hoàn thành; 2 nhánh Đã hủy (từ Chờ duyệt/Đã duyệt) có guard |

Ảnh render: [`qldbh_diagram_tools/output/`](qldbh_diagram_tools/output/) — nguồn `.puml`: [`output/sources/`](qldbh_diagram_tools/output/sources/).

## Cách render (không cần cài gì trên máy)

Render tự chạy khi push thay đổi vào `definitions/`, `qldbh_diagrams/` hoặc workflow. Xem tiến độ ở tab **Actions**, kết quả PNG được bot commit lại vào `output/` (và kèm artifact mỗi lần chạy).

Sửa biểu đồ = sửa JSON:

1. Mở `qldbh_diagram_tools/definitions/exam_diagrams.json` trên GitHub → bút chì (Edit).
2. Sửa `data` của biểu đồ tương ứng (thêm use case / lớp / thông điệp...).
3. Commit → đợi Actions chạy xanh (~1.5 phút) → lấy PNG mới trong `output/`.

Thêm biểu đồ mới: copy 1 object trong JSON, đổi `id`/`title`/`data`. Các loại được hỗ trợ: `use_case`, `class`, `sequence`, `activity`, `state`, `use_case_scenario` — schema đầy đủ trong [`ai_tools/diagram_tool_schema.json`](qldbh_diagram_tools/ai_tools/diagram_tool_schema.json).

## Chạy tay (tùy chọn, khi cần)

```bash
qldbh_diagram_tools/bin/qldbh-diagrams validate  qldbh_diagram_tools/definitions/exam_diagrams.json
qldbh_diagram_tools/bin/qldbh-diagrams generate  qldbh_diagram_tools/definitions/exam_diagrams.json --out-dir /tmp/src --style vp
qldbh_diagram_tools/bin/qldbh-diagrams render    qldbh_diagram_tools/definitions/exam_diagrams.json --out-dir qldbh_diagram_tools/output --style vp --engine dot
```

- `--style vp` (mặc định): phong cách Visual Paradigm; `--style plain`: mặc định PlantUML.
- `--engine smetana` (mặc định): không cần Graphviz; `--engine dot`: cần `dot`, layout đẹp hơn cho use case/trạng thái. Tuần tự và hoạt động không phụ thuộc engine.
- Render cần Java + `plantuml.jar` tại `qldbh_diagram_tools/vendor/plantuml.jar`.

Hướng dẫn đầy đủ cho AI: [`ai_tools/AI_TOOL_MANUAL.md`](qldbh_diagram_tools/ai_tools/AI_TOOL_MANUAL.md).
