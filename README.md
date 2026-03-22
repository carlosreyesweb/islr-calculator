# Venezuelan Income Tax Calculator (ISLR)

A terminal-based calculator for Venezuelan individual income tax (Impuesto Sobre la Renta - ISLR).

## Features

- Two modes: **Declaration** (last year's actual income) and **Simulation** (project this year's tax from monthly income)
- Supports income in Bolivares (Bs.) or US Dollars (USD)
- Accounts for dependents, standard deduction, and taxpayer credits
- Shows tax owed, net income, and effective rate
- Optional 3-installment payment plan with SENIAT-correct due dates
- Optional step-by-step calculation breakdown in plain language
- View current tax brackets in UT and Bs.
- Available in English and Spanish (`ISLR_LANG=en` or `ISLR_LANG=es`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/carlosreyesweb/islr-calculator.git
cd islr-calculator
```

2. Install dependencies:

```bash
uv sync
# or
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

3. Create a `.env` file. Copy `.env.example` as a starting point:

```bash
cp .env.example .env
```

Then update the values to match the current fiscal year:

```env
ISLR_LANG=es                  # Language: en or es
UT_VALUE=43                   # Current Unidad Tributaria value in Bs.
USD_TO_VES=457.07             # Fallback USD/Bs. rate if the live fetch fails (see below)
STANDARD_DEDUCTION_UT=774     # Standard deduction in UT (reduces taxable income)
TAXPAYER_CREDIT_UT=10         # Tax credit for the taxpayer in UT (reduces tax owed)
DEPENDENT_CREDIT_UT=10        # Tax credit per dependent in UT (reduces tax owed)
INSTALLMENT_DAYS=20           # Days between installment payments from the March 31 deadline
```

### Live USD/Bs. rate

At startup the calculator automatically fetches the official BCV USD/Bs. exchange rate from [ve.dolarapi.com](https://ve.dolarapi.com). The rate and its update date are shown in the header. If the API is unreachable (no internet, timeout, etc.) it falls back silently to the `USD_TO_VES` value in your `.env`.

4. (Optional) Update tax brackets in `tax_brackets.csv` if SENIAT publishes new ones:

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

Column reference:

| Column | Description |
|---|---|
| `min_ut` | Lower bound of the bracket in UT |
| `max_ut` | Upper bound in UT (`inf` for the top bracket) |
| `rate` | Tax rate as a decimal (e.g. `0.34` for 34%) |
| `subtract_ut` | Bracket subtraction constant in UT |

## Usage

```bash
uv run main.py
# or
python main.py
```

### Declaration mode

Use this when you have your **total annual income for last year** and want to know exactly what you owe before filing at SENIAT. The calculator will show:

- Tax owed in Bs. and USD
- Net income after tax
- Effective tax rate
- Optional 3-installment payment plan with exact due dates (filing date, April 20, May 10)
- Optional step-by-step breakdown

### Simulation mode

Use this to **estimate what your tax will be** based on your current monthly income. The calculator annualizes the monthly figure and shows a projected tax. No installment plan is shown since the year is not yet closed.

### Installment payment plan

When calculating last year's tax, the calculator can show your payment split into 3 equal installments per SENIAT rules:

- **1st installment:** on your filing date
- **2nd installment:** 20 days after March 31
- **3rd installment:** 40 days after March 31

The interval is configurable via `INSTALLMENT_DAYS` in case SENIAT modifies the rules.

## Notes on exchange rate

The `USD_TO_VES` rate should reflect the official BCV (Banco Central de Venezuela) rate at the time of declaration. This affects the USD equivalent figures shown for reference — all tax calculations are done in Bs.

## Disclaimer

This calculator is for informational purposes only. Tax rates, brackets, and rules may change. Always verify your declaration with SENIAT or a qualified tax professional.

## License

MIT
