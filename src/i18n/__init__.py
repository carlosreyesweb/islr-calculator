"""
Internationalization (i18n) module for ISLR Calculator
Loads translations from JSON files based on ISLR_LANG environment variable
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_translations = {}
_current_language = os.getenv("ISLR_LANG", "en")


def load_translations():
    """Load translations for current language"""
    locale_dir = Path(__file__).parent / "locales"
    locale_file = locale_dir / f"{_current_language}.json"

    # Fallback to English if language file doesn't exist
    if not locale_file.exists():
        locale_file = locale_dir / "en.json"

    with open(locale_file, "r", encoding="utf-8") as f:
        return json.load(f)


_translations = load_translations()


def t(key: str, **kwargs) -> str:
    """
    Get translation by key with optional interpolation

    Args:
        key: Dot-notation key (e.g., "menu.prompt", "input.income_prompt")
        **kwargs: Variables for string interpolation

    Returns:
        Translated string with interpolated values

    Examples:
        t("menu.prompt")
        t("input.income_prompt", currency="USD")
        t("results.dependent_credits", count=2)
    """
    keys = key.split(".")
    value = _translations

    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, key)
        else:
            return key

    if isinstance(value, str) and kwargs:
        return value.format(**kwargs)

    return value if isinstance(value, str) else key


def get_current_language() -> str:
    """Get the current language code"""
    return _current_language
