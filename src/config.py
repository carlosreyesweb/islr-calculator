"""
Configuration module for ISLR Calculator
Handles loading of environment variables and configuration files
"""

import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from src.i18n import t
from src.models import TaxBracket


@dataclass
class Config:
    """Configuration for the ISLR calculator"""

    ut_value: float
    usd_to_ves: float
    standard_deduction_ut: float
    taxpayer_credit_ut: float
    dependent_credit_ut: float
    tax_brackets: list[TaxBracket]


def load_config(console: Console) -> Config:
    """Load configuration from environment variables and files"""
    load_dotenv()

    # Get UT_VALUE from environment variable
    ut_value_str = os.getenv("UT_VALUE")
    if ut_value_str is None:
        console.print(f"[bold red]{t('config_errors.ut_value_not_set')}[/bold red]")
        console.print(f"[yellow]{t('config_errors.please_set_ut_value')}[/yellow]")
        console.print(f"[dim]{t('config_errors.example_ut_value')}[/dim]")
        sys.exit(1)

    try:
        ut_value = float(ut_value_str)
    except ValueError:
        console.print(
            f"[bold red]{t('config_errors.ut_value_invalid', value=ut_value_str)}[/bold red]"
        )
        sys.exit(1)

    # Get USD_TO_VES from environment variable
    usd_to_ves_str = os.getenv("USD_TO_VES")
    if usd_to_ves_str is None:
        console.print(f"[bold red]{t('config_errors.usd_rate_not_set')}[/bold red]")
        console.print(f"[yellow]{t('config_errors.please_set_usd_rate')}[/yellow]")
        console.print(f"[dim]{t('config_errors.example_usd_rate')}[/dim]")
        sys.exit(1)

    try:
        usd_to_ves = float(usd_to_ves_str)
    except ValueError:
        console.print(
            f"[bold red]{t('config_errors.usd_rate_invalid', value=usd_to_ves_str)}[/bold red]"
        )
        sys.exit(1)

    # Get STANDARD_DEDUCTION_UT from environment variable
    standard_deduction_ut_str = os.getenv("STANDARD_DEDUCTION_UT")
    if standard_deduction_ut_str is None:
        console.print(
            f"[bold red]{t('config_errors.standard_deduction_not_set')}[/bold red]"
        )
        console.print(
            f"[yellow]{t('config_errors.please_set_standard_deduction')}[/yellow]"
        )
        console.print(f"[dim]{t('config_errors.example_standard_deduction')}[/dim]")
        sys.exit(1)

    try:
        standard_deduction_ut = float(standard_deduction_ut_str)
    except ValueError:
        console.print(
            f"[bold red]{t('config_errors.standard_deduction_invalid', value=standard_deduction_ut_str)}[/bold red]"
        )
        sys.exit(1)

    # Get TAXPAYER_CREDIT_UT from environment variable
    taxpayer_credit_ut_str = os.getenv("TAXPAYER_CREDIT_UT")
    if taxpayer_credit_ut_str is None:
        console.print(
            f"[bold red]{t('config_errors.taxpayer_credit_not_set')}[/bold red]"
        )
        console.print(
            f"[yellow]{t('config_errors.please_set_taxpayer_credit')}[/yellow]"
        )
        console.print(f"[dim]{t('config_errors.example_taxpayer_credit')}[/dim]")
        sys.exit(1)

    try:
        taxpayer_credit_ut = float(taxpayer_credit_ut_str)
    except ValueError:
        console.print(
            f"[bold red]{t('config_errors.taxpayer_credit_invalid', value=taxpayer_credit_ut_str)}[/bold red]"
        )
        sys.exit(1)

    # Get DEPENDENT_CREDIT_UT from environment variable
    dependent_credit_ut_str = os.getenv("DEPENDENT_CREDIT_UT")
    if dependent_credit_ut_str is None:
        console.print(
            f"[bold red]{t('config_errors.dependent_credit_not_set')}[/bold red]"
        )
        console.print(
            f"[yellow]{t('config_errors.please_set_dependent_credit')}[/yellow]"
        )
        console.print(f"[dim]{t('config_errors.example_dependent_credit')}[/dim]")
        sys.exit(1)

    try:
        dependent_credit_ut = float(dependent_credit_ut_str)
    except ValueError:
        console.print(
            f"[bold red]{t('config_errors.dependent_credit_invalid', value=dependent_credit_ut_str)}[/bold red]"
        )
        sys.exit(1)

    # Load tax brackets
    tax_brackets = load_tax_brackets_from_csv(console)

    return Config(
        ut_value=ut_value,
        usd_to_ves=usd_to_ves,
        standard_deduction_ut=standard_deduction_ut,
        taxpayer_credit_ut=taxpayer_credit_ut,
        dependent_credit_ut=dependent_credit_ut,
        tax_brackets=tax_brackets,
    )


def load_tax_brackets_from_csv(
    console: Console, filename: str = "tax_brackets.csv"
) -> list[TaxBracket]:
    """
    Load tax brackets from a CSV file

    Args:
        console: Console instance for output
        filepath: Path to the CSV file containing tax brackets

    Returns:
        List of TaxBracket objects
    """
    brackets = []
    csv_path = Path(__file__).parent.parent / filename
    print(csv_path)

    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                bracket = TaxBracket(
                    min_ut=float(row["min_ut"]),
                    max_ut=float("inf")
                    if row["max_ut"].lower() == "inf"
                    else float(row["max_ut"]),
                    rate=float(row["rate"]),
                    subtract_ut=float(row["subtract_ut"]),
                )
                brackets.append(bracket)

        if not brackets:
            console.print(
                f"[bold red]{t('config_errors.no_brackets_found', filename=filename)}[/bold red]"
            )
            sys.exit(1)

        return brackets

    except FileNotFoundError:
        console.print(
            f"[bold red]{t('config_errors.brackets_file_not_found', filename=filename)}[/bold red]"
        )
        console.print(f"[yellow]{t('config_errors.ensure_csv_exists')}[/yellow]")
        sys.exit(1)
    except (KeyError, ValueError) as e:
        console.print(
            f"[bold red]{t('config_errors.invalid_csv_format', error=e)}[/bold red]"
        )
        console.print(f"[yellow]{t('config_errors.expected_columns')}[/yellow]")
        sys.exit(1)
