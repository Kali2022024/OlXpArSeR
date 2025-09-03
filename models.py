"""
Моделі даних для парсера цін
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

@dataclass
class Product:
    """Модель товару з основними даними"""
    # Обов'язкові поля
    name: str                    # Назва товару
    price: Decimal               # Поточна ціна
    product_url: str             # Посилання на товар
    
    # Опціональні поля
    availability: bool = True     # Наявність товару
    sku: str = ""                # Артикул / код товару
    
    # Додаткові поля
    id: str = ""
    currency: str = "UAH"
    category: str = ""
    subcategory: str = ""
    brand: str = ""
    description: str = ""
    image_url: str = ""
    rating: Optional[float] = None
    review_count: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    parsed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує товар в словник"""
        return {
            "name": self.name,
            "price": str(self.price),
            "product_url": self.product_url,
            "availability": self.availability,
            "sku": self.sku,
            "id": self.id,
            "currency": self.currency,
            "category": self.category,
            "subcategory": self.subcategory,
            "brand": self.brand,
            "description": self.description,
            "image_url": self.image_url,
            "rating": self.rating,
            "review_count": self.review_count,
            "attributes": self.attributes,
            "parsed_at": self.parsed_at.isoformat()
        }
    
    def get_essential_data(self) -> Dict[str, Any]:
        """Отримує тільки основні дані про товар"""
        return {
            "name": self.name,
            "price": str(self.price),
            "product_url": self.product_url,
            "availability": self.availability,
            "sku": self.sku
        }

@dataclass
class Category:
    """Модель категорії"""
    name: str
    url: str
    parent_category: Optional[str] = None
    subcategories: List[str] = field(default_factory=list)
    product_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує категорію в словник"""
        return {
            "name": self.name,
            "url": self.url,
            "parent_category": self.parent_category,
            "subcategories": self.subcategories,
            "product_count": self.product_count
        }

@dataclass
class ParsingResult:
    """Результат парсингу"""
    success: bool
    products: List[Product] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_products: int = 0
    total_categories: int = 0
    parsing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує результат в словник"""
        return {
            "success": self.success,
            "products": [product.to_dict() for product in self.products],
            "categories": [category.to_dict() for category in self.categories],
            "errors": self.errors,
            "total_products": self.total_products,
            "total_categories": self.total_categories,
            "parsing_time": self.parsing_time
        }
    
    def get_essential_products_data(self) -> List[Dict[str, Any]]:
        """Отримує тільки основні дані про товари"""
        return [product.get_essential_data() for product in self.products]
