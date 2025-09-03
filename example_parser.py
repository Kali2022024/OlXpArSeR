"""
Приклад парсера для демонстрації базової функціональності
"""
import asyncio
import re
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from decimal import Decimal

from base_parser import BasePriceParser
from models import Product, Category, ParsingResult
from config import ParserConfig

class ExamplePriceParser(BasePriceParser):
    """Приклад парсера для демонстрації"""
    
    def __init__(self, config: ParserConfig):
        super().__init__(config)
        self.logger.info("Ініціалізовано ExamplePriceParser")
    
    async def get_categories(self) -> List[Category]:
        """Отримання списку категорій - приклад"""
        # Це приклад - в реальному проекті тут буде парсинг сайту
        categories = [
            Category(name="Електроніка", url=f"{self.config.base_url}/electronics"),
            Category(name="Одяг", url=f"{self.config.base_url}/clothing"),
            Category(name="Книги", url=f"{self.config.base_url}/books")
        ]
        
        self.logger.info(f"Знайдено {len(categories)} категорій (приклад)")
        return categories
    
    async def get_products_from_category(self, category: Category) -> List[Product]:
        """Отримання товарів з конкретної категорії - приклад"""
        # Це приклад - в реальному проекті тут буде парсинг сторінки
        products = []
        
        # Симулюємо затримку
        await asyncio.sleep(1)
        
        # Створюємо тестові товари
        for i in range(1, 6):  # 5 товарів для прикладу
            product = Product(
                name=f"Товар {i} в категорії {category.name}",
                price=Decimal(f"{100 + i * 50}.00"),
                product_url=f"{category.url}/product-{i}",
                availability=True,
                sku=f"SKU-{category.name[:3].upper()}-{i:03d}"
            )
            products.append(product)
        
        self.logger.info(f"Знайдено {len(products)} товарів в категорії {category.name}")
        return products
    
    def extract_product_data_from_element(self, element: Tag, base_url: str) -> Optional[Product]:
        """Витягування даних про товар з HTML елемента - приклад"""
        # Це приклад - в реальному проекті тут буде парсинг HTML
        try:
            # Назва товару
            name_elem = element.find('h3') or element.find('h2') or element.find('h1')
            if not name_elem:
                return None
            
            name = self.clean_text(name_elem.get_text())
            if not name:
                return None
            
            # Ціна
            price_elem = element.find(class_=re.compile(r'price|cost'))
            price = None
            if price_elem:
                price_text = price_elem.get_text()
                price = self.extract_price(price_text)
            
            # Посилання
            link_elem = element.find('a', href=True)
            if not link_elem:
                return None
            
            product_url = self.make_absolute_url(link_elem['href'], base_url)
            
            # Створюємо товар
            product = Product(
                name=name,
                price=price if price else Decimal("0"),
                product_url=product_url,
                availability=True
            )
            
            return product
            
        except Exception as e:
            self.logger.error(f"Помилка при витягуванні даних про товар: {e}")
            return None
    
    def extract_price(self, price_text: str) -> Optional[Decimal]:
        """Витягування ціни з тексту - приклад"""
        try:
            if not price_text:
                return None
            
            # Видаляємо зайві символи
            price_text = price_text.replace('грн', '').replace('₴', '').replace('UAH', '').strip()
            
            # Шукаємо числа
            price_match = re.search(r'(\d+(?:[\s,]*\d+)*)', price_text)
            if price_match:
                price_str = price_match.group(1).replace(' ', '').replace(',', '')
                return Decimal(price_str)
                
        except (ValueError, AttributeError, TypeError):
            self.logger.warning(f"Не вдалося розпарсити ціну: {price_text}")
        
        return None
