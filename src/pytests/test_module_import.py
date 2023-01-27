"""
    Unit test set to test import of the barcode_service module
"""

from packaging import version

import barcode_service


def test_version_object_type():
    """
        This test has two objectives:
            1) Test if importing the barcode_service module works without failures
            2) Test if the SERVICE_VERSION variable is referencing a str
    """
    assert isinstance(barcode_service.barcodemain.SERVICE_VERSION, str)
    assert isinstance(version.parse(barcode_service.barcodemain.SERVICE_VERSION), version.Version)
