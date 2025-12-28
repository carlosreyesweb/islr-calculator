"""
Venezuelan Income Tax (ISLR) Calculator
Calculates income tax based on Venezuelan tax brackets using Unidad Tributaria (UT)
"""

import os
import sys

from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

load_dotenv()

console = Console()

# Get UT_VALUE from environment variable
UT_VALUE_STR = os.getenv("UT_VALUE")
if UT_VALUE_STR is None:
    console.print(
        "[bold red]Error: UT_VALUE environment variable is not set.[/bold red]"
    )
    console.print("[yellow]Please set UT_VALUE before running the calculator.[/yellow]")
    console.print("[dim]Example: export UT_VALUE=43.0[/dim]")
    sys.exit(1)

try:
    UT_VALUE = float(UT_VALUE_STR)
except ValueError:
    console.print(
        f"[bold red]Error: UT_VALUE '{UT_VALUE_STR}' is not a valid number.[/bold red]"
    )
    sys.exit(1)


# Get USD_TO_VES from environment variable
USD_TO_VES_STR = os.getenv("USD_TO_VES")
if USD_TO_VES_STR is None:
    console.print(
        "[bold red]Error: USD_TO_VES environment variable is not set.[/bold red]"
    )
    console.print(
        "[yellow]Please set USD_TO_VES before running the calculator.[/yellow]"
    )
    console.print("[dim]Example: export USD_TO_VES=50.0[/dim]")
    sys.exit(1)

try:
    USD_TO_VES = float(USD_TO_VES_STR)
except ValueError:
    console.print(
        f"[bold red]Error: USD_TO_VES '{USD_TO_VES_STR}' is not a valid number.[/bold red]"
    )
    sys.exit(1)

# Get STANDARD_DEDUCTION_UT from environment variable
STANDARD_DEDUCTION_UT_STR = os.getenv("STANDARD_DEDUCTION_UT")
if STANDARD_DEDUCTION_UT_STR is None:
    console.print(
        "[bold red]Error: STANDARD_DEDUCTION_UT environment variable is not set.[/bold red]"
    )
    console.print(
        "[yellow]Please set STANDARD_DEDUCTION_UT before running the calculator.[/yellow]"
    )
    console.print("[dim]Example: export STANDARD_DEDUCTION_UT=775[/dim]")
    sys.exit(1)

try:
    STANDARD_DEDUCTION_UT = float(STANDARD_DEDUCTION_UT_STR)
except ValueError:
    console.print(
        f"[bold red]Error: STANDARD_DEDUCTION_UT '{STANDARD_DEDUCTION_UT_STR}' is not a valid number.[/bold red]"
    )
    sys.exit(1)

# Venezuelan Tax Brackets (ISLR)
# Based on annual income in UT
TAX_BRACKETS = [
    {"min_ut": 0, "max_ut": 1000, "rate": 0.06, "subtract_ut": 0},
    {"min_ut": 1000, "max_ut": 1500, "rate": 0.09, "subtract_ut": 30},
    {"min_ut": 1500, "max_ut": 2000, "rate": 0.12, "subtract_ut": 75},
    {"min_ut": 2000, "max_ut": 2500, "rate": 0.16, "subtract_ut": 155},
    {"min_ut": 2500, "max_ut": 3000, "rate": 0.20, "subtract_ut": 255},
    {"min_ut": 3000, "max_ut": 4000, "rate": 0.24, "subtract_ut": 375},
    {"min_ut": 4000, "max_ut": 6000, "rate": 0.29, "subtract_ut": 575},
    {"min_ut": 6000, "max_ut": float("inf"), "rate": 0.34, "subtract_ut": 875},
]


