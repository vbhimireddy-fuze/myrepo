from pathlib import Path

import pytest

from barcode_service.barcodereader import Barcode, BarcodeReader
from barcode_service.zbarreader import zbar_barcode_extractor

TEST_DATA_LOCATION = Path(__file__).parent / "resources" / "images"


@pytest.mark.parametrize(
    "barcodes_file, expected_barcodes",
    [
        ("barcode.tif", (Barcode(page_no=1, format='CODE128', raw_result='kelly.troy@aerocareusa.com'),),),
        ("nobarcode.tif", tuple(),),
        ("brandon_jenkins_adapthealth.tif", (Barcode(page_no=2, format='CODE128', raw_result='Brandon.Jenkins@adapthealth.com'),))
    ],
)
def test_barcode_reader(barcodes_file, expected_barcodes):
    conf = BarcodeReader.BarcodeConfiguration(faxes_location = TEST_DATA_LOCATION)
    barcoder = BarcodeReader(conf, zbar_barcode_extractor)
    assert expected_barcodes == barcoder.read_barcode(barcodes_file)
