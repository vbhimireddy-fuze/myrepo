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
        ("brandon_jenkins_adapthealth.tif", (Barcode(page_no=2, format='CODE128', raw_result='Brandon.Jenkins@adapthealth.com'),),),
        ("L12.28.40.48(a-zA-Z0-9)(5P.5pp).tif", (
            Barcode(page_no=2, format='CODE128', raw_result="KT,P*}H]D(j"),
            Barcode(page_no=2, format='CODE128', raw_result="@A')/Z'aN!b'"),
            Barcode(page_no=2, format='CODE128', raw_result="~jOV1?~ohv8`"),
            Barcode(page_no=2, format='CODE128', raw_result='j6sp\nwAIqZ'),
            Barcode(page_no=2, format='CODE128', raw_result='NR"xn[VHhC=I'),
            Barcode(page_no=3, format='CODE128', raw_result="ZmZRdoX7SjnSJ6jL12DBh6BThyY9"),
            Barcode(page_no=3, format='CODE128', raw_result="cLr8SuKUJG6WJWZgOmA4FsXTNwYA"),
            Barcode(page_no=3, format='CODE128', raw_result="AhJqQgGvA23BDllYaSzbVYltaaLs"),
            Barcode(page_no=3, format='CODE128', raw_result="jAkT2xylXQtwdjuXm1LW5kVCJZJZ"),
            Barcode(page_no=3, format='CODE128', raw_result="37R2ruqxhWg1kQu1PmPXIBWTZRCB"),
            Barcode(page_no=4, format='CODE128', raw_result="A8Gtaglmxqwms9zLLgnlk0Daqm4ipyuZ2udDuWmD"),
            Barcode(page_no=4, format='CODE128', raw_result="a9Bj0L7uKt1yqIyTEUGyMFvYzNMxlBIfRZfjSwM7"),
            Barcode(page_no=4, format='CODE128', raw_result="p9gAisx8KWR2x2Uo1d8ukjZdR4Fnk43KKyTICX9q"),
            Barcode(page_no=4, format='CODE128', raw_result="OJX7RZWmKfTzKlgP2dtFVD1R4rdFhIakC2rHQ21g"),
            Barcode(page_no=4, format='CODE128', raw_result="pIABYI8GCmQ1jcuC4EB9ihXX9PONny6BCe2AW2vL"),
            Barcode(page_no=5, format='CODE128', raw_result="Xo2XrAJJtrFIE8bpHeVXOjipXCQ0ie2zJJN4O5pDdONCgVyg"),
            Barcode(page_no=5, format='CODE128', raw_result="cSAaYZ2sFRQ5sORKsKeWNnYMVCFWoQXrb0lTfwRmhDhWL2AW"),
            Barcode(page_no=5, format='CODE128', raw_result="ivsLY5XMmcvkW1B6vuPFNixqdsNnYAJNBp0qQRFklRRwnF8K"),
            Barcode(page_no=5, format='CODE128', raw_result="16epwtcRms3DgfegHPv12dkqS3zIfOhMBOmf18gabOtJsy4D"),
            Barcode(page_no=5, format='CODE128', raw_result="AtvHQHnagzktY4uPqDSluNwh2LwoYFpfYC9gTIs2bdAlZuz4"),
        ),),
    ],
)
def test_barcode_reader(barcodes_file, expected_barcodes):
    conf = BarcodeReader.BarcodeConfiguration(faxes_location = TEST_DATA_LOCATION)
    scanned_barcodes = BarcodeReader(conf, zbar_barcode_extractor).read_barcode(barcodes_file)
    assert all(barcode in scanned_barcodes for barcode in expected_barcodes)
