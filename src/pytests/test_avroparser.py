from importlib.resources import open_text as open_resource_text

from pytests.shared_data import KAFKA_FAX_DATA

from barcode_service.avroparser import AvroDec, AvroEnc


def test_enc_dec():
    # Loading Producer Schema
    with open_resource_text("barcode_service.resources", "reader.avsc") as resource_file:
        schema_txt = resource_file.read()

    enc = AvroEnc(schema_txt)
    dec = AvroDec(schema_txt)

    encoded = enc.encode(KAFKA_FAX_DATA)
    decoded = dec.decode_confluent(encoded)

    assert KAFKA_FAX_DATA == decoded
