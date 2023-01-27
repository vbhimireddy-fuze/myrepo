import logging
from dataclasses import dataclass

import requests

__all__ = (
    "SpringConfigException",
    "get_configurations_from_cloud8_spring_config_service",
)

_BARCODE_SERVICE_CONFIGURATION_FILENAME = 'barcode-service-configuration.yaml'
_BARCODE_LOGGER_CONFIGURATION_FILENAME = 'barcode-logger-configuration.yaml'
_URL_FORMAT = '{server:s}/{label:s}/{file:s}'

_log = logging.getLogger(__name__)

class SpringConfigException(RuntimeError):
    pass


@dataclass
class SpringConfigurations():
    barcode_service_configuration: str
    barcode_logger_configuration: str


def get_configurations_from_cloud8_spring_config_service(config_host: str, label: str) -> SpringConfigurations:
    try:
        _log.info(f"Spring Configurations: CONFIG_HOST: [{config_host}]; SPRING_CLOUD_CONFIG_LABEL: [{label}];")

        label = label.replace("/", "(_)")

        response = requests.get(_URL_FORMAT.format(server=config_host, label=label, file=_BARCODE_SERVICE_CONFIGURATION_FILENAME), timeout=5)
        if response.status_code != 200:
            raise SpringConfigException(
                f"Could not obtain service configuration file from Spring Config Service: "
                f"Error Code: [{response.status_code}]"
                f"Error Reason: [{response.reason}]"
            )
        barcode_service_configuration: str = response.text

        response = requests.get(_URL_FORMAT.format(server=config_host, label=label, file=_BARCODE_LOGGER_CONFIGURATION_FILENAME), timeout=5)
        if response.status_code != 200:
            raise SpringConfigException(
                f"Could not obtain logger configuration file from Spring Config Service: "
                f"Error Code: [{response.status_code}]"
                f"Error Reason: [{response.reason}]"
            )
        barcode_logger_configuration: str = response.text

        return SpringConfigurations(barcode_service_configuration, barcode_logger_configuration)
    except requests.exceptions.ConnectionError as ex:
        raise SpringConfigException("Could not connect to Spring Config Service") from ex