def calculate_tax(
    annual_income_ves: float,
    ut_value: float = UT_VALUE,
    currency: str = "VES",
    usd_rate: float = USD_TO_VES,
    standard_deduction_ut: float = STANDARD_DEDUCTION_UT,
) -> dict:
    """
    Calculate income tax based on Venezuelan ISLR rates

    Args:
        annual_income_ves: Annual income in VES (Venezuelan Bolivares)
        ut_value: Current value of Unidad Tributaria
        currency: Currency used for input (VES or USD)
        usd_rate: USD to VES exchange rate
        standard_deduction_ut: Standard deduction in UT

    Returns:
        Dictionary with tax calculation details
    """
    # Convert income to UT
    income_ut = annual_income_ves / ut_value

    # Apply standard deduction
    taxable_income_ut = max(0, income_ut - standard_deduction_ut)

    # Find the applicable bracket
    applicable_bracket = None
    for bracket in TAX_BRACKETS:
        if bracket["min_ut"] <= taxable_income_ut < bracket["max_ut"]:
            applicable_bracket = bracket
            break

    # If no bracket found, use the last one (highest bracket)
    if applicable_bracket is None and taxable_income_ut > 0:
        applicable_bracket = TAX_BRACKETS[-1]

    # Calculate tax using the bracket's rate and subtract_ut
    if applicable_bracket and taxable_income_ut > 0:
        # Tax = (Taxable Income × Rate) - Subtract Amount
        total_tax_ut = (
            taxable_income_ut * applicable_bracket["rate"]
        ) - applicable_bracket["subtract_ut"]
        total_tax_ut = max(0, total_tax_ut)  # Tax cannot be negative
    else:
        total_tax_ut = 0

    total_tax_ves = total_tax_ut * ut_value

    # Calculate effective rate
    effective_rate = (
        (total_tax_ves / annual_income_ves * 100) if annual_income_ves > 0 else 0
    )

    return {
        "annual_income_ves": annual_income_ves,
        "annual_income_usd": annual_income_ves / usd_rate,
        "income_ut": income_ut,
        "standard_deduction_ut": standard_deduction_ut,
        "taxable_income_ut": taxable_income_ut,
        "bracket_rate": applicable_bracket["rate"] * 100 if applicable_bracket else 0,
        "total_tax_ut": total_tax_ut,
        "total_tax_ves": total_tax_ves,
        "total_tax_usd": total_tax_ves / usd_rate,
        "net_income_ves": annual_income_ves - total_tax_ves,
        "net_income_usd": (annual_income_ves - total_tax_ves) / usd_rate,
        "effective_rate": effective_rate,
        "currency": currency,
        "usd_rate": usd_rate,
    }


def display_tax_brackets(ut_value: float):
    """Display the tax brackets table"""
    table = Table(title="📊 Venezuelan ISLR Tax Brackets", box=box.ROUNDED)

    table.add_column("Income Range (UT)", style="cyan", justify="right")
    table.add_column("Income Range (Bs.)", style="cyan", justify="right")
    table.add_column("Tax Rate", style="magenta", justify="center")
    table.add_column("Subtract (UT)", style="yellow", justify="right")

    for bracket in TAX_BRACKETS:
        min_ves = f"{bracket['min_ut'] * ut_value:,.2f}"
        max_ves = (
            "∞"
            if bracket["max_ut"] == float("inf")
            else f"{bracket['max_ut'] * ut_value:,.2f}"
        )
        max_ut = (
            "∞" if bracket["max_ut"] == float("inf") else f"{bracket['max_ut']:,.0f}"
        )

        table.add_row(
            f"{bracket['min_ut']:,.0f} - {max_ut}",
            f"{min_ves} - {max_ves}",
            f"{bracket['rate'] * 100:.0f}%",
            f"{bracket['subtract_ut']:,.0f} UT",
        )

    console.print(table)
    console.print()


