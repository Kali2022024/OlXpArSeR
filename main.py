"""
Головний файл для запуску парсера цін
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Optional, List

from config import ParserConfig, DEFAULT_CONFIG
from olx_parser import OlxPriceParser
from models import ParsingResult, Category
from excel_exporter import ExcelExporter

class PriceParserManager:
    """Менеджер для управління парсером цін"""
    
    def __init__(self):
        self.config = self.load_config()
        self.parser: Optional[OlxPriceParser] = None
    
    def load_config(self) -> ParserConfig:
        """Завантаження конфігурації"""
        # Тут можна додати завантаження з файлу або змінних середовища
        return DEFAULT_CONFIG
    
    def setup_parser(self, base_url: str):
        """Налаштування парсера"""
        self.config.base_url = base_url
        self.parser = OlxPriceParser(self.config)
    
    async def show_categories(self) -> list:
        """Показує доступні категорії та повертає список"""
        if not self.parser:
            raise ValueError("Парсер не налаштований. Використайте setup_parser()")
        
        async with self.parser as parser:
            categories = await parser.get_categories()
            
            if categories:
                print(f"\n📁 Доступні категорії ({len(categories)}):")
                for i, category in enumerate(categories, 1):
                    print(f"   {i}. {category.name}")
                    print(f"      URL: {category.url}")
                print(f"💡 Для парсингу ВСІХ категорій введіть: 100")
                print()
            else:
                print("❌ Не знайдено категорій")
            
            return categories
    
    async def parse_specific_category(self, category_index: int) -> ParsingResult:
        """Парсинг конкретної категорії за індексом"""
        if not self.parser:
            raise ValueError("Парсер не налаштований. Використайте setup_parser()")
        
        # Отримуємо категорії
        categories = await self.show_categories()
        
        if not categories or category_index < 1 or category_index > len(categories):
            raise ValueError(f"Невірний індекс категорії: {category_index}")
        
        selected_category = categories[category_index - 1]
        print(f"\n🎯 Обрана категорія: {selected_category.name}")
        
        # Парсимо тільки обрану категорію
        async with self.parser as parser:
            result = await parser.parse_specific_category(selected_category)
            return result
    
    async def run_parsing(self) -> ParsingResult:
        """Запуск парсингу"""
        if not self.parser:
            raise ValueError("Парсер не налаштований. Використайте setup_parser()")
        
        async with self.parser as parser:
            result = await parser.parse_catalog()
            return result
    
    def save_results(self, result: ParsingResult, filename: Optional[str] = None, essential_only: bool = False):
        """Збереження результатів"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parsing_results_{timestamp}.json"
        
        # Створення директорії для результатів
        os.makedirs(self.config.output_directory, exist_ok=True)
        filepath = os.path.join(self.config.output_directory, filename)
        
        # Вибір даних для збереження
        if essential_only:
            data_to_save = {
                "success": result.success,
                "products": result.get_essential_products_data(),
                "total_products": result.total_products,
                "parsing_time": result.parsing_time,
                "errors": result.errors
            }
        else:
            data_to_save = result.to_dict()
        
        # Збереження в JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        print(f"Результати збережено в {filepath}")
        return filepath
    
    def save_results_excel(self, result: ParsingResult, category_name: str) -> str:
        """Збереження результатів в Excel формат"""
        try:
            exporter = ExcelExporter()
            filepath = exporter.export_to_excel(result, self.config.output_directory, category_name)
            print(f"Результати експортовано в Excel: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Помилка при експорті в Excel: {e}")
            return None

async def process_parsing_result(manager: PriceParserManager, result: ParsingResult, category: Category):
    """Обробляє результат парсингу та зберігає дані"""
    if result.success:
        print(f"\n✅ Парсинг успішно завершено!")
        print(f"📊 Знайдено товарів: {result.total_products}")
        print(f"⏱️  Час парсингу: {result.parsing_time:.2f} сек")
        
        # Показуємо приклад знайдених даних
        if result.products:
            print(f"\n📋 Приклад знайденого товару:")
            first_product = result.products[0]
            print(f"   Назва: {first_product.name}")
            print(f"   Ціна: {first_product.price} {first_product.currency}")
            print(f"   Посилання: {first_product.product_url}")
            print(f"   Наявність: {'✅' if first_product.availability else '❌'}")
            if first_product.sku:
                print(f"   Артикул: {first_product.sku}")
        
        # Збереження результатів
        print(f"\n💾 Збереження результатів...")
        
        # Зберігаємо повні дані
        full_file = manager.save_results(result, f"olx_{category.name.lower().replace(' ', '_')}_full.json")
        
        # Зберігаємо тільки основні дані
        essential_file = manager.save_results(result, f"olx_{category.name.lower().replace(' ', '_')}_essential.json", essential_only=True)
        
        # Експортуємо в Excel
        excel_file = manager.save_results_excel(result, category.name)
        
        print(f"📁 Повні дані: {full_file}")
        print(f"📁 Основні дані: {essential_file}")
        if excel_file:
            print(f"📊 Excel файл: {excel_file}")
        
    else:
        print(f"\n❌ Помилка при парсингу:")
        for error in result.errors:
            print(f"   - {error}")

