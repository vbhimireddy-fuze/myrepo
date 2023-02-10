from pathlib import Path

from barcode_service.confutil import ConfUtil

CONFIGURATIONS_LOCATION = Path(__file__).parent / "resources" / "configurations"

def test_conf():
    conf = ConfUtil(CONFIGURATIONS_LOCATION / "conf.yaml", CONFIGURATIONS_LOCATION / "log.yaml")
    expected = {
        "user_id":"ipbx",
        "thread_cnt":1,
        "db":{
           "host":"127.0.0.1",
           "port":1234,
           "database":"dbname",
           "user":"dbuser",
           "password":"dbpassword",
           "max_column_size":50000,
           "pool_size":1
        },
        "handler":{
           "start_time":1665634474000
        },
        "barcoder":{
           "faxes_dir":"/nfs/fax_files_root/"
        },
        "zbar":"",
        "consumer":{
           "bootstrap.servers":"127.0.0.1",
           "group.id":"barcode",
           "topics":[
              "fax_without_barcode"
           ],
           "auto.offset.reset":"earliest",
           "enable.auto.commit": True,
           "timeout":1.0,
           "schema_path":"fax.avsc",
           "is_confluent": True
        },
        "producer":{
           "bootstrap.servers":"127.0.0.1",
           "topic":"fax_with_barcode",
           "schema_path":"faxbarcode2.avsc"
        }
    }
    config = conf.conf
    assert  expected == config
