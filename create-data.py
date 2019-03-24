#!/usr/bin/env python

from datetime import datetime
import hashlib
import json
import random
import requests
import string

#import logging
#logging.basicConfig(level=logging.DEBUG)


from os import listdir, environ
from os.path import isfile, join

from nuvla.api import Api as nuvla_Api

nuvla_api = nuvla_Api(environ['NUVLA_ENDPOINT'], insecure=True)

nuvla_api.login_internal('super', 'supeR8-supeR8')

bucket = 'new-bucket-for-tests'
object = 'new-object-for-tests'

#
# get the s3 infrastructure-service
#

response = nuvla_api.search('infrastructure-service', filter="type='s3'")
s3_service = response.data['resources'][0]
s3_id = s3_service['id']
s3_endpoint = s3_service['endpoint']

print('S3 ID: %s' % s3_id)
print('S3 ENDPOINT: %s' % s3_endpoint)

#
# get the credential for s3
#

response = nuvla_api.search('credential', filter="infrastructure-services='%s'" % s3_id)
s3_credential = response.data['resources'][0]
s3_credential_id = s3_credential['id']

print('CREDENTIAL ID: %s' % s3_credential_id)
print(s3_credential)

#
# get the swarm infrastructure-service
#

response = nuvla_api.search('infrastructure-service', filter="type='swarm'")
swarm_service = response.data['resources'][0]
swarm_id = swarm_service['id']
swarm_endpoint = swarm_service['endpoint']

print('SWARM ID: %s' % swarm_id)
print('SWARM ENDPOINT: %s' % swarm_endpoint)

#
# function to create a file with random contents
#

def random_file(size):
    chars = ''.join([random.choice(string.lowercase) for i in range(size)])
    filename = "%s.txt" % hashlib.sha1(chars).hexdigest()
    with open(filename, 'w') as f:
        f.write(chars)
    return filename

file_size = 1024
filename = random_file(file_size)

#
# create a data-object
#

data = {"name": "data-object-1",
        "description": "data object 1 with random data",
        "template": {
            "credential": s3_credential_id,
            "type": "generic",
            "resource-type": "data-object-template",
            "content-type": "text/plain",
            "object": object,
            "bucket": bucket,
            "href": "data-object-template/generic"
        }
}

response = nuvla_api.add('data-object', data)
data_object_id = response.data['resource-id']
print("data-object id: %s\n" % data_object_id)

#
# upload the file contents
#

print("UPLOAD ACTION")
data_object = nuvla_api.get(data_object_id)
response = nuvla_api.operation(data_object, "upload")
upload_url = response.data['uri']
print("upload_url: %s\n" % upload_url)

body = open(filename, 'rb').read()
headers = {"content-type": "text/plain"}
response = requests.put(upload_url, data=body, headers=headers)
print(response)

#
# mark the object as ready
#

print("READY ACTION")
data_object = nuvla_api.get(data_object_id)
response = nuvla_api.operation(data_object, "ready")
print(response)

#
# download the file
#

print("DOWNLOAD ACTION")
data_object = nuvla_api.get(data_object_id)
response = nuvla_api.operation(data_object, "download")
download_url = response.data['uri']
print("download_url: %s\n" % download_url)

response = requests.get(download_url, headers=headers)
from pprint import pprint
pprint(response)
print(response.text)

#
# create data-record
#

current_date = '%sZ' % datetime.utcnow().replace(microsecond=0).isoformat()

# FIXME: This should point to S3 service rather than SWARM.

data = {
    "infrastructure-service": swarm_id,
    
    "name": "data-object-1",
    "description": "data-object-1 description",
    
    "resource:type": "DATA",
    "resource:protocol": "NFS",
    "resource:object": data_object_id,
    
    "data:bucket": bucket,
    "data:object": object,
    "data:contentType": "text/plain",
    "data:timestamp": current_date,

    "data:bytes": file_size,
    
    "data:nfsDevice": "/nfs-root",
    "data:nfsIP": environ['INFRA_IP'],
    
    "data:protocols": [
        "tcp+nfs"
    ],

    "gnss:mission": "random",
    
    "acl": {
        "owner": {
            "type": "ROLE",
            "principal": "ADMIN"
        },
        "rules": [
            {
                "right": "VIEW",
                "type": "ROLE",
                "principal": "USER"
            },
            {
                "type": "ROLE",
                "principal": "ADMIN",
                "right": "ALL"
            }
        ]
    }    
}

response = nuvla_api.add('data-record', data)
data_record_id = response.data['resource-id']
print("data-record id: %s\n" % data_record_id)


#
# delete the data-object
#

#print("DELETE")
#response = nuvla_api.delete(data_object_id)
#print(response)

