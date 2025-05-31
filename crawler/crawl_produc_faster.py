import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import time
import random
import os
import logging
import warnings

warnings.filterwarnings('ignore', category=RuntimeWarning, message='Event loop is closed')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CrawlProduct:
    def __init__(self, products_list):
        self.list_id_and_url = products_list
        self.products = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = None

    async def init_session(self):
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
            await asyncio.sleep(0.25)

    async def get_page_content(self, url, retries=3):
        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    html_content = await response.text()
                    return BeautifulSoup(html_content, 'html.parser')
            except Exception as e:
                if attempt == retries - 1:
                    logging.error(f"Hết lượt thử cho {url}: {e}")
                    return None
                await asyncio.sleep(1)
        return None

    def extract_product(self, soup, data_id, url):
        product = {
            'data_id': data_id,
            'url': url,
            'number_of_reviews': '',
            'number_of_qa': '',
            'image_links': [],
            'descriptioninfo': '',
            'specificationinfo': '',
            'ingredientinfo': '',
            'guideinfo': '',
            'average_rating': ''
        }
        try:
            target_div = soup.find('div', class_='flex items-center gap-1 text-[#326E51] text-[13px]')
            if target_div:
                a_tags = target_div.find_all('a', class_='cursor-pointer')
                product['number_of_reviews'] = a_tags[0].text.strip() if a_tags else ''
                product['number_of_qa'] = a_tags[1].text.strip() if len(a_tags) > 1 else ''
        except Exception:
            pass

        try:
            imgs = soup.find_all('img', class_='mt-2.5 first:mt-0 border-[1px] border-[#e5e5e5] cursor-pointer')
            product['image_links'] = [img['src'] for img in imgs if img.get('src')]
        except Exception:
            pass

        try:
            product['descriptioninfo'] = soup.find('div', id='DescriptionInfo').get_text(separator='\n', strip=True)
        except Exception:
            pass

        try:
            product['specificationinfo'] = soup.find('div', id='SpecificationInfo').get_text(separator='\n', strip=True)
        except Exception:
            pass

        try:
            product['ingredientinfo'] = soup.find('div', id='IngredientInfo').get_text(separator='\n', strip=True)
        except Exception:
            pass

        try:
            product['guideinfo'] = soup.find('div', id='GuideInfo').get_text(separator='\n', strip=True)
        except Exception:
            pass

        try:
            product['average_rating'] = soup.find('div', class_="text-orange text-[80px] font-bold leading-[80px]").get_text(strip=True)
        except Exception:
            pass

        return product

    async def crawl_single_product(self, item, index):
        url = item['link']
        data_id = item['data_id']
        logging.info(f"Đang thu thập sản phẩm thứ {index + 1}/{len(self.list_id_and_url)}: {url}")
        soup = await self.get_page_content(url)
        product = self.extract_product(soup, data_id, url) if soup else {
            'data_id': data_id,
            'url': url,
            'number_of_reviews': '',
            'number_of_qa': '',
            'image_links': [],
            'descriptioninfo': '',
            'specificationinfo': '',
            'ingredientinfo': '',
            'guideinfo': '',
            'average_rating': ''
        }
        logging.info(f"Đã crawl thành công: {data_id}")
        return product

    async def process_multiple_products_async(self, max_concurrent=5):
        await self.init_session()
        try:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def crawl_with_semaphore(item):
                async with semaphore:
                    product = await self.crawl_single_product(item, self.list_id_and_url.index(item))
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    return product

            tasks = [crawl_with_semaphore(item) for item in self.list_id_and_url]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"Lỗi khi crawl item {i}: {result}")
                    item = self.list_id_and_url[i]
                    self.products.append({
                        'data_id': item['data_id'],
                        'url': item['link'],
                        'number_of_reviews': '',
                        'number_of_qa': '',
                        'image_links': [],
                        'descriptioninfo': '',
                        'specificationinfo': '',
                        'ingredientinfo': '',
                        'guideinfo': '',
                        'average_rating': ''
                    })
                else:
                    self.products.append(result)
        finally:
            await self.close_session()

    def return_list_products(self):
        return self.products


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    async def main():
        file_path = r"data/list_products1.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            products_list = json.load(f)

        logging.info(f"Bắt đầu crawl {len(products_list)} sản phẩm với async...")
        start_time = time.time()

        crawler = CrawlProduct(products_list)
        await crawler.process_multiple_products_async(max_concurrent=5)

        end_time = time.time()
        crawl_time = end_time - start_time
        products = crawler.return_list_products()

        logging.info(f"Đã thu thập {len(products)} sản phẩm trong {crawl_time:.2f} giây")
        logging.info(f"Tốc độ trung bình: {len(products)/crawl_time:.2f} sản phẩm/giây")

        output_file = "data/product.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        chunk_size = 100
        for i in range(0, len(products), chunk_size):
            chunk = products[i:i + chunk_size]
            mode = 'w' if i == 0 else 'a'
            with open(output_file, mode, encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
                if mode == 'a':
                    f.write('\n')

        logging.info(f"Đã lưu {len(products)} sản phẩm vào file {output_file}")

    asyncio.run(main())