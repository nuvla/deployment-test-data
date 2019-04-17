#!/usr/bin/env python

from datetime import datetime
import hashlib
import random
import requests
import string

#import logging
#logging.basicConfig(level=logging.DEBUG)


from os import listdir, environ, remove

from nuvla.api import Api as nuvla_Api

nuvla_api = nuvla_Api(environ['NUVLA_ENDPOINT'], insecure=True)

nuvla_api.login_password('super', 'supeR8-supeR8')

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
# (text is lowercase characters, "binary" is uppercase characters)
#

def random_text_file(size):
    chars = ''.join([random.choice(string.lowercase) for i in range(size)])
    filename = "%s.txt" % hashlib.sha1(chars).hexdigest()
    with open(filename, 'w') as f:
        f.write(chars)
    return filename

def random_binary_file(size):
    chars = ''.join([random.choice(string.uppercase) for i in range(size)])
    filename = "%s.txt" % hashlib.sha1(chars).hexdigest()
    with open(filename, 'w') as f:
        f.write(chars)
    return filename

#
# Create a timestamp to associate with the data
#


timestamp = '%s.00Z' % datetime.utcnow().replace(microsecond=0).isoformat()

location = [6.143158, 46.204391, 373.0]

#
# create a data-object
#

data = {"name": "data-object-1",
        "description": "data object 1 with random data",
        "template": {
            "href": "data-object-template/generic",
            "type": "generic",
            "resource-type": "data-object-template",
            "credential": s3_credential_id,
            "timestamp": timestamp,
            "location": location,
            "content-type": "text/plain",
            "bucket": bucket,
            "object": object
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

file_size = random.randint(1, 8096)
filename = random_text_file(file_size)

body = open(filename, 'rb').read()
headers = {"content-type": "text/plain"}
response = requests.put(upload_url, data=body, headers=headers)
print(response)

remove(filename)

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

# FIXME: This should point to S3 service rather than SWARM.

data = {
    "infrastructure-service": swarm_id,
    
    "name": "data-object-1",
    "description": "data-object-1 description",

    "content-type": "text/plain",
    "timestamp": timestamp,
    "location": location,

    "bytes": file_size,

    "mount": {"mount-type": "volume",
              "target": 'mnt/%s' % bucket,
              "volume-options": {"type": "nfs",
                                 "o": 'addr=%s' % environ['INFRA_IP'],
                                 "device": ':/nfs-root/%s' % bucket}},
              
    "gnss:mission": "random",
    
    "acl": {
        "owners": ["group/nuvla-admin"],
        "view-acl": ["group/nuvla-user"]
    }
}

response = nuvla_api.add('data-record', data)
data_record_id = response.data['resource-id']
print("data-record id: %s\n" % data_record_id)

