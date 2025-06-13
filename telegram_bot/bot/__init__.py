"""Main bot package."""
from .config import Config
from .config.pairs import TRADING_PAIRS, PAIR_DISPLAY_NAMES, PAIR_DESCRIPTIONS, DEFAULT_PAIRS, PAIR_CATEGORIES
from .main import main

__all__ = [
    'Config',
    'TRADING_PAIRS',
    'PAIR_DISPLAY_NAMES',
    'PAIR_DESCRIPTIONS',
    'DEFAULT_PAIRS',
    'PAIR_CATEGORIES',
    'main'
] 