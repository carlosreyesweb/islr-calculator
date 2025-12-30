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

from models import TaxBracket


@dataclass
class Config:
    """Configuration for the ISLR calculator"""

    ut_value: float
    usd_to_ves: float
    standard_deduction_ut: float
    tax_brackets: list[TaxBracket]


def load_config(console: Console) -> Config:
    """Load configuration from environment variables and files"""
    load_dotenv()

    # Get UT_VALUE from environment variable
    ut_value_str = os.getenv("UT_VALUE")
    if ut_value_str is None:
        console.print(
            "[bold red]Error: UT_VALUE environment variable is not set.[/bold red]"
        )
        console.print(
            "[yellow]Please set UT_VALUE before running the calculator.[/yellow]"
        )
        console.print("[dim]Example: export UT_VALUE=43.0[/dim]")
        sys.exit(1)

    try:
        ut_value = float(ut_value_str)
    except ValueError:
        console.print(
            f"[bold red]Error: UT_VALUE '{ut_value_str}' is not a valid number.[/bold red]"
        )
        sys.exit(1)

    # Get USD_TO_VES from environment variable
    usd_to_ves_str = os.getenv("USD_TO_VES")
    if usd_to_ves_str is None:
        console.print(
            "[bold red]Error: USD_TO_VES environment variable is not set.[/bold red]"
        )
        console.print(
            "[yellow]Please set USD_TO_VES before running the calculator.[/yellow]"
        )
        console.print("[dim]Example: export USD_TO_VES=50.0[/dim]")
        sys.exit(1)

    try:
        usd_to_ves = float(usd_to_ves_str)
    except ValueError:
        console.print(
            f"[bold red]Error: USD_TO_VES '{usd_to_ves_str}' is not a valid number.[/bold red]"
        )
        sys.exit(1)

    # Get STANDARD_DEDUCTION_UT from environment variable
    standard_deduction_ut_str = os.getenv("STANDARD_DEDUCTION_UT")
    if standard_deduction_ut_str is None:
        console.print(
            "[bold red]Error: STANDARD_DEDUCTION_UT environment variable is not set.[/bold red]"
        )
        console.print(
            "[yellow]Please set STANDARD_DEDUCTION_UT before running the calculator.[/yellow]"
        )
        console.print("[dim]Example: export STANDARD_DEDUCTION_UT=775[/dim]")
        sys.exit(1)

    try:
        standard_deduction_ut = float(standard_deduction_ut_str)
    except ValueError:
        console.print(
            f"[bold red]Error: STANDARD_DEDUCTION_UT '{standard_deduction_ut_str}' is not a valid number.[/bold red]"
        )
        sys.exit(1)

    # Load tax brackets
    tax_brackets = load_tax_brackets_from_csv(console)

    return Config(
        ut_value=ut_value,
        usd_to_ves=usd_to_ves,
        standard_deduction_ut=standard_deduction_ut,
        tax_brackets=tax_brackets,
    )


def load_tax_brackets_from_csv(
    console: Console, filepath: str = "tax_brackets.csv"
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
    csv_path = Path(__file__).parent / filepath

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
                f"[bold red]Error: No tax brackets found in {filepath}[/bold red]"
            )
            sys.exit(1)

        return brackets

    except FileNotFoundError:
        console.print(
            f"[bold red]Error: Tax brackets file '{filepath}' not found.[/bold red]"
        )
        console.print(
            "[yellow]Please ensure the CSV file exists in the project directory.[/yellow]"
        )
        sys.exit(1)
    except (KeyError, ValueError) as e:
        console.print(
            f"[bold red]Error: Invalid format in tax brackets CSV: {e}[/bold red]"
        )
        console.print(
            "[yellow]Expected columns: min_ut, max_ut, rate, subtract_ut[/yellow]"
        )
        sys.exit(1)
