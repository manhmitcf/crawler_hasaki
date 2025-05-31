import requests
from bs4 import BeautifulSoup
import re

def get_number_of_products(url: str) -> int:
    """
    Lấy số lượng sản phẩm trên trang web
    Args:
        url (str): URL của trang web cần lấy số lượng sản phẩm
    Returns:
        int: Số lượng sản phẩm
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm phần tử chứa tổng số sản phẩm
        total_products_element = soup.select_one('.txt_999')  # Cập nhật selector nếu cần
        if total_products_element:
            total_products_text = total_products_element.get_text().strip()
            print(f"Tổng số sản phẩm: {total_products_text}")
            # Lấy số từ chuỗi (ví dụ: "Có 1.234 sản phẩm")
            match = re.search(r'(\d[\d\.]*)', total_products_text)
            if match:
                number_str = match.group(1).replace('.', '')
                return int(number_str)
            else:
                print("Không tìm thấy số trong chuỗi.")
            return 0
        else:
            print("Không tìm thấy phần tử chứa tổng số sản phẩm.")
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải trang {url}: {e}")
        return 0
def get_number_of_pages(number_of_products : int) -> int:
    """
    Tính số trang dựa trên số lượng sản phẩm
    Args:
        number_of_products (int): Số lượng sản phẩm
    Returns:
        int: Số trang
    """
    products_per_page = 40  # Giả sử mỗi trang có 40 sản phẩm
    return int(number_of_products / products_per_page) + (1 if number_of_products % products_per_page > 0 else 0)


if __name__ == "__main__":
    url = 'https://hasaki.vn/danh-muc/suc-khoe-lam-dep-c3.html?sort=position'
    number_of_products = get_number_of_products(url)
    print(f"Số lượng sản phẩm: {number_of_products}")
    number_of_pages = get_number_of_pages(number_of_products)
    print(f"Số trang: {number_of_pages}")
