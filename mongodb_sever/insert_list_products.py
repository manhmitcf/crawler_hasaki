
def insert_products_to_mongodb_sever(products, db_name, collection_name, client):
    """
    Chèn danh sách sản phẩm vào MongoDB
    Args:
        products (list): Danh sách sản phẩm cần chèn
    """
    client = client # Kết nối MongoDB
    db = client[db_name]  # Tên database
    collection = db[collection_name]  # Tên collection
    try:
        # Chèn danh sách sản phẩm vào collection
        result = collection.insert_many(products)
        print(f"Đã chèn {len(result.inserted_ids)} sản phẩm vào MongoDB.")
    except Exception as e:
        print(f"Lỗi khi chèn sản phẩm: {e}")
if __name__ == "__main__":
    from pymongo import MongoClient
    # Ví dụ sử dụng
    products = [
        {"name": "Sản phẩm 1", "link": "https://example.com/product1"},
        {"name": "Sản phẩm 2", "link": "https://example.com/product2"}
    ]
    db_name = "hasaki"
    collection_name = "products"
    
    # Kết nối đến MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    
    insert_products_to_mongodb_sever(products, db_name, collection_name, client)
    
    # Đóng kết nối
    client.close()
