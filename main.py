import time
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from web_scraper.product_scraper import ProductScraper
from web_scraper.get_number_of_pages import get_number_of_products, get_number_of_pages

from mongodb_sever.insert_list_products import insert_products_to_mongodb_sever
from crawler.crawl_product_API import CrawlProduct
from pymongo.errors import CollectionInvalid

# Load environment variables from .env file
load_dotenv()

def main():
    start_time = time.time()

    try:
        # ====== 1. KẾT NỐI DATABASE ======
        mongodb_uri = os.getenv('MONGODB_URI')
        database_name = os.getenv('MONGODB_DATABASE', 'hasaki_db')
        
        if not mongodb_uri:
            raise ValueError("MONGODB_URI không được tìm thấy trong file .env")
            
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        if "products" not in db.list_collection_names():
            # ====== 2. PHÂN TÍCH DANH MỤC & TẠO URL ======
            base_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?p="
            category_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html"

            print(f"Đang phân tích danh mục: {category_url}")
            number_of_products = get_number_of_products(category_url)
            number_of_pages = get_number_of_pages(number_of_products)
            print(f"Tổng số sản phẩm: {number_of_products}")
            print(f"Tổng số trang: {number_of_pages}")

            # ====== 3. SCRAPE DANH SÁCH SẢN PHẨM ======
            scraper = ProductScraper(base_url, None , number_of_products , number_of_pages)
            urls_to_scrape = scraper.generate_page_urls()
            print(f"Đã tạo {len(urls_to_scrape)} URL cần thu thập")

            # Kiểm tra kết nối trang 
            if not scraper.get_page_content(urls_to_scrape[0]):
                print("Không thể kết nối đến trang web, vui lòng kiểm tra lại URL hoặc kết nối internet")
                return
            print("Kết nối thành công đến trang web")

            # Thu thập sản phẩm
            product_selector = ".ProductGridItem__itemOuter"
            link_selector = ".v3_thumb_common_sp"
            print(f"Bắt đầu thu thập dữ liệu danh sách sản phẩm ...")
            scraper.scrape_products(urls_to_scrape, product_selector, link_selector)

            # ====== 4. INSERT VÀO MONGODB (products) ======
            products = scraper.return_products()
            print(f"Đã thu thập {len(products)} sản phẩm từ danh mục")
            insert_products_to_mongodb_sever(products, database_name, "products", client)
        else:
            print("Collection 'products' đã tồn tại, bỏ qua tạo mới.")
            # ====== 5. GỌI API CHI TIẾT SẢN PHẨM ======
            print("Bắt đầu gọi API chi tiết sản phẩm...")
            products_list = db["products"].find()
            crawler = CrawlProduct(products_list)
            crawler.crawl_product()
            detail_products = crawler.return_list_products()
            print(f"Đã thu thập {len(detail_products)} sản phẩm chi tiết")

            # ====== 6. INSERT VÀO MONGODB (product_detail) ======
            try:
                db.create_collection("product_detail")
                print("Đã tạo collection 'product_detail'.")
            except CollectionInvalid:
                print("Collection 'product_detail' đã tồn tại, bỏ qua tạo mới.")
            insert_products_to_mongodb_sever(detail_products, database_name, "product_detail", client)

            # ====== 7. TỔNG KẾT ======
            client.close()
            duration = time.time() - start_time
            print(f"\nTổng thời gian thực hiện: {duration:.2f} giây")
            print("Hoàn thành!")

    except KeyboardInterrupt:
        print("\nĐã hủy quá trình thu thập dữ liệu.")
    except Exception as e:
        print(f"\nLỗi: {e}")


if __name__ == "__main__":
    main()
