from barcode_service.avroparser import AvroEnc, AvroDec


def test_enc_dec():
    with open('../barcode_service/resources/reader.avsc', encoding="utf-8") as file:
        schema_txt = file.read()
    enc = AvroEnc(schema_txt)
    dec = AvroDec(schema_txt)
    msg = {
       "uuid":"579182d9-d827-435a-a91e-5ab6af28b5fb",
       "customerId":"0010r00000BF40SAAT",
       "userId":"KZGW7_R5TNmYGusP5y0Lvg",
       "faxId":"f2882f59916143f0bca1b4becdff602e",
       "subject":"",
       "fileName":"03aa178f6736421aad569fc4bedaba6f.pdf",
       "subscriberId":"Gg30YjCTQneGIJCWHFIwOA-INTERNET_FAX",
       "from":"14086278887",
       "to":"16014320257",
       "remotePartyId":"14086278887",
       "state":"completed",
       "cause":{
          "systemCode":"1001",
          "userString":"Normal.",
          "userCode":"2001"
       },
       "sentPage":"1/1",
       "receivedPage":"None",
       "retryCount":0,
       "startTimestamp":1669095140000,
       "updateTimestamp":1669066419457,
       "direction":"outgoing",
       "hqFax":"yes",
       "countryCode":"-US",
       "fromDid":"+14086278887",
       "toDid":"+16014320257",
       "subscriptionId":"06xGIVUxQ7OXorsZzt2WPw"
    }
    encoded = enc.encode(msg)
    decoded = dec.decode_confluent(encoded)

    assert msg == decoded
