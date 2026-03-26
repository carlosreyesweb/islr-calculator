"""
Venezuelan Income Tax (ISLR) Calculator
Calculates income tax based on Venezuelan tax brackets using Unidad Tributaria (UT)
"""

from datetime import date

from rich.console import Console

from src.calculator import ISLRCalculator
from src.config import fetch_historical_month_end_rates, load_config
from src.console import ConsoleUI
from src.i18n import t
from src.models import CalculatorMode, Currency


def run_calculation(
    ui: ConsoleUI,
    calculator: ISLRCalculator,
    config,
    mode: CalculatorMode,
) -> bool:
    """
    Run one full income tax calculation flow.

    Declaration mode: asks for last year's annual income, shows real tax owed
    and an installment plan.

    Simulation mode: asks for current monthly income, annualizes it, shows
    a projected tax estimate. No installment plan shown.

    Returns:
        True to go back to the menu, False to exit the app.
    """
    fiscal_year: int | None = None
    monthly_entries = None
    monthly_income_ves = None

    if mode == CalculatorMode.DECLARATION:
        fiscal_year = ui.get_fiscal_year()
        ui.print(
            f"[cyan]{t('messages.fetching_historical_rates', year=fiscal_year)}[/cyan]"
        )
        historical_rates = fetch_historical_month_end_rates(fiscal_year)

        if historical_rates is None:
            ui.print(
                f"[yellow]{t('messages.historical_rates_failed', fallback=f'{config.usd_to_ves:,.2f}')}[/yellow]"
            )
            historical_rates = {}
        else:
            ui.print(
                f"[green]{t('messages.historical_rates_fetched', months=len(historical_rates), year=fiscal_year)}[/green]"
            )

        monthly_entries = ui.get_monthly_income_entries(
            fiscal_year=fiscal_year,
            monthly_rates=historical_rates,
            default_usd_rate=config.usd_to_ves,
        )
        annual_income_ves = calculator.calculate_annual_income_from_monthly(
            monthly_entries
        )
        currency = Currency.VES
    else:
        income, currency = ui.get_income(mode=mode)

        income_ves = (
            calculator.usd_to_ves_convert(income)
            if currency == Currency.USD
            else income
        )

        monthly_income_ves = income_ves
        annual_income_ves = income_ves * 12

    dependents = ui.get_number_of_dependents()

    if annual_income_ves == 0:
        ui.print(f"[yellow]{t('messages.no_income_specified')}[/yellow]")
        return True

    result = calculator.calculate_tax(
        annual_income_ves,
        currency,
        dependents,
        fiscal_year=fiscal_year,
        monthly_entries=monthly_entries,
    )

    ui.display_results(result, mode=mode, monthly_income_ves=monthly_income_ves)

    if mode == CalculatorMode.DECLARATION:
        if ui.confirm(t("prompts.show_installment_plan"), default=True):
            declaration_year = (
                fiscal_year if fiscal_year is not None else date.today().year - 1
            )
            declaration_date = ui.get_declaration_date(declaration_year)
            plan = calculator.get_installment_plan(
                result, declaration_date, config.installment_days
            )
            ui.display_installment_plan(plan)

    if ui.confirm(t("prompts.show_calculation_breakdown"), default=True):
        steps = calculator.get_calculation_breakdown(result)
        ui.display_calculation_breakdown(steps)

    prompt_key = (
        "prompts.calculate_another_income"
        if mode == CalculatorMode.DECLARATION
        else "prompts.simulate_another_income"
    )
    return ui.confirm(t(prompt_key), default=True)


def main():
    """Main application entry point"""
    console = Console()
    ui = ConsoleUI(console)

    config = load_config(console)

    calculator = ISLRCalculator(
        ut_value=config.ut_value,
        usd_to_ves=config.usd_to_ves,
        standard_deduction_ut=config.standard_deduction_ut,
        taxpayer_credit_ut=config.taxpayer_credit_ut,
        dependent_credit_ut=config.dependent_credit_ut,
        tax_brackets=config.tax_brackets,
    )

    ui.clear()
    ui.display_header(
        config.ut_value,
        config.usd_to_ves,
        config.standard_deduction_ut,
        config.taxpayer_credit_ut,
        config.dependent_credit_ut,
        usd_rate_is_live=config.usd_rate_is_live,
        usd_rate_updated_at=config.usd_rate_updated_at,
    )

    try:
        while True:
            choice = ui.display_menu()

            if choice == "1":
                if not run_calculation(
                    ui, calculator, config, CalculatorMode.DECLARATION
                ):
                    break
            elif choice == "2":
                if not run_calculation(
                    ui, calculator, config, CalculatorMode.SIMULATION
                ):
                    break
            elif choice == "3":
                ui.display_tax_brackets(config.tax_brackets, config.ut_value)
                if not ui.confirm(t("prompts.return_to_main_menu"), default=True):
                    break
            elif choice == "4":
                break
    except KeyboardInterrupt:
        pass

    ui.show_goodbye_message()


if __name__ == "__main__":
    main()
