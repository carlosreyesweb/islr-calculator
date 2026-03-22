"""
Configuration module for ISLR Calculator
Handles loading of environment variables and configuration files
"""

import csv
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from src.i18n import t
from src.models import TaxBracket


BCV_API_URL = "https://ve.dolarapi.com/v1/dolares/oficial"
BCV_API_TIMEOUT = 3  # seconds


@dataclass
class Config:
    """Configuration for the ISLR calculator"""

    ut_value: float
    usd_to_ves: float
    usd_rate_is_live: bool  # True if fetched from BCV API, False if from .env
    usd_rate_updated_at: str | None  # fechaActualizacion from API, or None if fallback
    standard_deduction_ut: float
    taxpayer_credit_ut: float
    dependent_credit_ut: float
    installment_days: int
    tax_brackets: list[TaxBracket]


def fetch_usd_rate() -> tuple[float, str] | None:
    """
    Fetch the current official BCV USD/VES rate from ve.dolarapi.com.

    Returns:
        Tuple of (rate, fechaActualizacion) if successful, None otherwise.
    """
    try:
        req = urllib.request.Request(
            BCV_API_URL,
            headers={"User-Agent": "islr-calculator/1.0"},
        )
        with urllib.request.urlopen(req, timeout=BCV_API_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            rate = float(data["promedio"])
            updated_at = data.get("fechaActualizacion", "")
            return rate, updated_at
    except (urllib.error.URLError, KeyError, ValueError, TimeoutError):
        return None


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

    # Try to fetch live USD/VES rate from BCV API
    usd_rate_is_live = False
    usd_rate_updated_at = None
    live_result = fetch_usd_rate()

    if live_result is not None:
        usd_to_ves, usd_rate_updated_at = live_result
        usd_rate_is_live = True
    else:
        # Fall back to USD_TO_VES from .env
        console.print(f"[yellow]{t('config_errors.usd_rate_fetch_failed')}[/yellow]")
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

    # Get INSTALLMENT_DAYS from environment variable (optional, default 20)
    installment_days = 20
    installment_days_str = os.getenv("INSTALLMENT_DAYS")
    if installment_days_str is not None:
        try:
            installment_days = int(installment_days_str)
        except ValueError:
            console.print(
                f"[yellow]Warning: INSTALLMENT_DAYS '{installment_days_str}' is not a valid integer. Using default of 20.[/yellow]"
            )

    # Load tax brackets
    tax_brackets = load_tax_brackets_from_csv(console)

    return Config(
        ut_value=ut_value,
        usd_to_ves=usd_to_ves,
        usd_rate_is_live=usd_rate_is_live,
        usd_rate_updated_at=usd_rate_updated_at,
        standard_deduction_ut=standard_deduction_ut,
        taxpayer_credit_ut=taxpayer_credit_ut,
        dependent_credit_ut=dependent_credit_ut,
        installment_days=installment_days,
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
