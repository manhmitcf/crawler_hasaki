import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
import concurrent.futures
from urllib.parse import urljoin
from get_number_of_pages import get_number_of_pages, get_number_of_products

class ProductScraper:
    def __init__(self, base_url, output_file="products.json", number_of_products=None, number_of_pages=None, max_workers=5, timeout=30):
        """
        Khởi tạo scraper với URL cơ sở và file đầu ra
        
        Args:
            base_url (str): URL cơ sở của trang web cần thu thập
            output_file (str): Đường dẫn file JSON đầu ra
            number_of_products (int, optional): Số lượng sản phẩm
            number_of_pages (int, optional): Số trang
            max_workers (int): Số luồng tối đa chạy đồng thời
            timeout (int): Thời gian chờ tối đa cho mỗi request (giây)
        """
        self.base_url = base_url
        self.number_of_products = number_of_products
        self.number_of_pages = number_of_pages
        self.output_file = output_file
        self.max_workers = max_workers
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.products = []
        self.temp_dir = "temp_data"
        
        # Tạo thư mục tạm thời nếu chưa tồn tại
        os.makedirs(self.temp_dir, exist_ok=True)

    def generate_page_urls(self):
        """
        Tạo danh sách URLs cho tất cả các trang dựa trên số trang
        
        Returns:
            list: Danh sách URLs cho tất cả các trang
        """
        if not self.number_of_pages:
            return [self.base_url]
            
        urls = []
        for page in range(1, self.number_of_pages + 1):
            page_url = f"{self.base_url}{page}"
            urls.append(page_url)
        return urls
    
    def get_page_content(self, url):
        """
        Lấy nội dung HTML của trang web
        
        Args:
            url (str): URL của trang cần lấy nội dung
        Returns:
            BeautifulSoup: Đối tượng BeautifulSoup chứa nội dung trang
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải trang {url}: {e}")
            return None
    
    def extract_products(self, soup, product_selector, name_selector, link_selector=None):
        """
        Trích xuất thông tin sản phẩm từ nội dung HTML
        
        Args:
            soup (BeautifulSoup): Đối tượng BeautifulSoup chứa nội dung trang
            product_selector (str): CSS selector cho từng sản phẩm
            name_selector (str): CSS selector cho tên sản phẩm
            link_selector (str, optional): CSS selector cho link sản phẩm
            
        Returns:
            list: Danh sách các sản phẩm đã trích xuất
        """
        products = []
        
        for product in soup.select(product_selector):
            try:
                # Trích xuất ID sản phẩm nếu có
                product_id = ""
                id = ""
                data_product = ""
                data_id = ""
                data_name = ""
                data_category_name = ""
                data_price = ""
                data_variant = ""
                data_brand = ""
                
                if product.select_one('.block_info_item_sp'):
                    info_element = product.select_one('.block_info_item_sp')
                    id = info_element.get('id', '')
                    data_product = info_element.get('data-product', '')
                    data_id = info_element.get('data-id', '')
                    data_name = info_element.get('data-name', '')
                    data_category_name = info_element.get('data-category-name', '')
                    data_price = info_element.get('data-price', '')
                    data_variant = info_element.get('data-variant', '')
                    data_brand = info_element.get('data-brand', '')
                
                # Giá mới:
                new_price = product.select_one('.item_giamoi')
                if new_price:
                    price = new_price.get_text(strip=True)
                else:
                    price = "Không có giá mới"
                
                #Giá cũ:
                old_price = product.select_one('.item_giacu')
                if old_price:
                    old_price = old_price.get_text(strip=True)
                else:
                    old_price = "Không có giá cũ"
                
                #Giảm giá:
                discount = product.select_one('.discount_percent2_deal')
                if discount:
                    discount = discount.get_text(strip=True)
                else:
                    discount = "Không có giảm giá"
                
                # Tên Tiếng Việt:
                namevn_element = product.select_one(name_selector)
                namevn = namevn_element.get_text(strip=True) if namevn_element else "Không có tên"
                
                # Tên Tiếng Anh:
                nameen_element = product.select_one('.en_names')
                nameen = nameen_element.get_text(strip=True) if nameen_element else "Không có tên tiếng Anh"
                

                # Trích xuất link sản phẩm
                link = "Không có link"
                if link_selector:
                    link_element = product.select_one(link_selector)
                    if link_element and link_element.has_attr('href'):
                        link = urljoin("https://hasaki.vn", link_element['href'])
                
                # Trích xuất thông tin tình trạng hàng hóa nếu có
                stock_info = "Không có thông tin"
                stock_element = product.select_one('.block_info_hethang a, .block_info_hethang span')
                if stock_element:
                    stock_info = stock_element.get_text(strip=True)
                
                
                products.append({
                    'data_id': data_id,
                    'id': id,
                    'data_product': data_product,
                    'data_name': data_name,
                    'data_category_name': data_category_name,
                    'data_price': data_price,
                    'data_variant': data_variant,   
                    'data_brand': data_brand,
                    'namevn': namevn,
                    'nameen': nameen,
                    'price': price,
                    'old_price': old_price,
                    'discount': discount,
                    'link': link,
                    'stock_info': stock_info,
                })
            except Exception as e:
                print(f"Lỗi khi trích xuất sản phẩm: {e}")
                continue
        
        return products
    
    def process_url(self, url, product_selector, name_selector, link_selector=None):
        """
        Xử lý một URL cụ thể - được sử dụng bởi đa luồng
        
        Args:
            url (str): URL cần xử lý
            product_selector (str): CSS selector cho container sản phẩm
            name_selector (str): CSS selector cho tên sản phẩm
            link_selector (str, optional): CSS selector cho link sản phẩm
            
        Returns:
            list: Danh sách sản phẩm từ URL này
        """
        print(f"Đang thu thập từ: {url}")
        soup = self.get_page_content(url)
        
        if not soup:
            print(f"Không thể lấy nội dung từ {url}")
            return []
        
        page_products = self.extract_products(
            soup, 
            product_selector, 
            name_selector, 
            link_selector
        )
        
        # Lưu kết quả tạm thời vào file
        page_number = url.split('p=')[-1] if 'p=' in url else 'unknown'
        temp_file = os.path.join(self.temp_dir, f"page_{page_number}.json")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(page_products, f, ensure_ascii=False, indent=2)
        
        print(f"Đã thu thập {len(page_products)} sản phẩm từ {url}")
        
        # Tạm dừng ngẫu nhiên để tránh bị chặn
        time.sleep(random.uniform(0.5, 2))
        
        return page_products
    
    def scrape_products(self, urls, product_selector, name_selector, link_selector=None):
        """
        Thu thập sản phẩm từ danh sách URLs sử dụng đa luồng
        
        Args:
            urls (list): Danh sách URLs cần thu thập
            product_selector (str): CSS selector cho container sản phẩm
            name_selector (str): CSS selector cho tên sản phẩm
            link_selector (str, optional): CSS selector cho link sản phẩm
        """
        start_time = time.time()
        
        # Sử dụng ThreadPoolExecutor để tạo đa luồng
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Tạo các future cho mỗi URL
            future_to_url = {
                executor.submit(
                    self.process_url, 
                    url, 
                    product_selector, 
                    name_selector, 
                    link_selector
                ): url for url in urls
            }
            
            # Xử lý kết quả khi hoàn thành
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    page_products = future.result()
                    self.products.extend(page_products)
                except Exception as e:
                    print(f"Lỗi khi xử lý {url}: {e}")
        
        end_time = time.time()
        print(f"Tổng thời gian thu thập: {end_time - start_time:.2f} giây")
        print(f"Tổng số sản phẩm đã thu thập: {len(self.products)}")
    
    def merge_temp_files(self):
        """
        Gộp các file tạm thời thành một danh sách sản phẩm
        """
        self.products = []
        
        for filename in os.listdir(self.temp_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.temp_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        page_products = json.load(f)
                        self.products.extend(page_products)
                except Exception as e:
                    print(f"Lỗi khi đọc file {file_path}: {e}")
        
        print(f"Đã gộp {len(self.products)} sản phẩm từ các file tạm thời")
    
    def save_to_json(self):
        """Lưu dữ liệu sản phẩm vào file JSON"""
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Gộp các file tạm thời nếu cần
        if not self.products:
            self.merge_temp_files()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu {len(self.products)} sản phẩm vào file {self.output_file}")
    
    def cleanup_temp_files(self):
        """Xóa các file tạm thời sau khi hoàn thành"""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Lỗi khi xóa file {file_path}: {e}")
    def return_products(self):
        """
        Trả về danh sách sản phẩm đã thu thập
        
        Returns:
            list: Danh sách sản phẩm
        """
        return self.products

# Ví dụ sử dụng
if __name__ == "__main__":
    # URL cơ sở và URL danh mục
    base_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?sort=position&p="
    category_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?sort=position"
    output_file = "data/list_products.json"
    
    # Lấy số lượng sản phẩm và số trang
    number_of_products = get_number_of_products(category_url)
    number_of_pages = get_number_of_pages(number_of_products)
    
    print(f"Tổng số sản phẩm: {number_of_products}")
    print(f"Tổng số trang: {number_of_pages}")
    
    # Khởi tạo scraper với 8 luồng
    scraper = ProductScraper(
        base_url=base_url,
        output_file=output_file,
        number_of_products=number_of_products,
        number_of_pages=number_of_pages,
        max_workers=8,  # Số luồng tối đa chạy đồng thời
        timeout=30      # Thời gian chờ tối đa cho mỗi request
    )
    
    # Tạo danh sách URLs cho tất cả các trang
    urls_to_scrape = scraper.generate_page_urls()
    print(f"Đã tạo {len(urls_to_scrape)} URLs cần thu thập")
    
    # Định nghĩa các CSS selectors để trích xuất thông tin dựa trên HTML mẫu
    product_selector = ".ProductGridItem__itemOuter"  # Container chứa mỗi sản phẩm
    name_selector = ".vn_names"     # Thẻ chứa tên sản phẩm
    link_selector = ".v3_thumb_common_sp"   # Thẻ chứa link sản phẩm
    
    try:
        # Tiến hành thu thập với đa luồng
        scraper.scrape_products(
            urls_to_scrape,
            product_selector,
            name_selector,
            link_selector
        )
        
        # Lưu kết quả vào file JSON
        scraper.save_to_json()
        
        # Dọn dẹp các file tạm thời
        scraper.cleanup_temp_files()
        
    except KeyboardInterrupt:
        print("Đã hủy thu thập dữ liệu. Lưu kết quả đã thu thập được...")
        scraper.save_to_json()
        scraper.cleanup_temp_files()
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        # Vẫn cố gắng lưu dữ liệu đã thu thập được
        scraper.save_to_json()