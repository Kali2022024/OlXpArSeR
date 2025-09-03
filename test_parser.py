"""
Тестовий файл для демонстрації роботи парсера
"""
import asyncio
import json
from decimal import Decimal

from models import Product, Category, ParsingResult
from config import ParserConfig

async def test_models():
    """Тестування моделей даних"""
    print("=== Тестування моделей даних ===")
    
    # Створення тестового товару
    product = Product(
        name="iPhone 15 Pro Max 256GB",
        price=Decimal("45999.99"),
        product_url="https://example-shop.com/iphone-15-pro-max",
        availability=True,
        sku="IP15PM-256GB",
        category="Смартфони",
        brand="Apple",
        description="Новий iPhone 15 Pro Max з титановим корпусом"
    )
    
    print(f"✅ Товар створено: {product.name}")
    print(f"   Ціна: {product.price} {product.currency}")
    print(f"   URL: {product.product_url}")
    print(f"   Наявність: {'✅' if product.availability else '❌'}")
    print(f"   Артикул: {product.sku}")
    
    # Тестування конвертації в словник
    product_dict = product.to_dict()
    print(f"\n📊 Товар як словник:")
    print(json.dumps(product_dict, ensure_ascii=False, indent=2))
    
    # Тестування основних даних
    essential_data = product.get_essential_data()
    print(f"\n🎯 Основні дані:")
    print(json.dumps(essential_data, ensure_ascii=False, indent=2))
    
    # Створення тестової категорії
    category = Category(
        name="Смартфони",
        url="https://example-shop.com/smartphones",
        product_count=150
    )
    
    print(f"\n📁 Категорія створена: {category.name}")
    print(f"   URL: {category.url}")
    print(f"   Кількість товарів: {category.product_count}")
    
    # Створення результату парсингу
    result = ParsingResult(
        success=True,
        products=[product],
        categories=[category],
        total_products=1,
        total_categories=1,
        parsing_time=2.5
    )
    
    print(f"\n📈 Результат парсингу:")
    print(f"   Успіх: {'✅' if result.success else '❌'}")
    print(f"   Товарів: {result.total_products}")
    print(f"   Категорій: {result.total_categories}")
    print(f"   Час: {result.parsing_time} сек")
    
    # Тестування основних даних результатів
    essential_products = result.get_essential_products_data()
    print(f"\n🎯 Основні дані про товари:")
    print(json.dumps(essential_products, ensure_ascii=False, indent=2))

async def test_config():
    """Тестування конфігурації"""
    print("\n=== Тестування конфігурації ===")
    
    config = ParserConfig(
        base_url="https://example-shop.com",
        max_concurrent_requests=5,
        delay_between_requests=1.5,
        parse_entire_catalog=True,
        output_directory="test_output",
        log_level="DEBUG"
    )
    
    print(f"✅ Конфігурація створена:")
    print(f"   Базовий URL: {config.base_url}")
    print(f"   Максимум запитів: {config.max_concurrent_requests}")
    print(f"   Затримка: {config.delay_between_requests} сек")
    print(f"   Весь каталог: {'✅' if config.parse_entire_catalog else '❌'}")
    print(f"   Вихідна директорія: {config.output_directory}")
    print(f"   Рівень логування: {config.log_level}")

async def main():
    """Головна тестова функція"""
    print("🧪 Тестування парсера цін")
    print("=" * 50)
    
    await test_models()
    await test_config()
    
    print("\n" + "=" * 50)
    print("✅ Всі тести пройдені успішно!")
    print("\n💡 Для запуску реального парсера використайте:")
    print("   python main.py")

if __name__ == "__main__":
    asyncio.run(main())
