from pymongo import MongoClient
from bson.objectid import ObjectId

def find_document_by_id(input_id):
    # Thử tìm theo ObjectId
    try:
        obj_id = ObjectId(input_id)
        doc = collection.find_one({"data_id": obj_id})
        if doc:
            return doc
    except:
        pass  # Không phải ObjectId

    # Thử tìm theo số nguyên
    try:
        int_id = int(input_id)
        doc = collection.find_one({"data_id": int_id})
        if doc:
            return doc
    except:
        pass

    # Thử tìm theo string
    doc = collection.find_one({"data_id": input_id})
    return doc
def print_first_100_documents():
    docs = collection.find().limit(100)
    for i, doc in enumerate(docs, 1):
        print(f"{i}: {doc}")

if __name__ == "__main__":
    # Kết nối MongoDB
    client = MongoClient("mongodb://admin:your_secure_password@20.2.235.19:27017/?authSource=admin")
    db = client["hasaki_db"]
    collection = db["product_detail"]
    print("Kết nối MongoDB thành công!")
    # print("Danh sách 100 document đầu tiên:")
    # print_first_100_documents()
    input_id = input("Nhập vào id document: ").strip()
    document = find_document_by_id(input_id)
    if document:
        print("Tìm thấy document:")
        print(document['descriptioninfo'])
    else:
        print("Không tìm thấy document với id đó.")

