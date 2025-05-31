"""
MongoDB Server Package

Package này chứa các module và công cụ để tương tác với MongoDB.
"""

# Import các hàm và lớp cần thiết để sử dụng từ bên ngoài package
from .insert_list_products import insert_products_to_mongodb_sever

# Định nghĩa các thành phần được export khi sử dụng "from mongodb_sever import *"
__all__ = ['insert_products_to_mongodb_sever']

# Thông tin phiên bản
__version__ = '1.0.0'
