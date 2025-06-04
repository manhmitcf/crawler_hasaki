
from bs4 import BeautifulSoup
import json
import time
import requests
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
class CrawlProduct:
    def __init__(self, products_list):
        self.list_id_and_url  = products_list
        self.products = []  
        self.produc_link_api ="https://hasaki.vn/mobile/v3/detail/product?product_id={}&is_desktop=1&form_key=6b36a8e03a246f534507da830c23da32"     
        self.ratting_reviews_api = "https://hasaki.vn/mobile/v3/detail/product/rating-reviews?product_id={}&page=1&size={}&sort=create&is_desktop=1&form_key=6b36a8e03a246f534507da830c23da32"
        self.comments_api = "https://hasaki.vn/mobile/v1/detail/product/comments?product_id={}&page=1&size={}&form_key=6b36a8e03a246f534507da830c23da32"
        self.url_produc_link_api = None
        self.url_ratting_reviews_api = None
        self.url_comments_api = None
        self.id = None
        self.url = None
        self.total_ratting_reviews = 10  
        self.toatal_comments = 10
    def get_page_content(self, url: str):
        if not url:
            raise ValueError("URL không được để trống")

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
            "Mozilla/5.0 (X11; Linux x86_64)...",
        ]
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
            "Referer": "https://hasaki.vn/",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        session = requests.Session()
        session.headers.update(headers)

        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()

            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Lỗi khi tải dữ liệu từ {url}: {e}")
            return None
    def _get_block_by_type(self, blocks, block_type):
        return next((block for block in blocks if block.get('type') == block_type), None)

    def _get_text_from_html(self, html, separator="\n"):
        if not html:
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=separator, strip=True)

    def get_common_info(self, data_json):
        blocks = data_json.get('data', {}).get('blocks', [])

        # === Common Info ===
        common_block = self._get_block_by_type(blocks, 'CommonInfo')
        common_info = common_block.get('common_data', {}) if common_block else {}

        name = common_info.get('name', 'Không có tên')
        english_name = common_info.get('english_name', 'Không có tên tiếng Anh')
        category_name = common_info.get('category_name', 'Không có tên danh mục')
        brand = common_info.get('brand', {}).get('name', 'Không có thương hiệu')
        market_price = common_info.get('market_price', 'Không có giá thị trường')
        price = common_info.get('price', 'Không có giá')
        discount_percent = common_info.get('discount_percent', 'Không có phần trăm giảm giá')
        total_rating = common_info.get('rating', {}).get('total', 'Không có đánh giá')
        average_rating = common_info.get('rating', {}).get('average', 'Không có đánh giá trung bình')
        total_comment = common_info.get('comment', {}).get('total', 'Không có bình luận')
        gallery = common_info.get('gallery', [])
        gallery = [item["image"] for item in gallery if "image" in item]

        category_list = common_info.get('category_list', [])
        categorys = ", ".join([c.get('name') for c in category_list if c.get('name')])

        self.total_ratting_reviews = total_rating  
        self.toatal_comments = total_comment

        # === Description Info ===
        desc_block = self._get_block_by_type(blocks, 'DescriptionInfo')
        description_text = "Đang cập nhật mô tả đầy đủ..."
        description_warning = "Đang cập nhật mô tả cảnh báo..."
        image_links = []

        if desc_block:
            info = desc_block.get('description_data', {}).get('info', {})
            short_desc = info.get('short', "")
            full_html = info.get('full', "")
            warning_html = info.get('description_warning')

            description_text = self._get_text_from_html(full_html) if full_html else description_text
            description_warning = self._get_text_from_html(warning_html) if warning_html else description_warning

            # Ảnh trong phần mô tả
            if full_html:
                soup = BeautifulSoup(full_html, 'html.parser')
                image_links = [
                    img.get('src') for img in soup.find_all('img')
                    if img.get('src') and 'media' in img.get('src')
                ]

        # === Specification Info ===
        spec_block = self._get_block_by_type(blocks, 'SpecificationInfo')
        specification_text = "Không có thông số kỹ thuật nào được cung cấp."
        if spec_block:
            infos = spec_block.get('specification_data', {}).get('infos', [])
            if infos:
                specification_text = "\n".join(
                    f"{item.get('label')}: {item.get('value', 'Không có thông tin')}"
                    for item in infos if item.get('label')
                )

        # === Guide Info ===
        guide_block = self._get_block_by_type(blocks, 'GuideInfo')
        guide_text = "Không có thông tin hướng dẫn sử dụng được cung cấp."
        if guide_block:
            full_guide_html = guide_block.get('guide_data', {}).get('info', {}).get('full', "")
            guide_text = self._get_text_from_html(full_guide_html) if full_guide_html else guide_text

        # === Ingredient Info ===
        ingredient_block = self._get_block_by_type(blocks, 'IngredientInfo')
        ingredient_text = "Không có thông tin thành phần sản phẩm được cung cấp."
        if ingredient_block:
            full_ingredient_html = ingredient_block.get('ingredient_data', {}).get('info', {}).get('full', "")
            ingredient_text = self._get_text_from_html(full_ingredient_html) if full_ingredient_html else ingredient_text

        # === Trả về kết quả tổng hợp ===
        return {
            'data_product': self.id,
            'url': self.url,
            'name': name,
            'english_name': english_name,
            'category_name': category_name,
            'brand': brand,
            'market_price': market_price,
            'price': price,
            'discount_percent': discount_percent,
            'total_rating': total_rating,
            'average_rating': average_rating,
            'comment': total_comment,
            'categorys': categorys,
            'descriptioninfo': description_text,
            'description_warning': description_warning,
            'specificationinfo': specification_text,
            'ingredientinfo': ingredient_text,
            'guideinfo': guide_text,
            'gallery': gallery,
            'image_links_descriptioninfo': image_links,
        }
    def get_ratting_reviews(self,review_json):
        data = review_json.get("data", {})
        reviews_data = data.get("reviews", [])
        stars_data = data.get("rating", {}).get("stars", [])

        # Tạo chuỗi đánh giá sao
        star_lines = [
            f"{star['star']} sao - {star['count']} lượt ({star['description']})"
            for star in stars_data
        ]
        stars_text = "\n".join(star_lines)

        comments = []
        image_links = []

        for review in reviews_data:
            user = review.get("user_fullname", "Người dùng ẩn danh")
            content = review.get("content", "")
            answer = review.get("answer_rating", "")

            if answer:
                comments.append(f"{user}: {content}\nHasaki: {answer}")
            else:
                comments.append(f"{user}: {content}")

            # Chỉ lấy ảnh từ trường 'images'
            images = review.get("images", [])
            if images:
                image_links.extend(images)

        # Trả kết quả dưới dạng dict
        return {
            'stars': stars_text,
            'reviews': comments,
            'image_links_ratting_reviews': image_links,
        }
    def get_comments(self, comments_json):
        conversations = []

        for comment in comments_json["data"]["comments"]:
            dialogue_lines = [f"Q: {comment['content'].strip()}"]
            for sub in comment.get("sub_comments", []):
                dialogue_lines.append(f"A: {sub['content'].strip()}")
            dialogue_block = "\n".join(dialogue_lines)
            conversations.append(dialogue_block)
        return conversations
    def crawl_product(self):
        count = 1
        for product in self.list_id_and_url:
            self.url = product['link']
            self.id = product['data_product']
            print("Lần thứ:", count)
            print(f"Đang thu thập từ: {self.id} - {self.url}")
            print("==" * 50)
            self.url_produc_link_api = self.produc_link_api.format(self.id)
            data_json = self.get_page_content(url=self.url_produc_link_api)
            if data_json:
                data_product = self.get_common_info(data_json)
            self.url_ratting_reviews_api = self.ratting_reviews_api.format(self.id, self.total_ratting_reviews)
            review_json = self.get_page_content(url=self.url_ratting_reviews_api)
            if review_json:
                ratting_reviews = self.get_ratting_reviews(review_json)
                data_product.update(ratting_reviews)
            self.url_comments_api = self.comments_api.format(self.id, self.toatal_comments)
            comments_json = self.get_page_content(url=self.url_comments_api)
            if comments_json:
                comments = self.get_comments(comments_json)
                data_product['comments'] = comments
            self.products.append(data_product)
            # time.sleep(random.uniform(1, 3))  # Để tránh bị chặn IP nếu cần
            count += 1
    def return_list_products(self):
        return self.products
if __name__ == "__main__":
    with open('data/list_products.json', 'r', encoding='utf-8') as f:
        products_list = json.load(f)
    # Khởi tạo đối tượng CrawlProduct
    crawler = CrawlProduct(products_list)
    # Bắt đầu quá trình thu thập dữ liệu
    crawler.crawl_product() 

    # Lấy danh sách sản phẩm đã thu thập        
    products = crawler.return_list_products()
    print(f"Đã thu thập {len(products)} sản phẩm")

    # Lưu kết quả vào file JSON
    with open('data/product.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print("Đã lưu dữ liệu sản phẩm vào file products.json")





