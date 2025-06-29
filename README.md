# Hasaki Product Crawler

Dự án thu thập dữ liệu sản phẩm từ website Hasaki.vn và lưu trữ vào MongoDB.

## Mô tả

Đây là một hệ thống crawler tự động thu thập thông tin sản phẩm từ trang web Hasaki.vn, bao gồm:
- Thu thập danh sách sản phẩm từ các trang danh mục
- Lấy thông tin chi tiết sản phẩm thông qua API
- Lưu trữ dữ liệu vào MongoDB

## Cấu trúc dự án

```
crawler_hasaki/
├── crawler/                    # Module crawler chính
│   ├── crawl_product_API.py   # Thu thập chi tiết sản phẩm qua API
│   └── crawl_product.py       # Thu thập sản phẩm cơ bản
├── web_scraper/               # Module web scraping
│   ├── get_number_of_pages.py # Tính toán số trang cần crawl
│   ├── product_scraper.py     # Scraper chính cho sản phẩm
│   └── product_scraper_multiprocessing.py # Scraper đa luồng
├── mongodb_sever/             # Module kết nối MongoDB
│   └── insert_list_products.py # Chèn dữ liệu vào MongoDB
├── main.py                    # File chính để chạy crawler
├── requirements.txt           # Danh sách thư viện cần thiết
├── .env                       # File cấu hình môi trường (không commit)
└── .gitignore                 # Danh sách file/folder bỏ qua khi commit
```

## Tính năng

- **Thu thập danh sách sản phẩm**: Scrape thông tin cơ bản từ các trang danh mục
- **Thu thập chi tiết sản phẩm**: Gọi API để lấy thông tin chi tiết
- **Lưu trữ MongoDB**: Tự động lưu dữ liệu vào 2 collection:
  - `products`: Danh sách sản phẩm cơ bản
  - `product_detail`: Thông tin chi tiết sản phẩm
- **Xử lý đa luồng**: Hỗ trợ crawl song song để tăng tốc độ
- **Xử lý lỗi**: Tự động retry và xử lý các lỗi kết nối

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd crawler_hasaki
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Cấu hình môi trường:
   - Tạo file `.env` từ template `.env.example` (nếu có)
   - Hoặc cập nhật file `.env` với thông tin MongoDB của bạn:
   ```env
   MONGODB_USERNAME=your_username
   MONGODB_PASSWORD=your_password
   MONGODB_HOST=your_host
   MONGODB_PORT=27017
   MONGODB_AUTH_SOURCE=admin
   MONGODB_DATABASE=hasaki_db
   MONGODB_URI=mongodb://your_username:your_password@your_host:27017/?authSource=admin
   ```
   - Đảm bảo MongoDB server đang chạy

## Sử dụng

Chạy crawler:
```bash
python main.py
```

Quá trình sẽ thực hiện theo các bước:
1. Kết nối đến MongoDB
2. Phân tích danh mục và tạo URL
3. Thu thập danh sách sản phẩm
4. Lưu vào collection `products`
5. Gọi API để lấy chi tiết sản phẩm
6. Lưu vào collection `product_detail`

## Thư viện sử dụng

- **beautifulsoup4**: Parse HTML
- **selenium**: Automation browser (nếu cần)
- **selenium-stealth**: Tránh detection
- **pymongo**: Kết nối MongoDB
- **requests**: HTTP requests
- **urllib3**: URL utilities
- **python-dotenv**: Quản lý biến môi trường từ file .env

## Cấu hình

### MongoDB
Thông tin kết nối MongoDB được lưu trong file `.env` để bảo mật:
```env
# Cấu hình MongoDB
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_secure_password
MONGODB_HOST=20.2.235.19
MONGODB_PORT=27017
MONGODB_AUTH_SOURCE=admin
MONGODB_DATABASE=hasaki_db

# Connection string đầy đủ
MONGODB_URI=mongodb://admin:your_secure_password@20.2.235.19:27017/?authSource=admin
```

**Lưu ý bảo mật:**
- File `.env` chứa thông tin nhạy cảm và đã được thêm vào `.gitignore`
- Không commit file `.env` lên repository
- Thay đổi mật khẩu mặc định trước khi sử dụng

### Target URL
Mặc định crawler sẽ thu thập từ danh mục "Sức khỏe làm đẹp":
```python
base_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?p="
category_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html"
```

## Lưu ý

- Crawler được thiết kế để tôn trọng server bằng cách thêm delay giữa các request
- Sử dụng User-Agent để tránh bị block
- Tự động xử lý các trường hợp lỗi kết nối
- Hỗ trợ resume từ điểm dừng (kiểm tra collection đã tồn tại)

## Troubleshooting

### Lỗi kết nối MongoDB
```
ValueError: MONGODB_URI không được tìm thấy trong file .env
```
**Giải pháp:** Kiểm tra file `.env` đã được tạo và chứa biến `MONGODB_URI`

### Lỗi import dotenv
```
ModuleNotFoundError: No module named 'dotenv'
```
**Giải pháp:** Cài đặt thư viện python-dotenv:
```bash
pip install python-dotenv
```

### Lỗi kết nối MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**Giải pháp:** 
- Kiểm tra MongoDB server đang chạy
- Kiểm tra thông tin kết nối trong file `.env`
- Kiểm tra firewall và network connectivity

### File .env không được load
**Giải pháp:**
- Đảm bảo file `.env` nằm trong thư mục gốc của project
- Kiểm tra tên file chính xác là `.env` (không có extension)
- Kiểm tra quyền đọc file

## Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

