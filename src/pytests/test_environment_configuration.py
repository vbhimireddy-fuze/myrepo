"""
    This unit test set tests the environment configuration features
"""

from barcode_service.environment_variables import get_environment_variable_configurations


def test_get_default_configuration():
    """
        Tests the default values provided by get_environment_variable_configurations
    """
    data = get_environment_variable_configurations()
    assert data.spring_config_host == "http://configservice:8087"
    assert data.spring_config_label == "master"


def test_get_mockup_configuration(monkeypatch):
    """
        Tests the default values provided by get_environment_variable_configurations
    """
    MOCK_LOCATION = 'http://mock_location:12345'
    MOCK_LABEL = 'mock_label'

    with monkeypatch.context() as patch:
        patch.setenv('CONFIG_HOST', MOCK_LOCATION)
        patch.setenv('SPRING_CLOUD_CONFIG_LABEL', MOCK_LABEL)
        environment_config = get_environment_variable_configurations()
        assert isinstance(environment_config.spring_config_host, str)
        assert isinstance(environment_config.spring_config_label, str)
        assert environment_config.spring_config_host == MOCK_LOCATION
        assert environment_config.spring_config_label == MOCK_LABEL
