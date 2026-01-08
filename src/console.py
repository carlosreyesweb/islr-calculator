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

from src.i18n import t
from src.models import CalculationStep, Currency, TaxBracket, TaxCalculationResult


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
        self,
        ut_value: float,
        usd_to_ves: float,
        standard_deduction_ut: float,
        taxpayer_credit_ut: float,
        dependent_credit_ut: float,
    ):
        """Display the application header"""
        title = Text(t("app.title"), style="bold blue")

        # Create a table for organized display
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Label", style="bold cyan")
        info_table.add_column("Value", style="bold white")

        info_table.add_row(t("header.ut_value"), f"{ut_value} Bs.")
        info_table.add_row(t("header.usd_rate"), f"{usd_to_ves} Bs.")
        info_table.add_row(
            t("header.standard_deduction"), f"{standard_deduction_ut} UT"
        )
        info_table.add_row(t("header.taxpayer_credit"), f"{taxpayer_credit_ut} UT")
        info_table.add_row(t("header.dependent_credit"), f"{dependent_credit_ut} UT")

        self.console.print(
            Panel(
                info_table,
                title=title,
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
            t("menu.prompt"),
            choices=[
                Choice(t("menu.calculate_tax"), value="1"),
                Choice(t("menu.view_brackets"), value="2"),
                Choice(t("menu.exit"), value="3"),
            ],
            style=self.qstyle,
        ).ask()

        return choice if choice else "3"

    def get_number_of_dependents(self) -> int:
        """
        Prompt user for number of dependents and validate input

        Returns:
            Number of dependents (int)
        """
        while True:
            try:
                dependents_str = questionary.text(
                    t("input.dependents_prompt"),
                    validate=lambda text: text.isdigit()
                    or text == ""
                    or t("errors.enter_valid_number"),
                    style=self.qstyle,
                    default="0",
                ).ask()

                if dependents_str is None:
                    return 0

                dependents = int(dependents_str)
                if dependents < 0:
                    self.console.print(f"[red]{t('errors.negative_dependents')}[/red]")
                    continue
                return dependents
            except ValueError:
                self.console.print(f"[red]{t('errors.invalid_whole_number')}[/red]")

    def get_monthly_income(self) -> tuple[float, Currency]:
        """
        Prompt user for monthly income and validate input

        Returns:
            Tuple of (monthly_income, currency)
        """
        # Ask for currency first
        currency = questionary.select(
            t("input.currency_prompt"),
            choices=[
                Choice(t("input.currency_ves"), value=Currency.VES),
                Choice(t("input.currency_usd"), value=Currency.USD),
            ],
            style=self.qstyle,
        ).ask()

        if not currency:
            return 0, Currency.VES

        while True:
            try:
                income_str = questionary.text(
                    t("input.income_prompt", currency=currency),
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
                    or t("errors.enter_valid_number"),
                    style=self.qstyle,
                    default="",
                ).ask()

                if income_str is None:
                    return 0, currency

                income = float(income_str.replace(",", "").replace(" ", ""))
                if income < 0:
                    self.console.print(f"[red]{t('errors.negative_income')}[/red]")
                    continue
                return income, currency
            except ValueError:
                self.console.print(f"[red]{t('errors.invalid_number')}[/red]")

    def display_tax_brackets(self, tax_brackets: list[TaxBracket], ut_value: float):
        """Display the tax brackets table"""
        table = Table(title=t("brackets.title"), box=box.ROUNDED)

        table.add_column(t("brackets.income_range_ut"), style="cyan", justify="right")
        table.add_column(t("brackets.income_range_bs"), style="cyan", justify="right")
        table.add_column(t("brackets.tax_rate"), style="magenta", justify="center")
        table.add_column(t("brackets.subtract_ut"), style="yellow", justify="right")

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
            t("results.annual_income_ves"), f"{result.annual_income_ves:,.2f} Bs."
        )
        results_table.add_row(
            t("results.annual_income_usd"), f"${result.annual_income_usd:,.2f}"
        )
        results_table.add_row(t("results.income_ut"), f"{result.income_ut:,.2f} UT")
        results_table.add_row(
            t("results.standard_deduction"), f"{result.standard_deduction_ut:,.2f} UT"
        )
        results_table.add_row(
            t("results.taxable_income"), f"{result.taxable_income_ut:,.2f} UT"
        )
        results_table.add_row(t("results.marginal_rate"), f"{result.bracket_rate:.0f}%")
        results_table.add_row(
            t("results.taxpayer_credit"), f"{result.taxpayer_credit_ut:.2f} UT"
        )
        if result.dependents > 0:
            results_table.add_row(
                t("results.dependent_credits", count=result.dependents),
                f"{result.dependents_credit_ut:,.2f} UT",
            )
        results_table.add_row("", "")
        results_table.add_row(
            t("results.total_tax_ut"), f"[bold yellow]{result.total_tax_ut:,.2f} UT[/]"
        )
        results_table.add_row(
            t("results.total_tax_ves"),
            f"[bold yellow]{result.total_tax_ves:,.2f} Bs.[/]",
        )
        results_table.add_row(
            t("results.total_tax_usd"), f"[bold yellow]${result.total_tax_usd:,.2f}[/]"
        )
        results_table.add_row("", "")
        results_table.add_row(
            t("results.effective_rate"),
            f"[bold magenta]{result.effective_rate:.2f}%[/]",
        )
        results_table.add_row(
            t("results.net_income_ves"),
            f"[bold green]{result.net_income_ves:,.2f} Bs.[/]",
        )
        results_table.add_row(
            t("results.net_income_usd"), f"[bold green]${result.net_income_usd:,.2f}[/]"
        )

        panel = Panel(
            results_table,
            title=t("results.title"),
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
        breakdown_table.add_column(t("breakdown.step"), style="dim cyan", no_wrap=True)
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
            title=t("breakdown.title"),
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
        self.console.print(f"[bold green]{t('messages.goodbye')}[/bold green]")
