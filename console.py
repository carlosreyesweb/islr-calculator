"""
Console module for ISLR Calculator
Handles all UI rendering, prompts, and display logic
"""

import questionary
from questionary import Choice
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models import CalculationStep, Currency, TaxBracket, TaxCalculationResult


class ConsoleUI:
    """Console UI handler for ISLR Calculator"""

    def __init__(self, console: Console = None):
        """
        Initialize the console UI

        Args:
            console: Optional Rich Console instance. Creates a new one if not provided.
        """
        self.console = console if console else Console()
        self.qstyle = questionary.Style(
            [
                ("qmark", "fg:cyan bold"),
                ("question", "bold"),
                ("answer", "fg:cyan bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan bold"),
                ("selected", "fg:cyan"),
                ("separator", "fg:#6C6C6C"),
                ("instruction", ""),
                ("text", ""),
            ]
        )

    def clear(self):
        """Clear the console"""
        self.console.clear()

    def print(self, *args, **kwargs):
        """Print to console"""
        self.console.print(*args, **kwargs)

    def display_header(
        self, ut_value: float, usd_to_ves: float, standard_deduction_ut: float
    ):
        """Display the application header"""
        title = Text("🇻🇪 Venezuelan Income Tax Calculator (ISLR)", style="bold blue")
        self.console.print(
            Panel(
                title,
                subtitle=f"UT: {ut_value} Bs. | USD Rate: {usd_to_ves} Bs. | Standard Deduction: {standard_deduction_ut} UT",
                border_style="blue",
            )
        )

    def display_menu(self) -> str:
        """
        Display main menu and get user choice

        Returns:
            User's menu choice as string
        """
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("💰 Calculate income tax", value="1"),
                Choice("📊 View tax brackets", value="2"),
                Choice("🚪 Exit", value="3"),
            ],
            style=self.qstyle,
        ).ask()

        return choice if choice else "3"

    def get_monthly_income(self) -> tuple[float, Currency]:
        """
        Prompt user for monthly income and validate input

        Returns:
            Tuple of (monthly_income, currency)
        """
        # Ask for currency first
        currency = questionary.select(
            "Select currency:",
            choices=[
                Choice("🇻🇪 VES (Bolívares)", value=Currency.VES),
                Choice("💵 USD (US Dollars)", value=Currency.USD),
            ],
            style=self.qstyle,
        ).ask()

        if not currency:
            return 0, Currency.VES

        while True:
            try:
                income_str = questionary.text(
                    f"Enter your monthly income in {currency}:",
                    validate=lambda text: text.replace(",", "")
                    .replace(" ", "")
                    .replace(".", "", 1)
                    .replace("-", "", 1)
                    .isdigit()
                    or text.replace(",", "")
                    .replace(" ", "")
                    .replace(".", "", 1)
                    .replace("-", "", 1)
                    == ""
                    or "Please enter a valid number",
                    style=self.qstyle,
                    default="",
                ).ask()

                if income_str is None:
                    return 0, currency

                income = float(income_str.replace(",", "").replace(" ", ""))
                if income < 0:
                    self.console.print(
                        "[red]❌ Income cannot be negative. Please try again.[/red]"
                    )
                    continue
                return income, currency
            except ValueError:
                self.console.print(
                    "[red]❌ Invalid input. Please enter a valid number.[/red]"
                )

    def display_tax_brackets(self, tax_brackets: list[TaxBracket], ut_value: float):
        """Display the tax brackets table"""
        table = Table(title="📊 Venezuelan ISLR Tax Brackets", box=box.ROUNDED)

        table.add_column("Income Range (UT)", style="cyan", justify="right")
        table.add_column("Income Range (Bs.)", style="cyan", justify="right")
        table.add_column("Tax Rate", style="magenta", justify="center")
        table.add_column("Subtract (UT)", style="yellow", justify="right")

        for bracket in tax_brackets:
            min_ves = f"{bracket.min_ut * ut_value:,.2f}"
            max_ves = (
                "∞"
                if bracket.max_ut == float("inf")
                else f"{bracket.max_ut * ut_value:,.2f}"
            )
            max_ut = "∞" if bracket.max_ut == float("inf") else f"{bracket.max_ut:,.0f}"

            table.add_row(
                f"{bracket.min_ut:,.0f} - {max_ut}",
                f"{min_ves} - {max_ves}",
                f"{bracket.rate * 100:.0f}%",
                f"{bracket.subtract_ut:,.0f} UT",
            )

        self.console.print(table)

    def display_results(self, result: TaxCalculationResult):
        """Display the tax calculation results in a formatted panel"""
        # Create a results table
        results_table = Table(show_header=False, box=None, padding=(0, 2))
        results_table.add_column("Label", style="bold cyan")
        results_table.add_column("Value", style="bold white")

        results_table.add_row(
            "Annual Income (VES):", f"{result.annual_income_ves:,.2f} Bs."
        )
        results_table.add_row(
            "Annual Income (USD):", f"${result.annual_income_usd:,.2f}"
        )
        results_table.add_row("Income in UT:", f"{result.income_ut:,.2f} UT")
        results_table.add_row(
            "Standard Deduction:", f"{result.standard_deduction_ut:,.2f} UT"
        )
        results_table.add_row("Taxable Income:", f"{result.taxable_income_ut:,.2f} UT")
        results_table.add_row("", "")
        results_table.add_row("Marginal Tax Rate:", f"{result.bracket_rate:.0f}%")
        results_table.add_row("", "")
        results_table.add_row(
            "Total Tax (UT):", f"[bold yellow]{result.total_tax_ut:,.2f} UT[/]"
        )
        results_table.add_row(
            "Total Tax (VES):", f"[bold yellow]{result.total_tax_ves:,.2f} Bs.[/]"
        )
        results_table.add_row(
            "Total Tax (USD):", f"[bold yellow]${result.total_tax_usd:,.2f}[/]"
        )
        results_table.add_row("", "")
        results_table.add_row(
            "Effective Tax Rate:", f"[bold magenta]{result.effective_rate:.2f}%[/]"
        )
        results_table.add_row(
            "Net Income (VES):", f"[bold green]{result.net_income_ves:,.2f} Bs.[/]"
        )
        results_table.add_row(
            "Net Income (USD):", f"[bold green]${result.net_income_usd:,.2f}[/]"
        )

        panel = Panel(
            results_table,
            title="💰 Tax Calculation Results",
            border_style="green",
            box=box.DOUBLE,
        )

        self.console.print(panel)

    def display_calculation_breakdown(self, steps: list[CalculationStep]):
        """
        Display detailed breakdown of tax calculation steps

        Args:
            steps: List of CalculationStep objects from calculator
        """
        breakdown_table = Table(show_header=False, box=None, padding=(0, 1))
        breakdown_table.add_column("Step", style="dim cyan", no_wrap=True)
        breakdown_table.add_column("Calculation", style="white")
        breakdown_table.add_column("Result", style="bold yellow", justify="right")

        for step in steps:
            breakdown_table.add_row(
                step.step + ".",
                step.description,
                step.result,
            )

        panel = Panel(
            breakdown_table,
            title="🔢 Calculation Breakdown",
            border_style="cyan",
            box=box.ROUNDED,
        )

        self.console.print(panel)

    def confirm(self, message: str, default: bool = True) -> bool:
        """Show a confirmation prompt"""
        result = questionary.confirm(message, default=default, style=self.qstyle).ask()
        return result if result is not None else default

    def show_goodbye_message(self):
        """Display goodbye message"""
        self.console.print(
            "[bold green]✨ Thank you for using the ISLR Calculator![/bold green]"
        )
