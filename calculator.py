"""
Calculator module for ISLR tax calculations
Contains the ISLRCalculator class with all calculation methods
"""

from models import CalculationStep, TaxBracket, TaxCalculationResult, Currency


class ISLRCalculator:
    """Venezuelan ISLR Tax Calculator"""

    def __init__(
        self,
        ut_value: float,
        usd_to_ves: float,
        standard_deduction_ut: float,
        tax_brackets: list[TaxBracket],
    ):
        """
        Initialize the calculator with configuration values

        Args:
            ut_value: Current value of Unidad Tributaria
            usd_to_ves: USD to VES exchange rate
            standard_deduction_ut: Standard deduction in UT
            tax_brackets: List of TaxBracket objects
        """
        self.ut_value = ut_value
        self.usd_to_ves = usd_to_ves
        self.standard_deduction_ut = standard_deduction_ut
        self.tax_brackets = tax_brackets

    def usd_to_ves_convert(self, amount_usd: float) -> float:
        """Convert USD to VES"""
        return amount_usd * self.usd_to_ves

    def ves_to_usd_convert(self, amount_ves: float) -> float:
        """Convert VES to USD"""
        return amount_ves / self.usd_to_ves

    def ves_to_ut_convert(self, amount_ves: float) -> float:
        """Convert VES to UT"""
        return amount_ves / self.ut_value

    def ut_to_ves_convert(self, amount_ut: float) -> float:
        """Convert UT to VES"""
        return amount_ut * self.ut_value

    def calculate_tax(
        self,
        annual_income_ves: float,
        currency: Currency,
    ) -> TaxCalculationResult:
        """
        Calculate income tax based on Venezuelan ISLR rates

        Args:
            annual_income_ves: Annual income in VES (Venezuelan Bolivares)
            currency: Currency used for input (VES or USD)

        Returns:
            TaxCalculationResult object with tax calculation details
        """
        # Convert income to UT
        income_ut = self.ves_to_ut_convert(annual_income_ves)

        # Apply standard deduction
        deduction_ut = self.standard_deduction_ut
        taxable_income_ut = max(0, income_ut - deduction_ut)

        # Find the applicable bracket
        applicable_bracket = None
        for bracket in self.tax_brackets:
            if bracket.min_ut <= taxable_income_ut < bracket.max_ut:
                applicable_bracket = bracket
                break

        # If no bracket found, use the last one (highest bracket)
        if applicable_bracket is None and taxable_income_ut > 0:
            applicable_bracket = self.tax_brackets[-1]

        # Calculate tax using the bracket's rate and subtract_ut
        if applicable_bracket and taxable_income_ut > 0:
            # Tax = (Taxable Income × Rate) - Subtract Amount
            total_tax_ut = (
                taxable_income_ut * applicable_bracket.rate
            ) - applicable_bracket.subtract_ut
            total_tax_ut = max(0, total_tax_ut)  # Tax cannot be negative
        else:
            total_tax_ut = 0

        total_tax_ves = self.ut_to_ves_convert(total_tax_ut)

        # Calculate effective rate
        effective_rate = (
            (total_tax_ves / annual_income_ves * 100) if annual_income_ves > 0 else 0
        )

        return TaxCalculationResult(
            annual_income_ves=annual_income_ves,
            annual_income_usd=self.ves_to_usd_convert(annual_income_ves),
            income_ut=income_ut,
            standard_deduction_ut=self.standard_deduction_ut,
            deduction_ut=deduction_ut,
            taxable_income_ut=taxable_income_ut,
            bracket_rate=applicable_bracket.rate * 100 if applicable_bracket else 0,
            total_tax_ut=total_tax_ut,
            total_tax_ves=total_tax_ves,
            total_tax_usd=self.ves_to_usd_convert(total_tax_ves),
            net_income_ves=annual_income_ves - total_tax_ves,
            net_income_usd=self.ves_to_usd_convert(annual_income_ves - total_tax_ves),
            effective_rate=effective_rate,
            currency=currency,
            usd_rate=self.usd_to_ves,
        )

    def get_calculation_breakdown(
        self, result: TaxCalculationResult
    ) -> list[CalculationStep]:
        """
        Get structured breakdown of tax calculation steps

        Args:
            result: TaxCalculationResult object

        Returns:
            List of CalculationStep objects
        """
        steps = []

        # Step 1: Convert to UT
        steps.append(
            CalculationStep(
                step="1",
                description=f"Gross Income: {result.annual_income_ves:,.2f} Bs ÷ {self.ut_value} UT/Bs",
                result=f"{result.income_ut:,.2f} UT",
            )
        )

        # Step 2: Apply standard deduction
        steps.append(
            CalculationStep(
                step="2",
                description=f"Less Standard Deduction: {result.income_ut:,.2f} UT - {result.standard_deduction_ut:.0f} UT",
                result=f"{result.taxable_income_ut:,.2f} UT",
            )
        )

        # Step 3: Identify bracket
        if result.bracket_rate > 0:
            # Find the bracket details
            for bracket in self.tax_brackets:
                if bracket.rate * 100 == result.bracket_rate:
                    max_ut = (
                        "∞"
                        if bracket.max_ut == float("inf")
                        else f"{bracket.max_ut:,.0f}"
                    )
                    steps.append(
                        CalculationStep(
                            step="3",
                            description=f"Tax Bracket: {bracket.min_ut:,.0f} - {max_ut} UT ({bracket.rate * 100:.0f}% rate)",
                            result="",
                        )
                    )
                    # Step 4: Calculate tax
                    if result.taxable_income_ut > 0:
                        steps.append(
                            CalculationStep(
                                step="4",
                                description=f"Tax Formula: ({result.taxable_income_ut:,.2f} UT × {bracket.rate * 100:.0f}%) - {bracket.subtract_ut:.0f} UT",
                                result=f"{result.total_tax_ut:,.2f} UT",
                            )
                        )
                    break
        else:
            steps.append(
                CalculationStep(
                    step="3",
                    description="No tax due (below minimum threshold)",
                    result="0.00 UT",
                )
            )

        # Step 5: Convert to VES
        if result.total_tax_ut > 0:
            steps.append(
                CalculationStep(
                    step="5",
                    description=f"Convert to VES: {result.total_tax_ut:,.2f} UT × {self.ut_value} Bs/UT",
                    result=f"{result.total_tax_ves:,.2f} Bs",
                )
            )

        # Step 6: Calculate effective rate
        if result.effective_rate > 0:
            steps.append(
                CalculationStep(
                    step="6",
                    description=f"Effective Rate: ({result.total_tax_ves:,.2f} Bs ÷ {result.annual_income_ves:,.2f} Bs) × 100",
                    result=f"{result.effective_rate:.2f}%",
                )
            )

        return steps
