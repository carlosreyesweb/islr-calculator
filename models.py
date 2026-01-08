"""
Data models for ISLR Calculator
Type-safe dataclasses for shared data structures across modules
"""

from dataclasses import dataclass
from enum import StrEnum


class Currency(StrEnum):
    """Supported currencies"""

    VES = "VES"
    USD = "USD"


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

    annual_income_ves: float
    annual_income_usd: float
    income_ut: float
    standard_deduction_ut: float
    dependents: int
    dependents_credit_ut: float
    contributor_credit_ut: float
    taxable_income_ut: float
    bracket_rate: float
    total_tax_ut: float
    total_tax_ves: float
    total_tax_usd: float
    net_income_ves: float
    net_income_usd: float
    effective_rate: float
    currency: Currency
    usd_rate: float
    # Store intermediate values to avoid recalculation
    tax_before_credits_ut: float
    applicable_bracket: TaxBracket | None
    total_credits_ut: float


@dataclass
class CalculationStep:
    """A single step in the tax calculation breakdown"""

    step: str
    description: str
    result: str
