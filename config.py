"""
Конфігурація для парсера цін
"""
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ParserConfig:
    """Конфігурація парсера"""
    # Базові налаштування
    base_url: str
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Налаштування запитів
    request_timeout: int = 30
    max_concurrent_requests: int = 10
    delay_between_requests: float = 1.0
    
    # Налаштування парсингу
    categories_to_parse: Optional[List[str]] = None
    parse_entire_catalog: bool = True
    
    # Налаштування збереження
    output_directory: str = "parsed_data"
    save_format: str = "json"  # json, csv, xml
    
    # Налаштування логування
    log_level: str = "INFO"
    log_file: str = "parser.log"

# Приклад конфігурації
DEFAULT_CONFIG = ParserConfig(
    base_url="",
    categories_to_parse=["electronics", "clothing", "books"],
    parse_entire_catalog=True
)
