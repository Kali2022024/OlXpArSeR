# Парсер цін з інтернет-магазинів

Автоматизована система для збору цін з інтернет-магазинів з використанням асинхронних запитів та парсингу HTML.

## 🎯 Основні можливості

Система збирає наступні дані про товари:

### ✅ Обов'язкові поля:
- **Назва товару** - повна назва товару
- **Поточна ціна** - актуальна вартість товару
- **Посилання на товар** - URL сторінки товару

### 🔍 Опціональні поля:
- **Наявність товару** - чи є товар в наявності
- **Артикул/код товару** - унікальний ідентифікатор товару

### 📊 Додаткові поля:
- Категорія та підкатегорія
- Бренд
- Опис
- Зображення
- Рейтинг та кількість відгуків
- Атрибути товару

### 📈 Формати експорту:
- **JSON** - повні та основні дані
- **Excel (.xlsx)** - структуровані дані з гіперпосиланнями

## 🚀 Технології

- **Python 3.8+** - основна мова програмування
- **aiohttp** - асинхронні HTTP запити
- **BeautifulSoup4** - парсинг HTML/XML
- **lxml** - швидкий XML/HTML парсер
- **asyncio** - асинхронне програмування
- **openpyxl** - робота з Excel файлами

## 📦 Встановлення

1. Клонуйте репозиторій:
```bash
git clone <repository-url>
cd Parserpriceinsite
```

2. Встановіть залежності:
```bash
pip install -r requirements.txt
```

## 🎮 Використання

### Excel Експорт

Система автоматично створює Excel файли з наступними колонками:

| Колонка | Опис | Приклад |
|---------|------|---------|
| **Назва товару** | Повна назва товару | "iPhone 14 Pro 128GB" |
| **Ціна** | Поточна вартість | "45,999 грн" |
| **Наявність** | Статус наявності | "✅ В наявності" |
| **Посилання** | Гіперпосилання на товар | "Перейти до товару" |

**Особливості Excel експорту:**
- Автоматичне форматування заголовків
- Гіперпосилання на товари (клікабельні)
- Чергування кольорів рядків для кращої читабельності
- Автоматична настройка ширини колонок
- Назва файлу включає категорію та timestamp

### Базовий запуск

```bash
python main.py
```

### Налаштування

1. **Введіть посилання на сайт** - URL головної сторінки інтернет-магазину
2. **Виберіть режим парсингу**:
   - Весь каталог - парсинг всіх доступних категорій
   - Конкретні категорії - парсинг тільки вказаних категорій

### Приклад використання

```python
from example_parser import ExamplePriceParser
from config import ParserConfig

# Налаштування конфігурації
config = ParserConfig(
    base_url="https://example-shop.com",
    max_concurrent_requests=5,
    delay_between_requests=1.0
)

# Створення та запуск парсера
async with ExamplePriceParser(config) as parser:
    result = await parser.parse_catalog()
    
    if result.success:
        print(f"Знайдено {result.total_products} товарів")
        for product in result.products:
            print(f"{product.name}: {product.price} {product.currency}")
```

## 🏗️ Архітектура

### Основні компоненти

1. **BasePriceParser** - базовий клас з загальною логікою
2. **OlxPriceParser** - спеціалізований парсер для OLX.ua
3. **Product** - модель даних товару
4. **Category** - модель даних категорії
5. **ParserConfig** - конфігурація парсера
6. **ExcelExporter** - експорт даних в Excel формат

### Структура проекту

```
Parserpriceinsite/
├── main.py              # Головний файл запуску
├── excel_exporter.py    # Експорт в Excel формат
├── models.py            # Моделі даних
├── config.py            # Конфігурація
├── requirements.txt     # Залежності
└── README.md           # Документація
```

## ⚙️ Налаштування

### Конфігурація парсера

```python
@dataclass
class ParserConfig:
    base_url: str                    # Базовий URL сайту
    user_agent: str                  # User-Agent для запитів
    request_timeout: int             # Таймаут запитів (сек)
    max_concurrent_requests: int     # Максимум одночасних запитів
    delay_between_requests: float    # Затримка між запитами (сек)
    parse_entire_catalog: bool       # Парсити весь каталог
    output_directory: str            # Директорія для результатів
    save_format: str                 # Формат збереження (json/csv/xml)
```

