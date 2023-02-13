
#https://github.com/8x8/barcode/Dockerfile
#This file should reside on the root of the github repo.
#You will need to clone https://github.com/8x8/barcode locally
#If Dockerfile is not merged yet please copy this file to the root of the repo

#Build it:
#1) remember to enable experimental features on your docker engine (OR remove --sqash in next step)  
#2) docker build --squash -t local/barcode:1 .   (local/barcode:1 was used as the example, we should propably call it with the actual registry name and commit hash as the version tag)
#3) push it to some repo somewhere : docker push
#Run it
#1) need to be on vpn (able to reach nfs 'nc -vz 100.127.160.8 2049' dns 'nc -vz 100.127.184.15 53' and kafka 'nc -v 100.127.160.107 9092')
#2) mount the nfs :  mount -o nolock -t nfs 100.127.160.8:/faxserver-docs /Users/afaryna/c1
#3) create directory and populate it with the customized env specyfic files :  conf.yaml and log.yaml
#4) docker run -it -v /Users/afaryna/arthur/work/k8s/bar1/Docker-configs/configs:/apps/configs -v /Users/afaryna/c1:/apps/ipbx/faxserver-docs --dns=100.127.184.15 --dns=100.127.184.14 -w /apps/barcode --user 1000:1000 local/barcode:1 python3 /apps/barcode/barcodemain.py
# -v attatches vulumes (nfs and configs)
# -w sets the working directory
# replace 'python3 /apps/barcode/barcodemain.py' with '/bin/bash' for troubleshooting

FROM docker.8x8.com:5000/8x8/hyperloop/centos7/python3.10:stable AS pythonbuild
#RUN yum update -y
RUN yum install -y zbar-devel
RUN yum install -y cmake python3-setuptools
RUN yum install -y gcc wget 
RUN yum install -y librdkafka1 librdkafka-devel

WORKDIR /package-build/
COPY . .
RUN pip3 install build
RUN pip3 install -r requirements.txt
RUN GV="$(cat APPVERSION)+$(cat GITSHORTHASH)" && sed -i "s/99.99.99999+fffffff/$GV/g" src/barcode_service/version.py
RUN pip3 wheel -w ./build_dir .

FROM docker.8x8.com:5000/8x8/hyperloop/centos7/python3.10:stable as release
#RUN yum -y update

WORKDIR /package-build/
RUN yum install -y librdkafka1 zbar-devel
COPY --from=pythonbuild /package-build/build_dir/* /package-build/
RUN pip3 install /package-build/*

RUN groupadd -g 1001 ipbx
RUN useradd -u 1001 -g 1001 -M ipbx

RUN mkdir -p /apps/ipbx/faxserver-docs

# seams like those need to be in the root folder
RUN ln -s /root/.pyenv/versions/3.10.9/lib/python3.10/site-packages/barcode_service /apps/barcode
RUN chown ipbx:ipbx /apps

# tar the directory if interested in artifacts (upload/copy those wherever needed)
RUN rm -rf /package-build/*
