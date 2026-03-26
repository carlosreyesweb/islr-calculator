"""
Calculator module for ISLR tax calculations
Contains the ISLRCalculator class with all calculation methods
"""

from datetime import date, timedelta

from src.i18n import t
from src.models import (
    CalculationStep,
    Currency,
    InstallmentPlan,
    MonthlyIncomeEntry,
    TaxBracket,
    TaxCalculationResult,
)


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
        fiscal_year: int | None = None,
        monthly_entries: list[MonthlyIncomeEntry] | None = None,
    ) -> TaxCalculationResult:
        """
        Calculate income tax based on Venezuelan ISLR rates.

        All math is done on annual figures in VES/UT.

        Args:
            annual_income_ves: Annual income in VES (already converted from USD if needed)
            currency: Currency the user originally entered (for display only)
            dependents: Number of direct dependents

        Returns:
            TaxCalculationResult with all calculation details
        """
        # Convert income to UT
        annual_income_ut = self.ves_to_ut_convert(annual_income_ves)

        # Apply standard deduction
        standard_deduction_ves = self.ut_to_ves_convert(self.standard_deduction_ut)
        taxable_income_ut = max(0, annual_income_ut - self.standard_deduction_ut)
        taxable_income_ves = self.ut_to_ves_convert(taxable_income_ut)

        # Find applicable tax bracket
        applicable_bracket = None
        for bracket in self.tax_brackets:
            if bracket.min_ut <= taxable_income_ut < bracket.max_ut:
                applicable_bracket = bracket
                break
        if applicable_bracket is None and taxable_income_ut > 0:
            applicable_bracket = self.tax_brackets[-1]

        # Calculate tax before credits using bracket formula
        if applicable_bracket and taxable_income_ut > 0:
            tax_before_credits_ut = max(
                0,
                (taxable_income_ut * applicable_bracket.rate)
                - applicable_bracket.subtract_ut,
            )
        else:
            tax_before_credits_ut = 0

        tax_before_credits_ves = self.ut_to_ves_convert(tax_before_credits_ut)

        # Apply credits (taxpayer + dependents)
        dependents_credit_ut = dependents * self.dependent_credit_ut
        total_credits_ut = self.taxpayer_credit_ut + dependents_credit_ut
        credits_ves = self.ut_to_ves_convert(total_credits_ut)

        # Final tax after credits
        total_tax_ut = max(0, tax_before_credits_ut - total_credits_ut)
        total_tax_ves = self.ut_to_ves_convert(total_tax_ut)
        total_tax_usd = self.ves_to_usd_convert(total_tax_ves)

        # Net income and effective rate
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
            standard_deduction_ves=standard_deduction_ves,
            taxable_income_ut=taxable_income_ut,
            taxable_income_ves=taxable_income_ves,
            bracket_rate=applicable_bracket.rate * 100 if applicable_bracket else 0,
            tax_before_credits_ves=tax_before_credits_ves,
            dependents=dependents,
            dependents_credit_ut=dependents_credit_ut,
            taxpayer_credit_ut=self.taxpayer_credit_ut,
            total_credits_ut=total_credits_ut,
            credits_ves=credits_ves,
            total_tax_ut=total_tax_ut,
            total_tax_ves=total_tax_ves,
            total_tax_usd=total_tax_usd,
            net_income_ves=net_income_ves,
            net_income_usd=net_income_usd,
            effective_rate=effective_rate,
            currency=currency,
            usd_rate=self.usd_to_ves,
            fiscal_year=fiscal_year,
            monthly_entries=monthly_entries,
            applicable_bracket=applicable_bracket,
        )

    def calculate_annual_income_from_monthly(
        self, entries: list[MonthlyIncomeEntry]
    ) -> float:
        """Sum all monthly entries converted to VES."""
        return sum(entry.amount_ves for entry in entries)

    def get_calculation_breakdown(
        self, result: TaxCalculationResult
    ) -> list[CalculationStep]:
        """
        Return a concise, user-friendly breakdown of the tax calculation.

        All values are in Bs. Steps are written in plain language - no UT
        arithmetic or bracket subtract_ut mechanics exposed to the user.

        Args:
            result: TaxCalculationResult from calculate_tax()

        Returns:
            List of CalculationStep objects (5-6 steps)
        """
        steps = []
        step_num = 1

        # Step 1: Annual income (with USD->Bs conversion if applicable)
        if result.currency == Currency.USD:
            steps.append(
                CalculationStep(
                    step=str(step_num),
                    description=t(
                        "calculation.income_usd",
                        usd=f"${result.annual_income_usd:,.2f}",
                        rate=f"{result.usd_rate:,.2f}",
                    ),
                    result=f"{result.annual_income_ves:,.2f} Bs.",
                )
            )
        else:
            steps.append(
                CalculationStep(
                    step=str(step_num),
                    description=t("calculation.income"),
                    result=f"{result.annual_income_ves:,.2f} Bs.",
                )
            )
        step_num += 1

        # Step 2: Standard deduction
        if result.taxable_income_ves > 0:
            steps.append(
                CalculationStep(
                    step=str(step_num),
                    description=t(
                        "calculation.deduction",
                        income=f"{result.annual_income_ves:,.2f}",
                        deduction=f"{result.standard_deduction_ves:,.2f}",
                    ),
                    result=f"{result.taxable_income_ves:,.2f} Bs.",
                )
            )
            step_num += 1

            # Step 3: Rate applied
            steps.append(
                CalculationStep(
                    step=str(step_num),
                    description=t(
                        "calculation.rate_applied",
                        taxable=f"{result.taxable_income_ves:,.2f}",
                        rate=f"{result.bracket_rate:.0f}",
                    ),
                    result=f"{result.tax_before_credits_ves:,.2f} Bs.",
                )
            )
            step_num += 1

            # Step 4: Credits
            if result.credits_ves > 0:
                steps.append(
                    CalculationStep(
                        step=str(step_num),
                        description=t(
                            "calculation.credits",
                            tax=f"{result.tax_before_credits_ves:,.2f}",
                            credits=f"{result.credits_ves:,.2f}",
                        ),
                        result=f"[bold]{result.total_tax_ves:,.2f} Bs.[/bold]",
                    )
                )
                step_num += 1
        else:
            # No taxable income after deduction
            steps.append(
                CalculationStep(
                    step=str(step_num),
                    description=t("calculation.no_taxable_income"),
                    result="0.00 Bs.",
                )
            )
            step_num += 1

        # Step 5: Effective rate
        steps.append(
            CalculationStep(
                step=str(step_num),
                description=t(
                    "calculation.effective_rate_calc",
                    tax=f"{result.total_tax_ves:,.2f}",
                    income=f"{result.annual_income_ves:,.2f}",
                ),
                result=f"{result.effective_rate:.2f}%",
            )
        )

        return steps

    def get_installment_plan(
        self,
        result: TaxCalculationResult,
        declaration_date: date,
        installment_days: int,
    ) -> InstallmentPlan:
        """
        Build a 3-installment payment plan per SENIAT rules.

        The 1st installment is due on the actual filing date. The 2nd and 3rd
        are anchored to March 31 (the fixed SENIAT deadline) plus
        installment_days intervals - always the same regardless of early filing.

        Args:
            result: TaxCalculationResult with total tax figures
            declaration_date: The date the taxpayer actually files
            installment_days: Calendar days between installments from March 31

        Returns:
            InstallmentPlan with amounts and due dates for each installment
        """
        amount_ves = result.total_tax_ves / 3
        amount_usd = result.total_tax_usd / 3

        deadline = date(declaration_date.year, 3, 31)
        dates = [
            declaration_date,
            deadline + timedelta(days=installment_days),
            deadline + timedelta(days=installment_days * 2),
        ]

        return InstallmentPlan(
            declaration_date=declaration_date,
            installment_days=installment_days,
            amount_per_installment_ves=amount_ves,
            amount_per_installment_usd=amount_usd,
            dates=dates,
        )
