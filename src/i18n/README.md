# Internationalization (i18n)

This directory contains the internationalization support for the ISLR Calculator.

## Available Languages

- **English** (`en`) - Default
- **Spanish** (`es`)

## Usage

Set the `ISLR_LANG` environment variable to your preferred language:

```bash
# Use English (default)
python main.py

# Use Spanish
export ISLR_LANG=es
python main.py

# Or inline
ISLR_LANG=es python main.py
```

## Adding a New Language

1. Create a new JSON file in `locales/` directory (e.g., `pt.json` for Portuguese)
2. Copy the structure from `en.json`
3. Translate all the strings to the new language
4. Save the file with UTF-8 encoding
5. Use it: `ISLR_LANG=pt python main.py`

## String Interpolation

Some strings support variable interpolation using `{variable}` syntax:

```json
"income_prompt": "Enter your monthly income in {currency}:"
```

Usage in code:

```python
from src.i18n import t
t("input.income_prompt", currency="USD")
```

## Development

The i18n module is initialized once when imported and loads translations based on the `ISLR_LANG` environment variable. If the specified language file doesn't exist, it falls back to English.

For the full API, see `__init__.py`.
