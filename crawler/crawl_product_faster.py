import json
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from multiprocessing import Pool
import os
def get_page_content(url):
    """
    Lấy nội dung trang web bằng Selenium.
    """
    try:
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--headless')  
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        stealth(
            driver,
            languages=["vi-VN", "vi"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'DescriptionInfo'))
        )
        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f"Lỗi khi tải trang {url} bằng selenium-stealth: {e}")
        return None

def extract_product(soup, data_id, url):
    """
    Trích xuất thông tin sản phẩm từ nội dung HTML.

    Args:
        soup (BeautifulSoup): Đối tượng BeautifulSoup chứa nội dung trang.
        data_id (str): ID của sản phẩm.
        url (str): URL của sản phẩm.

    Returns:
        dict: Thông tin sản phẩm.
    """
    product = {
        'data_id': data_id,
        'number_of_reviews': '',
        'number_of_qa': '',
        'image_links': [],
        'descriptioninfo': '',
        'specificationinfo': '',
        'ingredientinfo': '',
        'guideinfo': '',
        'average_rating': '',
        'url': url
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

def process_single_product(task):
    """
    Xử lý một sản phẩm: lấy nội dung trang và trích xuất thông tin.

    Args:
        task (tuple): Bộ gồm (item, index), trong đó item chứa link và data_id.

    Returns:
        dict: Thông tin sản phẩm đã trích xuất.
    """
    item, index = task
    url = item['link']
    data_id = item['data_id']
    print(f"Lần thứ: {index}")
    print(f"Đang thu thập từ: {url}")
    print("==" * 50)

    soup = get_page_content(url)
    if soup:
        product = extract_product(soup, data_id, url)
        time.sleep(random.uniform(1, 3))  # Random delay to avoid server overload
        return product
    return None

class CrawlProduct:
    def __init__(self, products_list):
        self.list_id_and_url = products_list
        self.products = []

    def process_multiple_products(self, batch_size=5):
        """
        Xử lý tất cả các sản phẩm song song theo lô bằng multiprocessing.

        Args:
            batch_size (int): Số lượng process chạy song song.
        """
        with Pool(processes=batch_size) as pool:
            for i in range(0, len(self.list_id_and_url), batch_size):
                batch = self.list_id_and_url[i:i + batch_size]
                # Create tasks with index for logging
                tasks = [(item, i + j + 1) for j, item in enumerate(batch)]
                # Run batch in parallel
                results = pool.map(process_single_product, tasks)
                # Collect non-None results
                for result in results:
                    if result:
                        self.products.append(result)

    def return_list_products(self):
        return self.products

def main():
    # Đọc dữ liệu từ file JSON
    with open('data/list_products1.json', 'r', encoding='utf-8') as f:
        products_list = json.load(f)

    # Khởi tạo đối tượng CrawlProduct
    crawler = CrawlProduct(products_list)

    # Bắt đầu quá trình thu thập dữ liệu
    print("Bắt đầu thu thập dữ liệu sản phẩm ...")
    crawler.process_multiple_products(batch_size=os.cpu_count())  
    # Lấy danh sách sản phẩm đã thu thập
    products = crawler.return_list_products()
    print(f"Đã thu thập {len(products)} sản phẩm")

    # Lưu kết quả vào file JSON
    with open('data/product.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

    print("Đã lưu dữ liệu sản phẩm vào file products.json")

if __name__ == "__main__":
    main()