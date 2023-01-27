# coding=utf-8
from argparse import ArgumentParser, ArgumentTypeError, SUPPRESS
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
    subparsers = parser.add_subparsers(help='sub-command help')
    # create the parser for the "a" command
    config_files_parser = subparsers.add_parser('config_files', help='Runs Barcode Service using config files')
    spring_config_parser = subparsers.add_parser('spring_config', help='Runs Barcode Service using configurations from Spring Config service')
    spring_config_parser.add_argument("--spring_config", help=SUPPRESS, default=True)
    spring_config_parser.add_argument("--config_files", help=SUPPRESS, default=False)
    config_files_parser.add_argument(
        "-sl",
        "--service_config_location",
        help="Service configuration (YAML) file path.",
        required=True,
        type=validate_file_path,
    )
    config_files_parser.add_argument(
        "-ll",
        "--log_config_location",
        help="Log configuration (YAML) file path.",
        required=True,
        type=validate_file_path,
    )
    config_files_parser.add_argument("--spring_config", help=SUPPRESS, default=False)
    config_files_parser.add_argument("--config_files", help=SUPPRESS, default=True)
    return parser
