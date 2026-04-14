"""
Selenium scraper for books.toscrape.com
Scrapes: title, rating, price, availability, genre, description, cover image, book URL
Supports multi-page scraping.
"""
import time
import django
import os
import sys

# Allow running this script standalone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from books.models import Book
from ai.insights import generate_all_insights
from ai.embeddings import embed_and_store_book

BASE_URL = "https://books.toscrape.com"

RATING_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0
}


def get_driver():
    """Sets up headless Chrome driver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    # Explicitly find Chrome on Windows
    import shutil
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("chrome"),
        shutil.which("google-chrome"),
    ]
    for path in chrome_paths:
        if path and os.path.exists(path):
            options.binary_location = path
            break

    # Fix webdriver-manager bug — find actual chromedriver.exe
    driver_path = ChromeDriverManager().install()
    driver_dir = os.path.dirname(driver_path)
    chromedriver_exe = os.path.join(driver_dir, 'chromedriver.exe')
    if not os.path.exists(chromedriver_exe):
        # Search subdirectories
        for root, dirs, files in os.walk(os.path.dirname(driver_dir)):
            for f in files:
                if f == 'chromedriver.exe':
                    chromedriver_exe = os.path.join(root, f)
                    break

    service = Service(chromedriver_exe)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_book_detail(driver, book_url):
    """Scrapes the detail page of a single book."""
    driver.get(book_url)
    time.sleep(1)

    data = {}

    try:
        data['title'] = driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
    except Exception:
        data['title'] = 'Unknown Title'

    try:
        rating_class = driver.find_element(By.CSS_SELECTOR, 'p.star-rating').get_attribute('class')
        rating_word = rating_class.replace('star-rating', '').strip()
        data['rating'] = RATING_MAP.get(rating_word, 0.0)
    except Exception:
        data['rating'] = 0.0

    try:
        data['price'] = driver.find_element(By.CSS_SELECTOR, 'p.price_color').text.strip()
    except Exception:
        data['price'] = ''

    try:
        data['availability'] = driver.find_element(
            By.CSS_SELECTOR, 'p.availability'
        ).text.strip()
    except Exception:
        data['availability'] = ''

    try:
        desc_elem = driver.find_element(By.CSS_SELECTOR, '#product_description ~ p')
        data['description'] = desc_elem.text.strip()
    except Exception:
        data['description'] = ''

    try:
        # Genre is in breadcrumb: Home > Books > Genre > Title
        breadcrumbs = driver.find_elements(By.CSS_SELECTOR, 'ul.breadcrumb li')
        if len(breadcrumbs) >= 3:
            data['genre'] = breadcrumbs[-2].text.strip()
        else:
            data['genre'] = ''
    except Exception:
        data['genre'] = ''

    try:
        img_src = driver.find_element(By.CSS_SELECTOR, '#product_gallery img').get_attribute('src')
        # Fix relative URL
        if img_src.startswith('../../'):
            img_src = BASE_URL + '/' + img_src.replace('../../', '')
        data['cover_image_url'] = img_src
    except Exception:
        data['cover_image_url'] = ''

    return data


def scrape_books(num_pages=5):
    """
    Main scraping function.
    Iterates through catalogue pages and scrapes each book's detail page.
    """
    driver = get_driver()
    scraped_count = 0
    new_count = 0

    try:
        for page_num in range(1, num_pages + 1):
            if page_num == 1:
                page_url = f"{BASE_URL}/catalogue/page-1.html"
            else:
                page_url = f"{BASE_URL}/catalogue/page-{page_num}.html"

            print(f"Scraping page {page_num}: {page_url}")
            driver.get(page_url)
            time.sleep(1.5)

            # Get all book links on this page
            book_elements = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod h3 a')
            book_links = []
            for elem in book_elements:
                href = elem.get_attribute('href')
                # Normalize URL
                if not href.startswith('http'):
                    href = BASE_URL + '/catalogue/' + href.split('catalogue/')[-1]
                book_links.append(href)

            print(f"  Found {len(book_links)} books on page {page_num}")

            for book_url in book_links:
                scraped_count += 1

                # Skip if already in DB (avoid duplicates)
                if Book.objects.filter(book_url=book_url).exists():
                    print(f"  Skipping (already exists): {book_url}")
                    continue

                try:
                    detail = scrape_book_detail(driver, book_url)
                    book = Book.objects.create(
                        title=detail['title'],
                        rating=detail['rating'],
                        price=detail['price'],
                        availability=detail['availability'],
                        description=detail['description'],
                        genre=detail['genre'],
                        cover_image_url=detail['cover_image_url'],
                        book_url=book_url
                    )
                    print(f"  Saved: {book.title}")

                    # Generate AI insights (summary, genre, sentiment)
                    try:
                        generate_all_insights(book)
                        print(f"  AI insights generated for: {book.title}")
                    except Exception as e:
                        print(f"  AI insights failed for {book.title}: {e}")

                    # Generate embeddings and store in ChromaDB
                    try:
                        embed_and_store_book(book)
                        print(f"  Embeddings stored for: {book.title}")
                    except Exception as e:
                        print(f"  Embedding failed for {book.title}: {e}")

                    new_count += 1

                except Exception as e:
                    print(f"  Error scraping {book_url}: {e}")

    finally:
        driver.quit()

    print(f"\nDone. Scraped {scraped_count} books, {new_count} new books added.")
    return {"scraped": scraped_count, "new": new_count}


if __name__ == '__main__':
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    scrape_books(num_pages=pages)
