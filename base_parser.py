"""
Базовий клас для парсерів цін
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup

from models import Product, Category, ParsingResult
from config import ParserConfig

class BasePriceParser(ABC):
    """Базовий клас для парсерів цін"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Налаштування логування
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('parser.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    async def __aenter__(self):
        """Асинхронний контекстний менеджер - вхід"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронний контекстний менеджер - вихід"""
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[Category]:
        """Отримання списку категорій - абстрактний метод"""
        pass
    
    @abstractmethod
    async def get_products_from_category(self, category: Category) -> List[Product]:
        """Отримання товарів з конкретної категорії - абстрактний метод"""
        pass
    
    async def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Отримання сторінки з URL"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status == 200:
                        html = await response.text()
                        return BeautifulSoup(html, 'html.parser')
                    else:
                        self.logger.warning(f"HTTP {response.status} для {url}")
                        return None
        except Exception as e:
            self.logger.error(f"Помилка при отриманні {url}: {e}")
            return None
    
    def make_absolute_url(self, href: str, base_url: str) -> str:
        """Перетворює відносний URL в абсолютний"""
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            # Перевіряємо чи href починається з /uk/ і base_url вже містить /uk
            if href.startswith('/uk/') and '/uk' in base_url:
                # Видаляємо /uk з href щоб уникнути дублювання
                original_href = href
                href = href[3:]  # Видаляємо перші 3 символи '/uk'
                self.logger.debug(f"Виправлено дублювання /uk: {original_href} -> {href}")
            
            result_url = base_url.rstrip('/') + href
            self.logger.debug(f"make_absolute_url: {href} + {base_url} = {result_url}")
            return result_url
        else:
            result_url = base_url.rstrip('/') + '/' + href
            self.logger.debug(f"make_absolute_url: {href} + {base_url} = {result_url}")
            return result_url
    
    def clean_text(self, text: str) -> str:
        """Очищає текст від зайвих символів"""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    async def parse_specific_category(self, category: Category) -> ParsingResult:
        """Парсинг конкретної категорії"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info(f"Початок парсингу категорії: {category.name}")
            
            # Отримуємо товари з категорії
            products = await self.get_products_from_category(category)
            
            # Розраховуємо час парсингу
            parsing_time = asyncio.get_event_loop().time() - start_time
            
            # Створюємо результат
            result = ParsingResult(
                success=True,
                products=products,
                total_products=len(products),
                parsing_time=parsing_time
            )
            
            self.logger.info(f"Парсинг категорії {category.name} завершено. Знайдено {len(products)} товарів")
            return result
            
        except Exception as e:
            parsing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Помилка при парсингу категорії {category.name}: {e}"
            self.logger.error(error_msg)
            
            result = ParsingResult(
                success=False,
                errors=[error_msg],
                parsing_time=parsing_time
            )
            return result
    
    async def parse_catalog(self) -> ParsingResult:
        """Парсинг всього каталогу"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info("Початок парсингу всього каталогу")
            
            # Отримуємо категорії
            categories = await self.get_categories()
            
            all_products = []
            all_errors = []
            
            # Парсимо кожну категорію
            for category in categories:
                try:
                    products = await self.get_products_from_category(category)
                    all_products.extend(products)
                    self.logger.info(f"Категорія {category.name}: знайдено {len(products)} товарів")
                except Exception as e:
                    error_msg = f"Помилка при парсингу категорії {category.name}: {e}"
                    all_errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Розраховуємо час парсингу
            parsing_time = asyncio.get_event_loop().time() - start_time
            
            # Створюємо результат
            result = ParsingResult(
                success=len(all_errors) == 0,
                products=all_products,
                categories=categories,
                errors=all_errors,
                total_products=len(all_products),
                total_categories=len(categories),
                parsing_time=parsing_time
            )
            
            self.logger.info(f"Парсинг каталогу завершено. Знайдено {len(all_products)} товарів в {len(categories)} категоріях")
            return result
            
        except Exception as e:
            parsing_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Критична помилка при парсингу каталогу: {e}"
            self.logger.error(error_msg)
            
            result = ParsingResult(
                success=False,
                errors=[error_msg],
                parsing_time=parsing_time
            )
            return result
