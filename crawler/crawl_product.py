
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os


class CrawlProduct:
    def __init__(self, products_list):
        self.list_id_and_url  = products_list
        self.products = [] 
        self.url = None
        self.id = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
    def get_random_headers(self):
        """Sinh headers với User-Agent ngẫu nhiên"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
        }
    def get_page_content(self):
        """
        Lấy nội dung HTML của trang web
        
        Args:
            url (str): URL của trang cần lấy nội dung
        Returns:
            BeautifulSoup: Đối tượng BeautifulSoup chứa nội dung trang
        """
        try:
            response = requests.get(self.url, headers=self.get_random_headers())
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải trang {self.url}: {e}")
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
        product = None
        try:
            target_div = soup.find('div', class_='flex items-center gap-1 text-[#326E51] text-[13px]')
            a_tags = target_div.find_all('a', class_='cursor-pointer')
            number_of_reviews = a_tags[0].text.strip()  
            number_of_qa = a_tags[1].text.strip() 
        except Exception as e:
            number_of_reviews = ''
            number_of_qa = ''

        try:
            imgs = soup.find_all('img', class_='mt-2.5 first:mt-0 border-[1px] border-[#e5e5e5] cursor-pointer')
            image_links = [img['src'] for img in imgs]
        except Exception as e:
            image_links = []

        try: 
            descriptioninfo = soup.find('div', id='DescriptionInfo').get_text(separator='\n', strip=True)
        except Exception as e:
            descriptioninfo = ''

        try:
            specificationinfo = soup.find('div', id='SpecificationInfo').get_text(separator='\n', strip=True)
        except Exception as e:
            specificationinfo = ''  

        try:
            ingredientinfo = soup.find('div', id='IngredientInfo').get_text(separator='\n', strip=True) 
        except Exception as e:
            ingredientinfo = ''
        
        try:
            guideinfo = soup.find('div', id='GuideInfo').get_text(separator='\n', strip=True) 
        except Exception as e:
            guideinfo = ''
        try:
            average_rating = soup.find('div', class_="text-orange text-[80px] font-bold leading-[80px]").get_text(strip=True)
        except Exception as e:
            average_rating = ''
        
 
        product ={
            'data_id': data_id,
            'number_of_reviews': number_of_reviews,
            'number_of_qa': number_of_qa,
            'image_links': image_links,
            'descriptioninfo': descriptioninfo,
            'specificationinfo': specificationinfo,
            'ingredientinfo': ingredientinfo,
            'guideinfo': guideinfo,
            'average_rating': average_rating,
            'url': self.url
        }

        return product
    def process_multiple_products(self):
        """
        Xử lý các URL và trích xuất thông tin sản phẩm từ mỗi trang web
        
        Args:
            urls (list): Danh sách URLs cần thu thập
        """
        count = 0
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
                time.sleep(random.uniform(1, 3))

    def return_list_products(self):
        return self.products
if __name__ == "__main__":
    with open('data/list_products1.json', 'r', encoding='utf-8') as f:
        products_list = json.load(f)
    print("Đang bắt đầu thu thập sản phẩm...")


    
    crawler = CrawlProduct(products_list)
    crawler.process_multiple_products()
    
    products = crawler.return_list_products()
    
    # Lưu kết quả vào file JSON
    with open('data/product.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print("Đã lưu dữ liệu sản phẩm vào file products.json")





