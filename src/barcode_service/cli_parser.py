# coding=utf-8
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from barcode_service.version import SERVICE_VERSION

__all__ = ["parse_arguments"]

def parse_arguments() -> ArgumentParser:
    """
    CLI Parameters parser
    """
    def validate_file_path(location: str) -> Path:
        loc = Path(location)
        if not loc.exists():
            raise ArgumentTypeError(f"File [{loc}] does not exist.")
        if not loc.is_file():
            raise ArgumentTypeError(f"Location [{loc}] does not reference a file.")
        return loc

    parser = ArgumentParser(prog="barcode_service", description=f"Barcode Service v{SERVICE_VERSION}")
    parser.add_argument(
        "-sl",
        "--service_config_location",
        help="Service configuration (YAML) file path.",
        required=True,
        type=validate_file_path,
    )
    parser.add_argument(
        "-ll",
        "--log_config_location",
        help="Log configuration (YAML) file path.",
        required=True,
        type=validate_file_path,
    )
    return parser
