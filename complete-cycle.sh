#!/bin/bash -xe

#
# setup all necessary environmental variables
#

source setup.sh

#
# install api
#

pip install nuvla-api

#
# do the work
#

python srvs-creds.py

python create-data.py 
