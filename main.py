"""
Venezuelan Income Tax (ISLR) Calculator
Calculates income tax based on Venezuelan tax brackets using Unidad Tributaria (UT)
"""

from rich.console import Console

from calculator import ISLRCalculator
from config import load_config
from console import ConsoleUI
from models import Currency


def main():
    """Main application entry point"""
    console = Console()
    ui = ConsoleUI(console)

    # Load configuration
    config = load_config(console)

    # Initialize calculator
    calculator = ISLRCalculator(
        ut_value=config.ut_value,
        usd_to_ves=config.usd_to_ves,
        standard_deduction_ut=config.standard_deduction_ut,
        tax_brackets=config.tax_brackets,
    )

    ui.clear()
    ui.display_header(config.ut_value, config.usd_to_ves, config.standard_deduction_ut)

    while True:
        # Display menu and get choice
        choice = ui.display_menu()

        if choice == "1":
            # Calculate tax with standard deduction
            monthly_income, currency = ui.get_monthly_income()

            # Convert to VES if needed
            if currency == Currency.USD:
                monthly_income_ves = calculator.usd_to_ves_convert(monthly_income)
            else:
                monthly_income_ves = monthly_income

            annual_income_ves = monthly_income_ves * 12

            if annual_income_ves == 0:
                ui.print(
                    "[yellow]⚠️  No income specified, no tax to calculate.[/yellow]"
                )
                continue

            # Calculate tax with standard deduction
            result = calculator.calculate_tax(annual_income_ves, currency)

            # Display results
            ui.display_results(result)

            # Ask if user wants to see calculation breakdown
            if ui.confirm("Show calculation breakdown?", default=True):
                steps = calculator.get_calculation_breakdown(result)
                ui.display_calculation_breakdown(steps)

            # Ask if user wants to calculate again
            if not ui.confirm("Calculate for another income?", default=True):
                break

        elif choice == "2":
            # View tax brackets
            ui.display_tax_brackets(config.tax_brackets, config.ut_value)

            if not ui.confirm("Return to main menu?", default=True):
                break

        elif choice == "3":
            break

    ui.show_goodbye_message()


if __name__ == "__main__":
    main()
