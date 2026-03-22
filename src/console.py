"""
Console module for ISLR Calculator
Handles all UI rendering, prompts, and display logic
"""

from datetime import date, datetime

import questionary
from questionary import Choice
from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from src.i18n import t
from src.models import (
    CalculationStep,
    CalculatorMode,
    Currency,
    InstallmentPlan,
    TaxBracket,
    TaxCalculationResult,
)


class ConsoleUI:
    """Console UI handler for ISLR Calculator"""

    def __init__(self, console: Console = None):
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
        usd_rate_is_live: bool = False,
        usd_rate_updated_at: str | None = None,
    ):
        """Display the application header with current config values"""
        title = Text(t("app.title"), style="bold blue")

        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Label", style="bold cyan")
        info_table.add_column("Value", style="bold white")

        info_table.add_row(t("header.ut_value"), f"{ut_value} Bs.")

        # USD rate row: show source tag and update date if live
        if usd_rate_is_live:
            date_hint = f"  ({usd_rate_updated_at[:10]})" if usd_rate_updated_at else ""
            usd_label = (
                t("header.usd_rate")
                + f" [dim]{t('header.usd_rate_live')}{date_hint}[/dim]"
            )
        else:
            usd_label = (
                t("header.usd_rate") + f" [dim]{t('header.usd_rate_fallback')}[/dim]"
            )
        info_table.add_row(usd_label, f"{usd_to_ves} Bs.")

        info_table.add_row(
            t("header.standard_deduction"), f"{standard_deduction_ut} UT"
        )
        info_table.add_row(t("header.taxpayer_credit"), f"{taxpayer_credit_ut} UT")
        info_table.add_row(t("header.dependent_credit"), f"{dependent_credit_ut} UT")
        info_table.add_row("", "")
        info_table.add_row(
            Text(t("messages.credit_header"), style="dim"),
            "",
        )

        self.console.print(Panel(info_table, title=title, border_style="blue"))

    def display_menu(self) -> str:
        """
        Display main menu.

        Returns:
            "1" = declaration, "2" = simulation, "3" = view brackets, "4" = exit
        """
        choice = questionary.select(
            t("menu.prompt"),
            choices=[
                Choice(t("menu.declare_tax"), value="1"),
                Choice(t("menu.simulate_tax"), value="2"),
                Choice(t("menu.view_brackets"), value="3"),
                Choice(t("menu.exit"), value="4"),
            ],
            style=self.qstyle,
        ).ask()

        return choice if choice else "4"

    def get_income(
        self, mode: CalculatorMode = CalculatorMode.DECLARATION
    ) -> tuple[float, Currency]:
        """
        Ask for currency and income amount.

        Declaration mode: asks for annual income.
        Simulation mode: asks for monthly income.

        Returns:
            Tuple of (income_amount, currency)
        """
        currency = questionary.select(
            t("input.currency_prompt"),
            choices=[
                Choice(t("input.currency_ves"), value=Currency.VES),
                Choice(t("input.currency_usd"), value=Currency.USD),
            ],
            style=self.qstyle,
        ).ask()

        if not currency:
            return 0.0, Currency.VES

        prompt = (
            t("input.income_prompt_declaration", currency=currency)
            if mode == CalculatorMode.DECLARATION
            else t("input.income_prompt_simulation", currency=currency)
        )

        while True:
            try:
                income_str = questionary.text(
                    prompt,
                    validate=lambda text: (
                        text.replace(",", "")
                        .replace(" ", "")
                        .replace(".", "", 1)
                        .replace("-", "", 1)
                        .isdigit()
                        or text.replace(",", "")
                        .replace(" ", "")
                        .replace(".", "", 1)
                        .replace("-", "", 1)
                        == ""
                        or t("errors.enter_valid_number")
                    ),
                    style=self.qstyle,
                    default="",
                ).ask()

                if income_str is None:
                    return 0.0, currency

                income = float(income_str.replace(",", "").replace(" ", ""))
                if income < 0:
                    self.console.print(f"[red]{t('errors.negative_income')}[/red]")
                    continue
                return income, currency
            except ValueError:
                self.console.print(f"[red]{t('errors.invalid_number')}[/red]")

    def get_number_of_dependents(self) -> int:
        """Ask how many direct dependents the user has."""
        while True:
            try:
                dependents_str = questionary.text(
                    t("input.dependents_prompt"),
                    validate=lambda text: (
                        text.isdigit() or text == "" or t("errors.enter_valid_number")
                    ),
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
                "inf"
                if bracket.max_ut == float("inf")
                else f"{bracket.max_ut * ut_value:,.2f}"
            )
            max_ut = (
                "inf" if bracket.max_ut == float("inf") else f"{bracket.max_ut:,.0f}"
            )

            table.add_row(
                f"{bracket.min_ut:,.0f} - {max_ut}",
                f"{min_ves} - {max_ves}",
                f"{bracket.rate * 100:.0f}%",
                f"{bracket.subtract_ut:,.0f} UT",
            )

        self.console.print(table)

    def display_results(
        self,
        result: TaxCalculationResult,
        mode: CalculatorMode = CalculatorMode.DECLARATION,
        monthly_income_ves: float | None = None,
    ):
        """
        Display tax calculation results.

        Summary section shows what the user owes and their net income.
        Details section shows annual income, marginal rate, and credits - all in Bs.
        UT values are not shown to the user.

        Args:
            result: TaxCalculationResult from calculator
            mode: DECLARATION or SIMULATION (affects title and notice)
            monthly_income_ves: Raw monthly income in Bs (simulation mode only, for display)
        """
        # --- Summary ---
        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column("Label", style="bold cyan")
        summary_table.add_column("Value", style="bold white")

        summary_table.add_row(
            t("results.total_tax_ves"),
            f"[bold yellow]{result.total_tax_ves:,.2f} Bs.[/]",
        )
        summary_table.add_row(
            t("results.total_tax_usd"),
            f"[bold yellow]${result.total_tax_usd:,.2f}[/]",
        )
        summary_table.add_row("", "")
        summary_table.add_row(
            t("results.net_income_ves"),
            f"[bold green]{result.net_income_ves:,.2f} Bs.[/]",
        )
        summary_table.add_row(
            t("results.net_income_usd"),
            f"[bold green]${result.net_income_usd:,.2f}[/]",
        )
        summary_table.add_row("", "")
        summary_table.add_row(
            t("results.effective_rate"),
            f"[bold magenta]{result.effective_rate:.2f}%[/]",
        )

        # --- Details ---
        details_table = Table(show_header=False, box=None, padding=(0, 2))
        details_table.add_column("Label", style="cyan")
        details_table.add_column("Value", style="white")

        # Annual income (with USD conversion note if applicable)
        if result.currency == Currency.USD:
            details_table.add_row(
                t("results.annual_income"),
                f"${result.annual_income_usd:,.2f} -> {result.annual_income_ves:,.2f} Bs.",
            )
        else:
            details_table.add_row(
                t("results.annual_income"),
                f"{result.annual_income_ves:,.2f} Bs.",
            )

        details_table.add_row(t("results.marginal_rate"), f"{result.bracket_rate:.0f}%")

        if result.credits_ves > 0:
            details_table.add_row(
                t("results.credits_applied"),
                f"{result.credits_ves:,.2f} Bs.",
            )

        # Simulation-only: show the monthly basis
        if mode == CalculatorMode.SIMULATION and monthly_income_ves is not None:
            details_table.add_row(
                t("results.simulation_monthly_basis"),
                f"{monthly_income_ves:,.2f} Bs.",
            )

        # --- Compose panel ---
        title = (
            t("results.title_simulation")
            if mode == CalculatorMode.SIMULATION
            else t("results.title")
        )

        content = []
        if mode == CalculatorMode.SIMULATION:
            content.append(Text(t("results.simulation_notice"), style="dim yellow"))
            content.append(Text(""))
        content += [
            summary_table,
            Rule(style="dim green"),
            Text(t("results.details_header"), style="dim cyan"),
            details_table,
        ]

        panel = Panel(
            Group(*content),
            title=title,
            border_style="green" if mode == CalculatorMode.DECLARATION else "yellow",
            box=box.DOUBLE,
        )

        self.console.print(panel)

    def display_calculation_breakdown(self, steps: list[CalculationStep]):
        """Display the calculation breakdown steps"""
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

    def get_declaration_date(self, fiscal_year: int) -> date:
        """
        Ask the user when they plan to file their declaration.

        Defaults to March 31 of fiscal_year + 1.
        """
        default_date = date(fiscal_year + 1, 3, 31)
        default_str = default_date.strftime("%d/%m/%Y")

        def validate_date(text: str) -> bool | str:
            text = text.strip()
            if not text:
                return True
            try:
                datetime.strptime(text, "%d/%m/%Y")
                return True
            except ValueError:
                return t("errors.invalid_date")

        while True:
            date_str = questionary.text(
                t("input.declaration_date_prompt", year=fiscal_year + 1),
                default=default_str,
                validate=validate_date,
                style=self.qstyle,
            ).ask()

            if date_str is None or date_str.strip() == "":
                return default_date

            try:
                return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
            except ValueError:
                self.console.print(f"[red]{t('errors.invalid_date')}[/red]")

    def display_installment_plan(self, plan: InstallmentPlan):
        """Display the 3-installment payment plan"""
        table = Table(box=box.ROUNDED)
        table.add_column(
            t("installments.installment_col"), style="bold cyan", justify="center"
        )
        table.add_column(t("installments.date_col"), style="white", justify="center")
        table.add_column(
            t("installments.amount_ves_col"), style="bold yellow", justify="right"
        )
        table.add_column(
            t("installments.amount_usd_col"), style="bold yellow", justify="right"
        )

        for i, due_date in enumerate(plan.dates, start=1):
            table.add_row(
                f"{i}/3",
                due_date.strftime("%d %b %Y"),
                f"{plan.amount_per_installment_ves:,.2f} Bs.",
                f"${plan.amount_per_installment_usd:,.2f}",
            )

        note = Text(
            t(
                "installments.note",
                days=plan.installment_days,
                days_x2=plan.installment_days * 2,
            ),
            style="dim",
        )

        self.console.print(
            Panel(
                Group(table, note),
                title=t("installments.title"),
                border_style="yellow",
                box=box.ROUNDED,
            )
        )

    def confirm(self, message: str, default: bool = True) -> bool:
        """Show a Yes/No confirmation prompt"""
        result = questionary.confirm(message, default=default, style=self.qstyle).ask()
        return result if result is not None else default

    def show_goodbye_message(self):
        """Display goodbye message with developer credit"""
        self.console.print(f"\n[bold green]{t('messages.goodbye')}[/bold green]")
        self.console.print(f"[dim]{t('messages.credit_footer')}[/dim]\n")
