# Venezuelan Income Tax Calculator (ISLR)

Terminal app for Venezuelan personal income tax (ISLR), with a guided CLI flow in English or Spanish.

## Features

- Two calculation modes: `Declaration` (closed fiscal year) and `Simulation` (current-year estimate)
- Income in `Bs.` or `USD`
- Automatic BCV USD rate fetch at startup, with `.env` fallback
- Historical BCV month-end rates for declaration input by month
- Dependents, standard deduction, and tax credits included
- Tax owed, net income, and effective tax rate in both `Bs.` and `USD`
- Optional 3-installment SENIAT-style payment plan
- Optional step-by-step calculation breakdown
- Tax bracket table viewer
- Built-in i18n (`ISLR_LANG=en` / `ISLR_LANG=es`)

## Requirements

- Python `>=3.12`
- `uv` (recommended) or `pip` + virtualenv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/carlosreyesweb/islr-calculator.git
cd islr-calculator
```

2. Install dependencies:

```bash
# recommended
uv sync

# alternative
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

3. Create `.env` from the example:

```bash
cp .env.example .env
```

## Configuration

Set values in `.env`:

| Variable                | Required | Description                                                           |
| ----------------------- | -------- | --------------------------------------------------------------------- |
| `ISLR_LANG`             | No       | UI language (`en` or `es`). Defaults to `en`.                         |
| `UT_VALUE`              | Yes      | Current Unidad Tributaria value in Bs.                                |
| `USD_TO_VES`            | Fallback | Fallback USD/Bs. rate used when live BCV fetch is unavailable.        |
| `STANDARD_DEDUCTION_UT` | Yes      | Standard deduction in UT (reduces taxable income).                    |
| `TAXPAYER_CREDIT_UT`    | Yes      | Taxpayer credit in UT (reduces tax owed).                             |
| `DEPENDENT_CREDIT_UT`   | Yes      | Credit per dependent in UT (reduces tax owed).                        |
| `INSTALLMENT_DAYS`      | No       | Days between installment dates from March 31 baseline (default `20`). |

Example:

```env
ISLR_LANG=es
UT_VALUE=43
USD_TO_VES=457.07
STANDARD_DEDUCTION_UT=774
TAXPAYER_CREDIT_UT=10
DEPENDENT_CREDIT_UT=10
INSTALLMENT_DAYS=20
```

### Live USD/Bs. behavior

At startup, the app tries to fetch the official BCV USD rate from [ve.dolarapi.com](https://ve.dolarapi.com). If successful, the header shows it as live (with update date). If the request fails, the app falls back to `USD_TO_VES` from `.env`.

## Running

```bash
# recommended
uv run main.py

# alternative
python main.py
```

You can override language inline:

```bash
ISLR_LANG=es uv run main.py
```

## Usage

### Main menu

When the app starts, you can choose:

- `[1]` Calculate tax on last year's income (`Declaration`)
- `[2]` Estimate tax on this year's income (`Simulation`)
- `[3]` View tax brackets
- `[4]` Exit

### Declaration mode (detailed)

Use this mode to calculate what you owe for a closed fiscal year.

Flow:

1. Select fiscal year (default is previous year).
2. App fetches historical BCV month-end rates for that year.
3. Enter income in rounds (instead of one prompt per month):
   - choose currency (`Bs.` or `USD`)
   - enter amount for this round
   - select the months where that amount applies (multi-select)
   - repeat if needed for other months/amounts
4. If some months remain empty, the app asks you to confirm those months were `0`.
5. Enter number of dependents.
6. Review results panel.
7. Optionally show installment plan.
8. Optionally show calculation breakdown.

For USD rounds:

- If a selected month has historical BCV month-end rate, that month uses it.
- If not, the app asks for one manual USD rate and applies it to all missing-rate months in that round.
- Each assigned month is logged with what was saved (amount, conversion, and rate source).

Example round:

```text
- January: $1,500.00 -> 685,500.00 Bs. (BCV 457.00 - 2024-01-31)
- February: $1,500.00 -> 690,000.00 Bs. (manual rate 460.00)
```

### Simulation mode (detailed)

Use this mode to estimate annual tax from current monthly income.

Flow:

1. Choose income currency (`Bs.` or `USD`).
2. Enter current monthly income.
3. Enter dependents.
4. App annualizes income (`monthly * 12`) and calculates estimated tax.
5. View results panel and optional calculation breakdown.

Note: installment plan is not offered in simulation mode.

### Tax brackets view

Menu option `[3]` displays the full bracket table in UT and Bs. using your current `UT_VALUE`.

## Installment payment plan

Available only in `Declaration` mode.

- 1st installment: filing date (your selected declaration date)
- 2nd installment: `March 31 + INSTALLMENT_DAYS`
- 3rd installment: `March 31 + (INSTALLMENT_DAYS * 2)`

With default `INSTALLMENT_DAYS=20`, this is usually April 20 and May 10.

## Tax brackets CSV

Tax brackets are loaded from `tax_brackets.csv`:

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

| Column        | Description                                              |
| ------------- | -------------------------------------------------------- |
| `min_ut`      | Lower bound in UT (inclusive)                            |
| `max_ut`      | Upper bound in UT (exclusive). Use `inf` for top bracket |
| `rate`        | Decimal tax rate (e.g. `0.34` = 34%)                     |
| `subtract_ut` | Bracket subtraction constant in UT                       |

Formula used at bracket level:

```text
tax_before_credits_ut = (taxable_income_ut * rate) - subtract_ut
```

If SENIAT updates brackets, edit this CSV and run the app again.

## Language support

- English: `ISLR_LANG=en`
- Spanish: `ISLR_LANG=es`

Language files live in `src/i18n/locales/`.

## Tech stack

- `python-dotenv` for `.env` loading
- `questionary` for interactive prompts
- `requests` for BCV API calls
- `rich` for terminal tables/panels

## Disclaimer

This calculator is for informational purposes only. Tax rules and values may change. Always validate your declaration with SENIAT or a qualified tax professional.

## License

MIT