def display_calculation_breakdown(result: dict):
    """Display detailed breakdown of tax calculation steps"""
    breakdown_table = Table(show_header=False, box=None, padding=(0, 1))
    breakdown_table.add_column("Step", style="dim cyan", no_wrap=True)
    breakdown_table.add_column("Calculation", style="white")
    breakdown_table.add_column("Result", style="bold yellow", justify="right")

    # Step 1: Convert to UT
    breakdown_table.add_row(
        "1.",
        f"Gross Income: {result['annual_income_ves']:,.2f} Bs ÷ {UT_VALUE} UT/Bs",
        f"{result['income_ut']:,.2f} UT",
    )

    # Step 2: Apply deduction
    breakdown_table.add_row(
        "2.",
        f"Less Standard Deduction: {result['income_ut']:,.2f} UT - {result['standard_deduction_ut']:,.0f} UT",
        f"{result['taxable_income_ut']:,.2f} UT",
    )

    # Step 3: Identify bracket
    if result["bracket_rate"] > 0:
        # Find the bracket details
        for bracket in TAX_BRACKETS:
            if bracket["rate"] * 100 == result["bracket_rate"]:
                max_ut = (
                    "∞"
                    if bracket["max_ut"] == float("inf")
                    else f"{bracket['max_ut']:,.0f}"
                )
                breakdown_table.add_row(
                    "3.",
                    f"Tax Bracket: {bracket['min_ut']:,.0f} - {max_ut} UT ({bracket['rate'] * 100:.0f}% rate)",
                    "",
                )
                # Step 4: Calculate tax
                if result["taxable_income_ut"] > 0:
                    breakdown_table.add_row(
                        "4.",
                        f"Tax Formula: ({result['taxable_income_ut']:,.2f} UT × {bracket['rate'] * 100:.0f}%) - {bracket['subtract_ut']:.0f} UT",
                        f"{result['total_tax_ut']:,.2f} UT",
                    )
                break
    else:
        breakdown_table.add_row(
            "3.",
            "No tax due (below minimum threshold)",
            "0.00 UT",
        )

    # Step 5: Convert to VES
    if result["total_tax_ut"] > 0:
        breakdown_table.add_row(
            "5.",
            f"Convert to VES: {result['total_tax_ut']:,.2f} UT × {UT_VALUE} Bs/UT",
            f"{result['total_tax_ves']:,.2f} Bs",
        )

    # Step 6: Calculate effective rate
    if result["effective_rate"] > 0:
        breakdown_table.add_row(
            "6.",
            f"Effective Rate: ({result['total_tax_ves']:,.2f} Bs ÷ {result['annual_income_ves']:,.2f} Bs) × 100",
            f"{result['effective_rate']:.2f}%",
        )

    panel = Panel(
        breakdown_table,
        title="🔢 Calculation Breakdown",
        border_style="cyan",
        box=box.ROUNDED,
    )

    console.print(panel)


def display_results(result: dict):
    """Display the tax calculation results in a formatted panel"""

    # Create a results table
    results_table = Table(show_header=False, box=None, padding=(0, 2))
    results_table.add_column("Label", style="bold cyan")
    results_table.add_column("Value", style="bold white")

    results_table.add_row(
        "Annual Income (VES):", f"{result['annual_income_ves']:,.2f} Bs."
    )
    results_table.add_row(
        "Annual Income (USD):", f"${result['annual_income_usd']:,.2f}"
    )
    results_table.add_row("Income in UT:", f"{result['income_ut']:,.2f} UT")
    results_table.add_row(
        "Standard Deduction:", f"{result['standard_deduction_ut']:,.2f} UT"
    )
    results_table.add_row("Taxable Income:", f"{result['taxable_income_ut']:,.2f} UT")
    results_table.add_row("", "")
    results_table.add_row("Marginal Tax Rate:", f"{result['bracket_rate']:.0f}%")
    results_table.add_row("", "")
    results_table.add_row(
        "Total Tax (UT):", f"[bold yellow]{result['total_tax_ut']:,.2f} UT[/]"
    )
    results_table.add_row(
        "Total Tax (VES):", f"[bold yellow]{result['total_tax_ves']:,.2f} Bs.[/]"
    )
    results_table.add_row(
        "Total Tax (USD):", f"[bold yellow]${result['total_tax_usd']:,.2f}[/]"
    )
    results_table.add_row("", "")
    results_table.add_row(
        "Effective Tax Rate:", f"[bold magenta]{result['effective_rate']:.2f}%[/]"
    )
    results_table.add_row(
        "Net Income (VES):", f"[bold green]{result['net_income_ves']:,.2f} Bs.[/]"
    )
    results_table.add_row(
        "Net Income (USD):", f"[bold green]${result['net_income_usd']:,.2f}[/]"
    )

    panel = Panel(
        results_table,
        title="💰 Tax Calculation Results",
        border_style="green",
        box=box.DOUBLE,
    )

    console.print(panel)


