#!/usr/bin/env python

import json

from os import listdir
from os.path import isfile, join

from nuvla.api import Api as nuvla_Api

nuvla_api = nuvla_Api('https://localhost', insecure=True)

nuvla_api.login_internal('super', 'supeRsupeR')

#
# set the swarm infrastructure-service
#

response = nuvla_api.search('infrastructure-service', filter="type='swarm'")
swarm_id = response.data['resources'][0]['id']

print("SWARM ID: %s" % swarm_id)

#
# collect all of the JSON files in gnss subdirectory
#

path="gnss"
json_files = [f for f in listdir(path) if isfile(join(path, f))]

#
# read and store entries
#

for f in json_files:
    with open(path + "/" + f) as json_file:

        # read JSON file
        data = json.load(json_file)

        # update service reference
        data['infrastructure-service'] = swarm_id

        # store the data-record
        response = nuvla_api.add('data-record', data)
        record_id = response.data['resource-id']
        print("data-record id: %s\n" % record_id)

