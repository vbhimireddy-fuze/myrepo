!/bin/bash

APPVERSION=$1
IMGTAG=$2

sed -i "s/APPVER/$APPVERSION/g" helm/faas-barcode/Chart.yaml
sed -i "s/IMGTAG/$IMGTAG/g" helm/faas-barcode/values.yaml