def get_monthly_income() -> tuple[float, str]:
    """Prompt user for monthly income and validate input"""
    # Ask for currency first
    console.print("\n[bold]Select currency:[/bold]")
    console.print("1. VES (Bolívares)")
    console.print("2. USD (US Dollars)")
    console.print()

    currency_choice = Prompt.ask(
        "[bold cyan]Choose currency[/bold cyan]", choices=["1", "2"], default="1"
    )

    currency = "VES" if currency_choice == "1" else "USD"

    while True:
        try:
            income_str = Prompt.ask(
                f"\n[bold cyan]Enter your monthly income in {currency}[/bold cyan]",
                default="0",
            )
            income = float(income_str.replace(",", "").replace(" ", ""))
            if income < 0:
                console.print(
                    "[red]❌ Income cannot be negative. Please try again.[/red]"
                )
                continue
            return income, currency
        except ValueError:
            console.print("[red]❌ Invalid input. Please enter a valid number.[/red]")


def main():
    """Main application entry point"""
    console.clear()

    # Display header
    title = Text("🇻🇪 Venezuelan Income Tax Calculator (ISLR)", style="bold blue")
    console.print(
        Panel(
            title,
            subtitle=f"UT: {UT_VALUE} Bs. | USD Rate: {USD_TO_VES} Bs. | Standard Deduction: {STANDARD_DEDUCTION_UT} UT",
            border_style="blue",
        )
    )
    console.print()

    while True:
        # Display menu
        console.print("[bold]What would you like to do?[/bold]")
        console.print("1. Calculate income tax")
        console.print("2. View tax brackets")
        console.print("3. Exit")
        console.print()

        choice = Prompt.ask(
            "[bold cyan]Choose an option[/bold cyan]",
            choices=["1", "2", "3"],
            default="1",
        )

        if choice == "1":
            # Get monthly income and currency
            monthly_income, currency = get_monthly_income()

            # Convert to VES if needed
            if currency == "USD":
                monthly_income_ves = monthly_income * USD_TO_VES
            else:
                monthly_income_ves = monthly_income

            annual_income_ves = monthly_income_ves * 12

            if annual_income_ves == 0:
                console.print(
                    "\n[yellow]⚠️  No income specified, no tax to calculate.[/yellow]\n"
                )
                continue

            # Calculate tax
            result = calculate_tax(
                annual_income_ves, UT_VALUE, currency, USD_TO_VES, STANDARD_DEDUCTION_UT
            )

            # Display results
            console.print()
            display_results(result)
            console.print()

            # Ask if user wants to see calculation breakdown
            if Confirm.ask("[bold]Show calculation breakdown?[/bold]", default=True):
                console.print()
                display_calculation_breakdown(result)
                console.print()

            # Ask if user wants to calculate again
            if not Confirm.ask(
                "\n[bold]Calculate for another income?[/bold]", default=True
            ):
                break

        elif choice == "2":
            console.print()
            display_tax_brackets(UT_VALUE)

            if not Confirm.ask("[bold]Return to main menu?[/bold]", default=True):
                break

        elif choice == "3":
            break

    console.print(
        "\n[bold green]✨ Thank you for using the ISLR Calculator![/bold green]\n"
    )


if __name__ == "__main__":
    main()
