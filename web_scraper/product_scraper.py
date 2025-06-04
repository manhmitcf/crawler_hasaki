import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin
from web_scraper.get_number_of_pages import get_number_of_products, get_number_of_pages
import os

class ProductScraper:
    def __init__(self, base_url, output_file="products.json", number_of_products=None, number_of_pages=None):
        """
        Khởi tạo scraper với URL cơ sở và file đầu ra
        
        Args:
            base_url (str): URL cơ sở của trang web cần thu thập
            output_file (str): Đường dẫn file JSON đầu ra
            number_of_products (int, optional): Số lượng sản phẩm
            number_of_pages (int, optional): Số trang
        """
        self.base_url = base_url
        self.number_of_products = number_of_products
        self.number_of_pages = number_of_pages
        self.output_file = output_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.products = []

    def generate_page_urls(self):
        """
        Tạo danh sách URLs cho tất cả các trang dựa trên số trang
        
        Args:
            base_category_url (str): URL cơ sở của danh mục sản phẩm
            
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
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải trang {url}: {e}")
            return None
    def extract_products(self, soup, product_selector,link_selector=None, page =1):
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
            # Trích xuất ID sản phẩm nếu có
            product_id = ""
            if product.select_one('.block_info_item_sp'):
                id = product.select_one('.block_info_item_sp').get('id', '')
                data_product = product.select_one('.block_info_item_sp').get('data-product', '')
                data_id = product.select_one('.block_info_item_sp').get('data-id', '')
                data_name = product.select_one('.block_info_item_sp').get('data-name', '')
                data_category_name = product.select_one('.block_info_item_sp').get('data-category-name', '')
                data_variant = product.select_one('.block_info_item_sp').get('data-variant', '')
        

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
            # Số đơn hàng đã bán
            try:
                item_count_by = product.select_one('.item_count_by').get_text(strip=True)
            except Exception as e:
                item_count_by = "Không có thông tin số đơn hàng đã bán"

            products.append({
                'data_id': data_id,
                'id': id,
                'data_product': data_product,
                'data_name': data_name,
                'data_category_name': data_category_name,
                'data_variant': data_variant,   
                'item_count_by': item_count_by,
                'page' : page,
                'link': link,
                'stock_info': stock_info    
            })
        
        return products
    def scrape_products(self, urls, product_selector,link_selector=None):
        """
        Thu thập sản phẩm từ danh sách URLs
        
        Args:
            urls (list): Danh sách URLs cần thu thập
        """
        count = 0
        for page, url in enumerate(urls, start=1):
            print(f"Đang thu thập từ: {url}")
            soup = self.get_page_content(url)
            
            if soup:
                page_products = self.extract_products(
                    soup, 
                    product_selector, 
                    link_selector, page = page
                )
                
                self.products.extend(page_products)
                print(f"Đã thu thập {len(page_products)} sản phẩm từ {url}")
                
                # Tạm dừng để tránh gây tải cho server
                # time.sleep(random.uniform(1, 3))
            count += 1
    def save_to_json(self):
        """Lưu dữ liệu sản phẩm vào file JSON"""
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu {len(self.products)} sản phẩm vào file {self.output_file}")
    def return_products(self):
        """
        Trả về danh sách sản phẩm đã thu thập
        
        Returns:
            list: Danh sách sản phẩm
        """
        return self.products
if __name__ == "__main__":
    # URL cơ sở và URL danh mục
    base_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?p="
    category_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html"
    output_file = "data/list_products.json"
    
    # Lấy số lượng sản phẩm và số trang
    number_of_products = get_number_of_products(category_url)
    number_of_pages = get_number_of_pages(number_of_products)
    
    print(f"Tổng số sản phẩm: {number_of_products}")
    print(f"Tổng số trang: {number_of_pages}")
    
    # Khởi tạo scraper
    scraper = ProductScraper(
        base_url=base_url,
        output_file=output_file,
        number_of_products=number_of_products,
        number_of_pages=number_of_pages
    )
    
    # Tạo danh sách URLs cho tất cả các trang
    urls_to_scrape = scraper.generate_page_urls()
    print(f"Đã tạo {len(urls_to_scrape)} URLs cần thu thập")
    for url in urls_to_scrape:
        print(url)
    # Kiểm tra kết nối đến trang đầu tiên
    first_url = urls_to_scrape[0] if urls_to_scrape else base_url
    soup = scraper.get_page_content(first_url)
    if soup:
        print("Kết nối thành công đến trang web")
    else:
        print("Không thể kết nối đến trang web, vui lòng kiểm tra lại URL hoặc kết nối internet")
    
    # Định nghĩa các CSS selectors để trích xuất thông tin dựa trên HTML mẫu
    product_selector = ".ProductGridItem__itemOuter"  # Container chứa mỗi sản phẩm
    link_selector = ".v3_thumb_common_sp"   # Thẻ chứa link sản phẩm
    
    # Tiến hành thu thập
    scraper.scrape_products(
        urls_to_scrape,
        product_selector,
        link_selector
    )
    
    # Lưu kết quả vào file JSON
    scraper.save_to_json()