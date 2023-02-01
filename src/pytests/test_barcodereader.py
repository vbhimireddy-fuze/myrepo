from pathlib import Path
from barcode_service.zbarreader import zbar_barcode_extractor
from barcode_service.barcodereader import BarcodeReader, Barcode

TEST_DATA_LOCATION = Path(__file__).parent / "resources" / "images"

def test_read_barcode():
    conf = BarcodeReader.BarcodeConfiguration(faxes_location = TEST_DATA_LOCATION)
    barcoder = BarcodeReader(conf, zbar_barcode_extractor)
    with_barcode = "barcode.tif"
    codes = barcoder.read_barcode(with_barcode)
    expected = (Barcode(page_no=1, format='CODE128', raw_result='kelly.troy@aerocareusa.com'),)
    assert expected == codes


def test_nobarcode_read_barcode():
    conf = BarcodeReader.BarcodeConfiguration(faxes_location = TEST_DATA_LOCATION)
    barcoder = BarcodeReader(conf, zbar_barcode_extractor)
    without_barcode = "nobarcode.tif"
    codes = barcoder.read_barcode(without_barcode)
    expected = ()
    assert expected == codes
