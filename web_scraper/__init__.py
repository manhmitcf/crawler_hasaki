"""
Web Scraper Package

Package này chứa các module và công cụ để thu thập dữ liệu từ các trang web.
"""

# Import các hàm và lớp cần thiết để sử dụng từ bên ngoài package
from .product_scraper import ProductScraper
from .get_number_of_pages import get_number_of_pages, get_number_of_products

# Định nghĩa các thành phần được export khi sử dụng "from web_scraper import *"
__all__ = ['ProductScraper', 'get_number_of_pages', 'get_number_of_products']

# Thông tin phiên bản
__version__ = '1.0.0'
