
import time
from pymongo import MongoClient
from web_scraper.product_scraper import ProductScraper, get_number_of_pages, get_number_of_products
from mongodb_sever.insert_list_products import insert_products_to_mongodb_sever
from crawler.crawl_product import CrawlProduct
from pymongo.errors import CollectionInvalid

def main1():
    # Bắt đầu đo thời gian
    start_time = time.time()
  
    try:
        # Kết nối tới MongoDB
        client = MongoClient("mongodb://admin:your_secure_password@20.2.235.19:27017/?authSource=admin")
        db_name = "hasaki_db"  # Tên database
        collection_name = "products"  # Tên collection
        
        # URL cơ sở và URL danh mục
        base_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?sort=position&p="
        category_url = "https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?sort=position"

        
        print(f"Đang phân tích danh mục: {category_url}")
        
        # Lấy số lượng sản phẩm và số trang
        number_of_products = get_number_of_products(category_url)
        number_of_pages = get_number_of_pages(number_of_products)
        
        print(f"Tổng số sản phẩm: {number_of_products}")
        print(f"Tổng số trang: {number_of_pages}")
        
        # Khởi tạo scraper
        scraper = ProductScraper(
            base_url=base_url,
            number_of_products=number_of_products,
            number_of_pages=number_of_pages
        )
        # Tạo danh sách URL cho tất cả các trang
        urls_to_scrape = scraper.generate_page_urls()
        print(f"Đã tạo {len(urls_to_scrape)} URL cần thu thập")
        
        # Kiểm tra kết nối đến trang web
        first_url = urls_to_scrape[0] if urls_to_scrape else base_url
        soup = scraper.get_page_content(first_url)
        if soup:
            print("Kết nối thành công đến trang web")
        else:
            print("Không thể kết nối đến trang web, vui lòng kiểm tra lại URL hoặc kết nối internet")
            return
        
        # Định nghĩa các CSS selector để trích xuất thông tin
        product_selector = ".ProductGridItem__itemOuter"  # Container chứa mỗi sản phẩm
        name_selector = ".vn_names"     # Thẻ chứa tên sản phẩm
        link_selector = ".v3_thumb_common_sp"   # Thẻ chứa link sản phẩm
        
        # Tiến hành thu thập dữ liệu
        print(f"Bắt đầu thu thập dữ liệu ...")
        scraper.scrape_products(
            urls_to_scrape,
            product_selector,
            name_selector,
            link_selector
        )
        # Lấy danh sách sản phẩm đã thu thập
        products = scraper.return_products()
        print(f"Đã thu thập {len(products)} sản phẩm")
        
        
        # Chèn sản phẩm vào MongoDB
        print(f"Bắt đầu insert dữ liệu vào MongoDB ({db_name}.{collection_name})...")
        insert_products_to_mongodb_sever(products, db_name, collection_name, client)
        
        # Đóng kết nối
        client.close()
        
        # Tính thời gian thực hiện
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nTổng thời gian thực hiện: {duration:.2f} giây")
        print("Hoàn thành!")

        
    except KeyboardInterrupt:
        print("\nĐã hủy quá trình thu thập dữ liệu.")
    except Exception as e:
        print(f"\nLỗi: {e}")
def main2():
    start_time = time.time()

    try:
        client = MongoClient("mongodb://admin:your_secure_password@20.2.235.19:27017/?authSource=admin")
        db = client["hasaki_db"]
        collection = db["products"]
        products_list = collection.find()

        crawler = CrawlProduct(products_list)
        crawler.process_multiple_products()
        print(f"Đã thu thập {len(crawler.products)} sản phẩm")
        products = crawler.return_list_products()

        # Tạo collection "product_detail" nếu chưa có
        try:
            db.create_collection("product_detail")
            print("Đã tạo collection 'product_detail'.")
        except CollectionInvalid:
            print("Collection 'product_detail' đã tồn tại, bỏ qua tạo mới.")
        db_name = "hasaki_db"  # Tên database
        collection_name = "product_detail"  # Tên collection

        print(f"Bắt đầu insert dữ liệu vào MongoDB")
        insert_products_to_mongodb_sever(products, db_name, collection_name, client)

        client.close()

        end_time = time.time()
        duration = end_time - start_time
        print(f"\nTổng thời gian thực hiện: {duration:.2f} giây")
        print("Hoàn thành!")

    except KeyboardInterrupt:
        print("\nĐã hủy quá trình thu thập dữ liệu.")
    except Exception as e:
        print(f"\nLỗi: {e}")
if __name__ == "__main__":
    main1()
    main2()
