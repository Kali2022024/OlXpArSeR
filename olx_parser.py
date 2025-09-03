"""
Спеціалізований парсер для OLX.ua
"""
import asyncio
import re
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from decimal import Decimal

from base_parser import BasePriceParser
from models import Product, Category, ParsingResult
from config import ParserConfig

class OlxPriceParser(BasePriceParser):
    """Парсер для OLX.ua"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        self.logger.info("Ініціалізовано OlxPriceParser для OLX.ua")
    
    async def get_categories(self) -> List[Category]:
        """Отримання списку категорій з OLX.ua"""
        categories = []
        try:
            # Отримуємо головну сторінку
            soup = await self.fetch_page(self.config.base_url)
            if not soup:
                return categories
            
            # Шукаємо основні категорії в меню
            category_container = soup.find('div', {'data-testid': 'home-categories-menu-row'})
            if category_container:
                category_links = category_container.find_all('a', class_=re.compile(r'css-.*'))
                
                for link in category_links:
                    href = link.get('href', '')
                    text_elem = link.find('p', class_='css-yrygxu')
                    
                    if text_elem and href and not href.startswith('http'):
                        text = text_elem.get_text(strip=True)
                        if text and len(text) > 2:
                            self.logger.debug(f"Знайдено категорію: {text}, href: {href}")
                            category_url = self.make_absolute_url(href, self.config.base_url)
                            self.logger.debug(f"Сформовано URL категорії: {category_url}")
                            category = Category(
                                name=text,
                                url=category_url
                            )
                            categories.append(category)
            
            self.logger.info(f"Знайдено {len(categories)} категорій")
            
        except Exception as e:
            self.logger.error(f"Помилка при отриманні категорій: {e}")
        
        return categories
    
    async def get_products_from_category(self, category: Category) -> List[Product]:
        """Отримання товарів з конкретної категорії OLX.ua з пагінацією"""
        all_products = []
        page = 1
        current_url = category.url  # Зберігаємо поточний URL для пагінації
        
        try:
            while True:
                # Формуємо URL з номером сторінки
                if page == 1:
                    page_url = current_url
                else:
                    # Додаємо параметр сторінки
                    if '?' in current_url:
                        page_url = f"{current_url}&page={page}"
                    else:
                        page_url = f"{current_url}?page={page}"
                
                self.logger.info(f"Парсинг сторінки {page}: {page_url}")
                self.logger.debug(f"Поточний URL для пагінації: {current_url}")
                
                # Отримуємо сторінку
                soup = await self.fetch_page(page_url)
                if not soup:
                    self.logger.warning(f"Не вдалося отримати сторінку {page}")
                    break
                
                # Перевіряємо чи є на сторінці кнопка "Показати всі оголошення" (тільки на першій сторінці)
                if page == 1:
                    show_all_link = soup.find('a', {'data-testid': 'sub-cat-1-root-link'})
                    if show_all_link:
                        show_all_url = show_all_link.get('href')
                        if show_all_url:
                            show_all_url = self.make_absolute_url(show_all_url, self.config.base_url)
                            self.logger.info(f"Знайдено посилання 'Показати всі': {show_all_url}")
                            
                            # Оновлюємо поточний URL для пагінації
                            old_url = current_url
                            current_url = show_all_url
                            self.logger.info(f"Оновлено URL для пагінації: {old_url} -> {current_url}")
                            
                            # Отримуємо сторінку з усіма оголошеннями
                            soup = await self.fetch_page(show_all_url)
                            if not soup:
                                self.logger.warning("Не вдалося отримати сторінку з усіма оголошеннями")
                                break
                
                # Шукаємо елементи товарів (оголошень)
                product_elements = soup.find_all('div', {'data-cy': 'l-card'})
                
                if not product_elements:
                    # Альтернативний пошук
                    product_elements = soup.find_all('div', class_=re.compile(r'css-.*'))
                
                if not product_elements:
                    self.logger.warning(f"Не знайдено товарів на сторінці {page}")
                    break
                
                self.logger.debug(f"Сторінка {page}: знайдено {len(product_elements)} елементів товарів")
                
                # Обробляємо знайдені товари
                page_products = []
                for element in product_elements:
                    product = self.extract_product_data_from_element(element, self.config.base_url)
                    if product:
                        page_products.append(product)
                
                if page_products:
                    all_products.extend(page_products)
                    self.logger.info(f"Сторінка {page}: знайдено {len(page_products)} товарів")
                else:
                    self.logger.warning(f"Сторінка {page}: не знайдено товарів")
                    break
                
                # Перевіряємо чи є наступна сторінка (покращений пошук)
                self.logger.debug(f"Шукаємо наступну сторінку на сторінці {page}")
                next_page_link = self.find_next_page_link(soup)
                if not next_page_link:
                    self.logger.info(f"Наступна сторінка не знайдена, завершуємо пагінацію")
                    break
                
                self.logger.info(f"Знайдено посилання на наступну сторінку: {next_page_link.get('href', 'N/A')}")
                page += 1
                
                # Обмежуємо кількість сторінок для тестування
                if page > 25:  # Збільшуємо ліміт до 25 сторінок
                    self.logger.info("Досягнуто ліміт сторінок (25)")
                    break
                
                # Невелика пауза між сторінками
                await asyncio.sleep(1)
            
            self.logger.info(f"Всього знайдено {len(all_products)} товарів в категорії {category.name}")
            
        except Exception as e:
            self.logger.error(f"Помилка при парсингу категорії {category.name}: {e}")
        
        return all_products
    
    def find_next_page_link(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Знаходить посилання на наступну сторінку в OLX"""
        try:
            # Різні варіанти пошуку кнопки "Наступна"
            next_page_selectors = [
                # Пошук за текстом
                soup.find('a', string=re.compile(r'Наступна|Следующая|Next', re.IGNORECASE)),
                # Пошук за aria-label
                soup.find('a', {'aria-label': re.compile(r'Наступна|Следующая|Next', re.IGNORECASE)}),
                # Пошук за data-testid
                soup.find('a', {'data-testid': 'pagination-forward'}),
                # Пошук за класом та текстом
                soup.find('a', class_=re.compile(r'css-.*'), string=re.compile(r'Наступна|Следующая|Next', re.IGNORECASE)),
                # Пошук за href що містить page=
                soup.find('a', href=re.compile(r'page=\d+')),
            ]
            
            # Знаходимо перший знайдений елемент
            for selector in next_page_selectors:
                if selector:
                    self.logger.debug(f"Знайдено посилання на наступну сторінку: {selector.get('href', 'N/A')}")
                    return selector
            
            # Додатковий пошук - шукаємо всі посилання та перевіряємо чи містять вони номер сторінки
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if 'page=' in href:
                    # Перевіряємо чи це не поточна сторінка
                    current_page_match = re.search(r'page=(\d+)', href)
                    if current_page_match:
                        page_num = int(current_page_match.group(1))
                        # Якщо номер сторінки більший за поточний, то це наступна сторінка
                        if page_num > 1:  # Приблизна перевірка
                            self.logger.debug(f"Знайдено посилання на сторінку {page_num}: {href}")
                            return link
            
            self.logger.debug("Посилання на наступну сторінку не знайдено")
            return None
            
        except Exception as e:
            self.logger.error(f"Помилка при пошуку наступної сторінки: {e}")
            return None
    
    def extract_product_data_from_element(self, element: Tag, base_url: str) -> Optional[Product]:
        """Витягування даних про товар з HTML елемента OLX.ua"""
        try:
            # Назва товару
            name_elem = element.find('h6') or element.find('h5') or element.find('h4')
            if not name_elem:
                name_elem = element.find('a', href=True)
            
            name = ""
            if name_elem:
                name = self.clean_text(name_elem.get_text())
            
            if not name:
                return None
            
            # Ціна
            price_elem = element.find(string=re.compile(r'грн|₴|UAH'))
            if not price_elem:
                price_elem = element.find(class_=re.compile(r'price|cost'))
            
            price_text = ""
            if price_elem:
                if hasattr(price_elem, 'get_text'):
                    price_text = price_elem.get_text()
                else:
                    price_text = str(price_elem)
            
            # Пошук ціни в тексті
            if not price_text:
                element_text = element.get_text()
                # Покращений регулярний вираз для пошуку цін
                price_match = re.search(r'(\d+(?:[\s,]*\d+)*)\s*(?:грн|₴|UAH)', element_text)
                if price_match:
                    price_text = price_match.group()
                else:
                    # Альтернативний пошук - просто числа
                    price_match = re.search(r'(\d+(?:[\s,]*\d+)*)', element_text)
                    if price_match:
                        price_text = price_match.group() + " грн"
            
            price = self.extract_price(price_text)
            
            # Посилання на товар
            link_elem = element.find('a', href=True)
            product_url = ""
            if link_elem:
                href = link_elem.get('href')
                if href and not href.startswith('#'):
                    product_url = self.make_absolute_url(href, base_url)
            
            if not product_url:
                return None
            
            # Наявність (за замовчуванням True для OLX)
            availability = True
            
            # Артикул (ID оголошення)
            sku = ""
            sku_elem = element.find('a', href=True)
            if sku_elem:
                href = sku_elem.get('href', '')
                sku_match = re.search(r'/uk/obyavlenie/([^/]+)', href)
                if sku_match:
                    sku = sku_match.group(1)
            
            # Створюємо об'єкт товару
            product = Product(
                name=name,
                price=price if price else Decimal("0"),
                product_url=product_url,
                availability=availability,
                sku=sku
            )
            
            return product
            
        except Exception as e:
            self.logger.error(f"Помилка при витягуванні даних про товар: {e}")
            return None
    
    def extract_price(self, price_text: str) -> Optional[Decimal]:
        """Витягування ціни з тексту OLX.ua"""
        try:
            if not price_text:
                return None
            
            # Видаляємо зайві символи та конвертуємо валюту
            price_text = price_text.replace('грн', '').replace('₴', '').replace('UAH', '').strip()
            
            # Шукаємо числа - змінюємо регулярний вираз щоб брати всі цифри
            # Використовуємо (\d+(?:[\s,]*\d+)*) для пошуку всіх цифр
            price_match = re.search(r'(\d+(?:[\s,]*\d+)*)', price_text)
            if price_match:
                price_str = price_match.group(1).replace(' ', '').replace(',', '')
                return Decimal(price_str)
                
        except (ValueError, AttributeError, TypeError):
            self.logger.warning(f"Не вдалося розпарсити ціну: {price_text}")
        
        return None