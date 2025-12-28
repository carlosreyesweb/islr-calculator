# 🇻🇪 Venezuelan Income Tax Calculator (ISLR)

A friendly terminal-based calculator for Venezuelan individual income tax (Impuesto Sobre la Renta - ISLR) with a beautiful user interface powered by Rich.

## Features

- 💰 Calculate income tax from monthly income (VES or USD)
- 📊 View tax brackets in UT and Bs.
- 🎨 Beautiful terminal UI
- 📈 Shows effective tax rate and net income
- 🔢 Optional calculation breakdown

## Installation

1. Clone the repository:

```bash
git clone https://github.com/carlosreyesweb/islr-calculator.git
cd islr-calculator
```

2. Create a `.env` file with these values:

```bash
UT_VALUE=43.0                    # Current UT value in Bs.
USD_TO_VES=295                   # Exchange rate from Central Bank of Venezuela
STANDARD_DEDUCTION_UT=775        # Standard deduction
```

3. Install dependencies:

```bash
uv sync
# or
pip install -e .
```

## Usage

Run the calculator:

```bash
python main.py
# or with uv
uv run main.py
```

## License

This project is open source and available under the MIT License.

## Disclaimer

This calculator is for informational purposes only. Please consult with a qualified tax professional for official tax advice and calculations. Tax rates and brackets may change over time.
