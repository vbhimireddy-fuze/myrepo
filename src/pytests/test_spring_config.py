"""
    This unit test set tests the spring config features
"""
from dataclasses import dataclass

import pytest
from requests import exceptions

from barcode_service.spring_config import (
    SpringConfigException,
    get_configurations_from_cloud8_spring_config_service)

_YAML_MOCK_DATA='''
yaml_test_data: "testing data"
'''


@dataclass
class RequestsResultMock():
    """
        Requests Resut MockUp
    """
    status_code: int
    reason: str
    text: str


def requests_get_mock(result: dict[str, RequestsResultMock], url, *_):
    """
        requests.get function mockup
    """
    if 'barcode-service-configuration.yaml' in url:
        return result['service_config']
    if 'barcode-logger-configuration.yaml' in url:
        return result['log_config']
    assert False


def test_get_data_from_mock_of_spring_config_service(monkeypatch):
    """
        Tests the get_configurations_from_cloud8_spring_config_service function.
        Verifies if it is properly returning what the requests results returns.
    """
    requests_fake_result = {
        "service_config": RequestsResultMock(
            status_code=200,
            reason="OK",
            text=_YAML_MOCK_DATA,
        ),
        "log_config": RequestsResultMock(
            status_code=200,
            reason="OK",
            text=_YAML_MOCK_DATA,
        ),
    }

    with monkeypatch.context() as patch:
        patch.setattr("requests.get", (lambda url, timeout, result=requests_fake_result: requests_get_mock(result, url, timeout)))
        spring_configurations = get_configurations_from_cloud8_spring_config_service("http://springconfigmock", "label_mock")
        assert spring_configurations.barcode_service_configuration == _YAML_MOCK_DATA
        assert spring_configurations.barcode_logger_configuration == _YAML_MOCK_DATA


def test_exception_from_get_service_config(monkeypatch):
    """
        Tests the get_configurations_from_cloud8_spring_config_service function.
        Verifies if it throws an exception when requests.get returns an error when requesting the service configuration.
    """
    service_config_request_mock = RequestsResultMock(
        status_code=300,
        reason="Mock Error",
        text="",
    )
    requests_fake_result = { "service_config": service_config_request_mock }

    with monkeypatch.context() as patch:
        patch.setattr("requests.get", (lambda url, timeout, result=requests_fake_result: requests_get_mock(result, url, timeout)))

        with pytest.raises(SpringConfigException) as ex:
            get_configurations_from_cloud8_spring_config_service("http://springconfigmock", "label_mock")
            assert "Could not obtain service configuration file from Spring Config Service:" in str(ex)
            assert f"Error Code: [{service_config_request_mock.status_code}]" in str(ex)
            assert f"Error Reason: [{service_config_request_mock.reason}]" in str(ex)


def test_exception_from_get_logger_config(monkeypatch):
    """
        Tests the get_configurations_from_cloud8_spring_config_service function.
        Verifies if it throws an exception when requests.get returns an error when requesting the logger configuration.
    """
    logger_config_request_mock = RequestsResultMock(
        status_code=300,
        reason="Mock Error",
        text="",
    )

    requests_fake_result = {
        "service_config": RequestsResultMock(
            status_code=200,
            reason="OK",
            text=_YAML_MOCK_DATA,
        ),
        "log_config": logger_config_request_mock,
    }

    with monkeypatch.context() as patch:
        patch.setattr("requests.get", (lambda url, timeout, result=requests_fake_result: requests_get_mock(result, url, timeout)))

        with pytest.raises(SpringConfigException) as ex:
            get_configurations_from_cloud8_spring_config_service("http://springconfigmock", "label_mock")
            assert "Could not obtain logger configuration file from Spring Config Service:" in str(ex)
            assert f"Error Code: [{logger_config_request_mock.status_code}]" in str(ex)
            assert f"Error Reason: [{logger_config_request_mock.reason}]" in str(ex)


def test_connection_error_exception_from_get_service_config(monkeypatch):
    """
        Tests the get_configurations_from_cloud8_spring_config_service function.
        Verifies if it throws an SpringConfigException when requests.get returns a connection error.
    """

    def requests_get_throws_connection_error_mockup():
        raise exceptions.ConnectionError("Mockup Error")

    with monkeypatch.context() as patch:
        patch.setattr("requests.get", (lambda *_, **_1: requests_get_throws_connection_error_mockup()))

        with pytest.raises(SpringConfigException) as ex:
            get_configurations_from_cloud8_spring_config_service("http://springconfigmock", "label_mock")
            assert "Could not connect to Spring Config Service" in str(ex)
