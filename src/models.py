"""
Data models for ISLR Calculator
Type-safe dataclasses for shared data structures across modules
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Currency(StrEnum):
    """Supported currencies"""

    VES = "VES"
    USD = "USD"


class CalculatorMode(StrEnum):
    """Which calculation flow the user selected"""

    DECLARATION = "declaration"  # Last year's closed income - real tax owed
    SIMULATION = "simulation"  # Current year projection - estimated future tax


@dataclass
class TaxBracket:
    """Tax bracket definition"""

    min_ut: float
    max_ut: float
    rate: float
    subtract_ut: float


@dataclass
class TaxCalculationResult:
    """Complete result of tax calculation"""

    # Income
    annual_income_ves: float
    annual_income_usd: float

    # Deduction and taxable base (in both UT and Bs for breakdown use)
    income_ut: float
    standard_deduction_ut: float
    standard_deduction_ves: float
    taxable_income_ut: float
    taxable_income_ves: float

    # Bracket
    bracket_rate: float  # as percentage (e.g. 34.0)

    # Tax before and after credits
    tax_before_credits_ves: float
    dependents: int
    dependents_credit_ut: float
    taxpayer_credit_ut: float
    total_credits_ut: float
    credits_ves: float  # total credits converted to Bs

    # Final tax
    total_tax_ut: float
    total_tax_ves: float
    total_tax_usd: float

    # Net income
    net_income_ves: float
    net_income_usd: float

    # Rate
    effective_rate: float

    # Meta
    currency: Currency
    usd_rate: float
    fiscal_year: int | None
    monthly_entries: list["MonthlyIncomeEntry"] | None

    # Stored intermediates for breakdown
    applicable_bracket: TaxBracket | None


@dataclass
class CalculationStep:
    """A single step in the tax calculation breakdown"""

    step: str
    description: str
    result: str


@dataclass
class MonthlyIncomeEntry:
    """Income entry for a specific month in the fiscal year"""

    month: int
    amount: float
    currency: Currency
    usd_rate: float | None
    amount_ves: float


@dataclass
class InstallmentPlan:
    """Payment plan split into 3 equal installments per SENIAT rules"""

    declaration_date: date
    installment_days: int
    amount_per_installment_ves: float
    amount_per_installment_usd: float
    dates: list[date]  # [declaration_date, +days, +days*2]
