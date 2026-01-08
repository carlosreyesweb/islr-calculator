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
STANDARD_DEDUCTION_UT=775        # Standard deduction (reduces taxable income)
CONTRIBUTOR_CREDIT_UT=10         # Tax credit for the contributor (reduces tax)
DEPENDENT_CREDIT_UT=10           # Tax credit per dependent (reduces tax)
```

3. Configure tax brackets (optional):

The tax brackets are loaded from `tax_brackets.csv`. You can modify this file to update the brackets without changing the code:

```csv
min_ut,max_ut,rate,subtract_ut
0,1000,0.06,0
1000,1500,0.09,30
1500,2000,0.12,75
2000,2500,0.16,155
2500,3000,0.20,255
3000,4000,0.24,375
4000,6000,0.29,575
6000,inf,0.34,875
```

- `min_ut`: Minimum income in UT for this bracket
- `max_ut`: Maximum income in UT for this bracket (use `inf` for unlimited)
- `rate`: Tax rate as a decimal (e.g., 0.06 for 6%)
- `subtract_ut`: Amount to subtract in UT when calculating tax

4. Install dependencies:

```bash
uv sync # creates environment and installs dependencies
# or
python3 -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows
pip install -e .
```

## Usage

Run the calculator:

```bash
uv run main.py
# or (if an environment is already set up)
python main.py
```

## License

This project is open source and available under the MIT License.

## Disclaimer

This calculator is for informational purposes only. Please consult with a qualified tax professional for official tax advice and calculations. Tax rates and brackets may change over time.
