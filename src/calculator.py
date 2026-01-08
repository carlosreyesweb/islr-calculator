"""
Calculator module for ISLR tax calculations
Contains the ISLRCalculator class with all calculation methods
"""

from src.i18n import t
from src.models import CalculationStep, Currency, TaxBracket, TaxCalculationResult


class ISLRCalculator:
    """Venezuelan ISLR Tax Calculator"""

    def __init__(
        self,
        ut_value: float,
        usd_to_ves: float,
        standard_deduction_ut: float,
        taxpayer_credit_ut: float,
        dependent_credit_ut: float,
        tax_brackets: list[TaxBracket],
    ):
        """
        Initialize the calculator with configuration values

        Args:
            ut_value: Current value of Unidad Tributaria
            usd_to_ves: USD to VES exchange rate
            standard_deduction_ut: Standard deduction in UT (reduces income)
            taxpayer_credit_ut: Contributor tax credit in UT (reduces tax)
            dependent_credit_ut: Tax credit per dependent in UT (reduces tax)
            tax_brackets: List of TaxBracket objects
        """
        self.ut_value = ut_value
        self.usd_to_ves = usd_to_ves
        self.standard_deduction_ut = standard_deduction_ut
        self.taxpayer_credit_ut = taxpayer_credit_ut
        self.dependent_credit_ut = dependent_credit_ut
        self.tax_brackets = tax_brackets

    def usd_to_ves_convert(self, amount: float) -> float:
        """Convert USD to VES"""
        return amount * self.usd_to_ves

    def ves_to_usd_convert(self, amount: float) -> float:
        """Convert VES to USD"""
        return amount / self.usd_to_ves

    def ves_to_ut_convert(self, amount: float) -> float:
        """Convert VES to UT"""
        return amount / self.ut_value

    def ut_to_ves_convert(self, amount: float) -> float:
        """Convert UT to VES"""
        return amount * self.ut_value

    def calculate_tax(
        self,
        annual_income_ves: float,
        currency: Currency,
        dependents: int = 0,
    ) -> TaxCalculationResult:
        """
        Calculate income tax based on Venezuelan ISLR rates

        Args:
            annual_income_ves: Annual income in VES (Venezuelan Bolivares)
            currency: Currency used for input (VES or USD)
            dependents: Number of direct dependents (default 0)

        Returns:
            TaxCalculationResult object with tax calculation details
        """
        # Step 1: Convert income to UT
        annual_income_ut = self.ves_to_ut_convert(annual_income_ves)

        # Step 2: Apply standard deduction to income
        taxable_income_ut = max(0, annual_income_ut - self.standard_deduction_ut)

        # Step 3: Find applicable tax bracket
        applicable_bracket = None
        for bracket in self.tax_brackets:
            if bracket.min_ut <= taxable_income_ut < bracket.max_ut:
                applicable_bracket = bracket
                break

        # If no bracket found, use the highest bracket
        if applicable_bracket is None and taxable_income_ut > 0:
            applicable_bracket = self.tax_brackets[-1]

        # Step 4: Calculate tax using bracket formula
        if applicable_bracket and taxable_income_ut > 0:
            # Tax = (Taxable Income × Rate) - Bracket Subtraction
            tax_before_credits_ut = max(
                0,
                (taxable_income_ut * applicable_bracket.rate)
                - applicable_bracket.subtract_ut,
            )
        else:
            tax_before_credits_ut = 0

        # Step 5: Apply tax credits (taxpayer + dependents)
        dependents_credit_ut = dependents * self.dependent_credit_ut
        taxpayer_credit_ut = self.taxpayer_credit_ut
        total_credits_ut = taxpayer_credit_ut + dependents_credit_ut

        # Final tax after credits
        total_tax_ut = max(0, tax_before_credits_ut - total_credits_ut)

        # Step 6: Convert tax to VES and USD
        total_tax_ves = self.ut_to_ves_convert(total_tax_ut)
        total_tax_usd = self.ves_to_usd_convert(total_tax_ves)

        # Step 7: Calculate net income and effective rate
        net_income_ves = annual_income_ves - total_tax_ves
        net_income_usd = self.ves_to_usd_convert(net_income_ves)
        effective_rate = (
            (total_tax_ves / annual_income_ves * 100) if annual_income_ves > 0 else 0
        )

        return TaxCalculationResult(
            annual_income_ves=annual_income_ves,
            annual_income_usd=self.ves_to_usd_convert(annual_income_ves),
            income_ut=annual_income_ut,
            standard_deduction_ut=self.standard_deduction_ut,
            dependents=dependents,
            dependents_credit_ut=dependents_credit_ut,
            taxpayer_credit_ut=taxpayer_credit_ut,
            taxable_income_ut=taxable_income_ut,
            bracket_rate=applicable_bracket.rate * 100 if applicable_bracket else 0,
            total_tax_ut=total_tax_ut,
            total_tax_ves=total_tax_ves,
            total_tax_usd=total_tax_usd,
            net_income_ves=net_income_ves,
            net_income_usd=net_income_usd,
            effective_rate=effective_rate,
            currency=currency,
            usd_rate=self.usd_to_ves,
            tax_before_credits_ut=tax_before_credits_ut,
            applicable_bracket=applicable_bracket,
            total_credits_ut=total_credits_ut,
        )

    def get_calculation_breakdown(
        self, result: TaxCalculationResult
    ) -> list[CalculationStep]:
        """
        Get structured breakdown of tax calculation steps
        Uses pre-calculated values from result to avoid redundant calculations

        Args:
            result: TaxCalculationResult object with intermediate values

        Returns:
            List of CalculationStep objects
        """
        steps = []

        # Step 1: Convert income to UT
        steps.append(
            CalculationStep(
                step="1",
                description=f"{t('calculation.annual_income')} {result.annual_income_ves:,.2f} Bs ÷ {self.ut_value} Bs/UT",
                result=f"{result.income_ut:,.2f} UT",
            )
        )

        # Step 2: Apply standard deduction
        steps.append(
            CalculationStep(
                step="2",
                description=f"{t('calculation.standard_deduction')} {result.income_ut:,.2f} UT - {result.standard_deduction_ut:.0f} UT",
                result=f"{result.taxable_income_ut:,.2f} UT ({t('calculation.taxable')})",
            )
        )

        # Step 3: Identify tax bracket and calculate tax
        if result.applicable_bracket and result.taxable_income_ut > 0:
            bracket = result.applicable_bracket
            max_ut = "∞" if bracket.max_ut == float("inf") else f"{bracket.max_ut:,.0f}"
            steps.append(
                CalculationStep(
                    step="3",
                    description=f"{t('calculation.tax_bracket')} {bracket.min_ut:,.0f} - {max_ut} UT ({bracket.rate * 100:.0f}%)",
                    result="",
                )
            )

            # Step 4: Calculate tax before credits (use stored value)
            steps.append(
                CalculationStep(
                    step="4",
                    description=f"{t('calculation.tax_calculation')} ({result.taxable_income_ut:,.2f} UT × {bracket.rate * 100:.0f}%) - {bracket.subtract_ut:.0f} UT",
                    result=f"{result.tax_before_credits_ut:,.2f} UT",
                )
            )
        else:
            # No taxable income or below threshold
            steps.append(
                CalculationStep(
                    step="3",
                    description=t("calculation.no_taxable_income"),
                    result="0.00 UT",
                )
            )

        # Step 5: Apply tax credits (use stored values)
        credit_parts = [f"{result.taxpayer_credit_ut:.0f} UT"]
        if result.dependents > 0:
            credit_parts.append(f"{result.dependents_credit_ut:.0f} UT")

        if result.tax_before_credits_ut > 0:
            credit_desc_parts = [t("calculation.contributor_credit")]
            if result.dependents > 0:
                credit_desc_parts.append(
                    f"{t('calculation.dependents')} ({result.dependents})"
                )

            steps.append(
                CalculationStep(
                    step="5",
                    description=f"{t('calculation.apply_tax_credits')} [{', '.join(credit_desc_parts)}]: {result.tax_before_credits_ut:,.2f} UT - {' - '.join(credit_parts)}",
                    result=f"{result.total_tax_ut:,.2f} UT ({t('calculation.final')})",
                )
            )
        else:
            # No tax before credits, just show credits aren't applied
            steps.append(
                CalculationStep(
                    step="5",
                    description=f"{t('calculation.tax_credits_not_applicable')} {result.total_credits_ut:.0f} UT",
                    result=f"{result.total_tax_ut:,.2f} UT ({t('calculation.final')})",
                )
            )

        # Step 6: Convert to VES
        steps.append(
            CalculationStep(
                step="6",
                description=f"{t('calculation.convert_to_ves')} {result.total_tax_ut:,.2f} UT × {self.ut_value} Bs/UT",
                result=f"{result.total_tax_ves:,.2f} Bs",
            )
        )

        # Step 7: Calculate effective rate
        steps.append(
            CalculationStep(
                step="7",
                description=f"{t('calculation.effective_rate_calc')} {result.total_tax_ves:,.2f} Bs ÷ {result.annual_income_ves:,.2f} Bs",
                result=f"{result.effective_rate:.2f}%",
            )
        )

        return steps