### Налаштування логування

```python
config = ParserConfig(
    log_level="INFO",        # DEBUG, INFO, WARNING, ERROR
    log_file="parser.log"    # Файл для логів
)
```

## 🔧 Створення власного парсера

Для створення парсера під конкретний сайт:

1. **Успадкуйте BasePriceParser**:
```python
class MyShopParser(BasePriceParser):
    def __init__(self, config: ParserConfig):
        super().__init__(config)
    
    async def get_categories(self) -> List[Category]:
        # Ваша логіка отримання категорій
        pass
    
    async def get_products_from_category(self, category: Category) -> List[Product]:
        # Ваша логіка отримання товарів
        pass
```

2. **Реалізуйте методи парсингу** під структуру конкретного сайту
3. **Налаштуйте селектори** для витягування даних

## 📊 Формати виводу

### JSON формат (основні дані)

```json
{
  "success": true,
  "products": [
    {
      "name": "iPhone 15 Pro",
      "price": "45999",
      "product_url": "https://shop.com/iphone-15-pro",
      "availability": true,
      "sku": "IP15P-256GB"
    }
  ],
  "total_products": 1,
  "parsing_time": 2.45
}
```

### JSON формат (повні дані)

```json
{
  "success": true,
  "products": [
    {
      "name": "iPhone 15 Pro",
      "price": "45999",
      "currency": "UAH",
      "category": "Смартфони",
      "brand": "Apple",
      "description": "Новий iPhone 15 Pro...",
      "image_url": "https://shop.com/images/iphone15pro.jpg",
      "rating": 4.8,
      "review_count": 127,
      "parsed_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## 🚨 Обмеження та рекомендації

### Етичні аспекти
- Дотримуйтесь robots.txt сайту
- Не перевантажуйте сервер занадто швидкими запитами
- Використовуйте затримки між запитами
- Поважайте умови використання сайту

### Технічні обмеження
- Максимум одночасних запитів: 10 (за замовчуванням)
- Мінімальна затримка між запитами: 1 секунда
- Таймаут запиту: 30 секунд

### Оптимізація продуктивності
- Використовуйте асинхронні запити
- Налаштуйте розмір пулу з'єднань
- Кешуйте результати при можливості
- Використовуйте селективний парсинг

## 🐛 Вирішення проблем

### Поширені помилки

1. **Connection timeout** - збільшіть `request_timeout`
2. **Too many requests** - збільшіть `delay_between_requests`
3. **Parser errors** - перевірте селектори та структуру HTML

### Діагностика

```python
# Увімкнення детального логування
config = ParserConfig(log_level="DEBUG")

# Перевірка доступності сайту
async with ExamplePriceParser(config) as parser:
    soup = await parser.fetch_page("https://example.com")
    if soup:
        print("Сайт доступний")
    else:
        print("Проблеми з доступом до сайту")
```

## 📈 Розширення функціональності

### Можливі покращення

- Підтримка проксі та ротації User-Agent
- Експорт в CSV/Excel формати
- База даних для зберігання результатів
- Веб-інтерфейс для управління
- Планувальник завдань
- API для інтеграції з іншими системами

### Інтеграція з базами даних

```python
# Приклад збереження в SQLite
import sqlite3

def save_to_database(products: List[Product]):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    for product in products:
        cursor.execute("""
            INSERT INTO products (name, price, url, availability, sku)
            VALUES (?, ?, ?, ?, ?)
        """, (product.name, product.price, product.product_url, 
              product.availability, product.sku))
    
    conn.commit()
    conn.close()
```

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT.

## 🤝 Внесок

Вітаються внески у вигляді:
- Повідомлень про помилки
- Запитів на нові функції
- Покращень документації
- Коду та тестів

## 📞 Підтримка

Для отримання допомоги:
1. Перевірте документацію
2. Пошукайте в існуючих issues
3. Створіть нове issue з детальним описом проблеми

---

**Примітка**: Цей парсер призначений тільки для освітніх та особистих цілей. Дотримуйтесь умов використання та законодавства при використанні.
