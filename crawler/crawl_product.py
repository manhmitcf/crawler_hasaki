
from bs4 import BeautifulSoup
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
class CrawlProduct:
    def __init__(self, products_list):
        self.list_id_and_url  = products_list
        self.products = [] 
        self.url = None
        self.id = None
    def get_page_content(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled') # Tắt chế độ tự động hóa
            options.add_argument('--headless')  # Chạy trình duyệt ở chế độ không giao diện
            options.add_argument('--no-sandbox') # Giúp tránh lỗi khi chạy trên môi trường không có giao diện
            driver = webdriver.Chrome(options=options)

            stealth(driver,
                languages=["vi-VN", "vi"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

            driver.get(self.url)
            WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.ID, 'DescriptionInfo'))
            )
            html = driver.page_source
            driver.quit()
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"Lỗi khi tải trang {self.url} bằng selenium-stealth: {e}")
            return None
    def extract_product(self, soup, data_id):
        """
        Trích xuất thông tin sản phẩm từ nội dung HTML

        Args:
            soup (BeautifulSoup): Đối tượng BeautifulSoup chứa nội dung trang
            data_id (str): ID của sản phẩm

        Returns:
            list: Danh sách sản phẩm
        """
        product ={
            'data_id': data_id,
            'number_of_reviews': '',
            'number_of_qa': '',
            'image_links': [],
            'descriptioninfo': '',
            'specificationinfo': '',
            'ingredientinfo': '',
            'guideinfo': '',
            'average_rating': '',
            'url': self.url
        }

        try:
            target_div = soup.find('div', class_='flex items-center gap-1 text-[#326E51] text-[13px]')
            a_tags = target_div.find_all('a', class_='cursor-pointer')
            product['number_of_reviews'] = a_tags[0].get_text(strip=True) 
            product['number_of_qa'] = a_tags[1].get_text(strip=True) 
        except Exception as e:
            print(f"Lỗi khi trích xuất số lượng đánh giá và câu hỏi: {e}")

        try:
            imgs = soup.find_all('img', class_='mt-2.5 first:mt-0 border-[1px] border-[#e5e5e5] cursor-pointer')
            product['image_links'] = [img['src'] for img in imgs]
        except Exception as e:
            print(f"Lỗi khi trích xuất hình ảnh: {e}")
        try: 
            product['descriptioninfo'] = soup.find('div', id='DescriptionInfo').get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Lỗi khi trích xuất mô tả sản phẩm: {e}")

        try:
            product['specificationinfo'] = soup.find('div', id='SpecificationInfo').get_text(separator='\n', strip=True)
        except Exception as e:
            print(f"Lỗi khi trích xuất thông số kỹ thuật: {e}") 

        try:
            product['ingredientinfo'] = soup.find('div', id='IngredientInfo').get_text(separator='\n', strip=True) 
        except Exception as e:
            print(f"Lỗi khi trích xuất thành phần: {e}")

        
        try:
            product['guideinfo'] = soup.find('div', id='GuideInfo').get_text(separator='\n', strip=True) 
        except Exception as e:
            print(f"Lỗi khi trích xuất hướng dẫn sử dụng: {e}")

        try:
            product['average_rating'] = soup.find('div', class_="text-orange text-[80px] font-bold leading-[80px]").get_text(strip=True)
        except Exception as e:
            print(f"Lỗi khi trích xuất đánh giá trung bình: {e}")
        return product
    def process_multiple_products(self):
        """
        Xử lý các URL và trích xuất thông tin sản phẩm từ mỗi trang web
        
        Args:
            urls (list): Danh sách URLs cần thu thập
        """
        count = 1
        for iteam in self.list_id_and_url:
            self.url = iteam['link']
            self.id = iteam['data_id']
            print("Lần thứ:", count)
            print(f"Đang thu thập từ: {self.url}")
            print("==" * 50)
            soup = self.get_page_content()
            if soup:
                product = self.extract_product(
                    soup, 
                    self.id
                )
                self.products.append(product)
                # Tạm dừng để tránh gây tải cho server
                count += 1
                # time.sleep(random.uniform(1, 3))
    def return_list_products(self):
        return self.products
if __name__ == "__main__":
    with open('data/list_products1.json', 'r', encoding='utf-8') as f:
        products_list = json.load(f)
    # Khởi tạo đối tượng CrawlProduct
    crawler = CrawlProduct(products_list)
    # Bắt đầu quá trình thu thập dữ liệu
    print("Bắt đầu thu thập dữ liệu sản phẩm ...")  
    crawler.process_multiple_products()
    # Lấy danh sách sản phẩm đã thu thập        
    products = crawler.return_list_products()
    print(f"Đã thu thập {len(products)} sản phẩm")

    # Lưu kết quả vào file JSON
    with open('data/product.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print("Đã lưu dữ liệu sản phẩm vào file products.json")





