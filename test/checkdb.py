
from pymongo import MongoClient

try:
    client = MongoClient("mongodb://admin:your_secure_password@20.2.235.19:27017/?authSource=admin")
    print("✅ Kết nối thành công!")

    # Lấy danh sách database
    print("🧱 Danh sách databases:")
    print(client.list_database_names())
    # Tên database muốn xoá
    db_name = "hasaki_db"

    # Xoá database
    client.drop_database(db_name)

    print(f"Đã xoá database '{db_name}' thành công.")

except Exception as e:
    print("❌ Lỗi:", e)





