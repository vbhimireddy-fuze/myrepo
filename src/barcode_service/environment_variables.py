"""
    This module implements the necessary features to obtain the required information for
    the barcode service operation, from environment variables.
"""

from dataclasses import dataclass
from os import getenv

_LOCAL_CONFIG_HOST = 'http://configservice:8087' # Default value points to Spring Config service from Cloud8 local environment. Used for testing.
_LOCAL_LABEL = 'master' # Default value points to Spring Config master branch from Cloud8 local environment. Used for testing.

__all__ = (
    "EnvironmentConfigurations",
    "get_environment_variable_configurations",
)


@dataclass
class EnvironmentConfigurations():
    spring_config_host: str
    spring_config_label: str


def get_environment_variable_configurations() -> EnvironmentConfigurations:
    return EnvironmentConfigurations(
        spring_config_host=getenv('CONFIG_HOST', _LOCAL_CONFIG_HOST),
        spring_config_label=getenv('SPRING_CLOUD_CONFIG_LABEL', _LOCAL_LABEL),
    )
