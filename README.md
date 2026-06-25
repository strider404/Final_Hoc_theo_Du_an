# Cinemax - Hệ Thống Quản Lý & Đặt Vé Rạp Phim

Cinemax là một ứng dụng web mô phỏng hệ thống rạp chiếu phim. Ứng dụng cung cấp luồng đặt vé cho khách hàng và một hệ thống quản trị nội dung (CMS) tích hợp sẵn trên Frontend dành riêng cho ban quản lý.

## 🚀 Tính năng nổi bật

* **Trải nghiệm Người dùng (Khách hàng):**
    * Giao diện Dark Mode đồng bộ, Responsive bằng Bootstrap 5.
    * Danh sách phim hiển thị chuẩn xác với poster lưu trữ nội bộ.
    * Hệ thống chọn ghế trực quan, khóa ghế tự động dựa trên giao dịch thực tế (ngăn chặn chọn trùng).
    * Trang cá nhân quản lý thông tin và lịch sử vé đặt.
* **Hệ thống Quản trị (CMS Dashboard):**
    * Thống kê trực quan: Doanh thu, số lượng vé bán ra, và tổng số phim.
    * Quản lý khách hàng: Phân quyền Admin, kích hoạt/vô hiệu hóa tài khoản trực tiếp trên giao diện.
    * Quản lý vé: Theo dõi trạng thái đặt vé, thay đổi trạng thái linh hoạt (Confirmed/Cancelled).
    * Quản lý phim: Chỉnh sửa thông tin phim thông qua lối tắt Frontend nhanh chóng.
* **Kiến trúc Triển khai (DevOps):**
    * Đóng gói hoàn toàn độc lập bằng Docker (Containerization).
    * Tự động khởi tạo cơ sở dữ liệu và tài khoản Admin mặc định khi chạy (Entrypoint).
    * Hoạt động Offline 100% (Hình ảnh và DB đã được tích hợp cứng vào Image, không phụ thuộc mạng lưới API bên ngoài).

## 🛠 Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.13
* **Backend Framework:** Django
* **Frontend:** HTML/Jinja, CSS, Bootstrap 5
* **Cơ sở dữ liệu:** SQLite 
* **Triển khai:** Docker, Docker Compose

## ⚙️ Hướng dẫn cài đặt và khởi chạy

Dự án đã được đóng băng trạng thái chuẩn nhất với toàn bộ dữ liệu (15 bộ phim, ảnh poster chất lượng cao) và không yêu cầu cấu hình môi trường máy chủ phức tạp.

### 1. Khởi chạy hệ thống bằng Docker
Đảm bảo máy tính đã cài đặt Docker. Mở terminal tại thư mục gốc của dự án và chạy lệnh sau để build và chạy ngầm (detached mode):

```bash
docker compose up --build -d
```

### 2. Truy cập ứng dụng
* **Trang chủ:** `http://127.0.0.1:8000/`
* **Tài khoản Quản trị mặc định (Tự động cấp bởi Docker):**
    * Username: `admin`
    * Password: `admin1234`

*(Lưu ý: Đăng nhập bằng tài khoản Admin, sau đó click vào tên tài khoản ở góc phải trên cùng -> Chọn "Dashboard Quản trị" để vào không gian điều khiển).*

### 3. Tắt ứng dụng

```bash
docker compose down
```
