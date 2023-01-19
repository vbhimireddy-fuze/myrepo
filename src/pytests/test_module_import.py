# coding=utf-8

# content of test_example.py
# Check PyTest documentation for more - https://docs.pytest.org/en/6.2.x/contents.html

import barcode_service


def test_version_object_type():
    assert isinstance(barcode_service.barcodemain.SERVICE_VERSION, str)