async def parse_all_categories(manager: PriceParserManager, categories: List[Category]):
    """Парсить всі категорії по черзі"""
    total_categories = len(categories)
    successful_categories = 0
    failed_categories = 0
    
    print(f"\n🚀 Початок парсингу {total_categories} категорій...")
    print("=" * 60)
    
    for i, category in enumerate(categories, 1):
        try:
            print(f"\n📊 [{i}/{total_categories}] Парсинг категорії: {category.name}")
            print(f"   URL: {category.url}")
            
            # Парсимо категорію
            result = await manager.parse_specific_category(i)
            
            if result.success:
                print(f"✅ Категорія {category.name} успішно оброблена!")
                print(f"   📊 Знайдено товарів: {result.total_products}")
                print(f"   ⏱️  Час парсингу: {result.parsing_time:.2f} сек")
                
                # Зберігаємо результати
                await process_parsing_result(manager, result, category)
                
                successful_categories += 1
            else:
                print(f"❌ Помилка при парсингу категорії {category.name}:")
                for error in result.errors:
                    print(f"   - {error}")
                failed_categories += 1
            
            # Невелика пауза між категоріями
            if i < total_categories:
                print(f"⏳ Пауза 3 секунди перед наступною категорією...")
                await asyncio.sleep(3)
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Критична помилка при парсингу категорії {category.name}: {e}")
            failed_categories += 1
            continue
    
    # Підсумкова статистика
    print("\n" + "=" * 60)
    print("🏁 ПАРСИНГ ВСІХ КАТЕГОРІЙ ЗАВЕРШЕНО!")
    print(f"✅ Успішно оброблено: {successful_categories}")
    print(f"❌ Помилки: {failed_categories}")
    print(f"📊 Всього категорій: {total_categories}")
    print("=" * 60)

async def main():
    """Головна функція"""
    print("=== Парсер цін з OLX.ua ===")
    print("Збираємо основні дані про товари:")
    print("✅ Назва товару")
    print("✅ Поточна ціна")
    print("✅ Посилання на товар")
    print("✅ Наявність товару")
    print("✅ Артикул / код товару")
    print("📊 Експорт в Excel з гіперпосиланнями")
    print()
    
    # Отримання вхідних даних від користувача
    base_url = input("Введіть посилання на сайт OLX.ua: ").strip()
    if not base_url:
        print("Помилка: Необхідно вказати посилання на сайт")
        return
    
    # Створення та налаштування парсера
    manager = PriceParserManager()
    manager.setup_parser(base_url)
    
    print(f"\n🔍 Аналіз сайту: {base_url}")
    
    try:
        # Показуємо доступні категорії
        categories = await manager.show_categories()
        
        if not categories:
            print("❌ Не вдалося отримати категорії")
            return
        
        # Користувач обирає категорію
        while True:
            try:
                choice = input(f"Виберіть номер категорії (1-{len(categories)}) або введіть 100 для парсингу всіх категорій: ").strip()
                category_index = int(choice)
                
                if 1 <= category_index <= len(categories):
                    break
                elif category_index == 100:
                    break
                else:
                    print(f"❌ Введіть число від 1 до {len(categories)} або 100 для всіх категорій")
            except ValueError:
                print("❌ Введіть коректне число")
        
        # Перевіряємо чи обрано парсинг всіх категорій
        if category_index == 100:
            print(f"\n🚀 Запуск парсингу ВСІХ категорій ({len(categories)})...")
            await parse_all_categories(manager, categories)
        else:
            # Парсинг однієї категорії
            selected_category = categories[category_index - 1]
            print(f"\n🎯 Обрана категорія: {selected_category.name}")
            print(f"   URL: {selected_category.url}")
            
            # Парсинг обраної категорії
            print(f"\n🚀 Початок парсингу категорії: {selected_category.name}")
            
            result = await manager.parse_specific_category(category_index)
            
            if result.success:
                await process_parsing_result(manager, result, selected_category)
            else:
                print(f"\n❌ Помилка при парсингу:")
                for error in result.errors:
                    print(f"   - {error}")
                
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
