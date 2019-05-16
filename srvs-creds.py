import os

#
# Creates the services and credenials needed for the ESA Swarm/Minio
# infrastructure for GNSS.
#
# The following environmenal variables can/must be defined:
#
# NUVLA_ENDPOINT: endpoint of Nuvla server, defaults to localhost
#
# SWARM_ENDPOINT: endpoint of Docker Swarm cluster
# SWARM_CERT: Swarm client public key
# SWARM_KEY: Swarm client private key
#
# MINIO_ENDPOINT: endpoint of Minio (S3) service
# MINIO_ACCESS_KEY: access key for Minio service
# MINIO_SECRET_KEY: secret key for Minio service
#

from nuvla.api import Api as nuvla_Api

nuvla_api = nuvla_Api(os.environ['NUVLA_ENDPOINT'], insecure=True)

nuvla_api.login_password('super', 'supeR8-supeR8')

#
# Create infrastructure-service-group to hold the test services..
#

group = {"name": "Group of Test Services",
         "description": "Test services used to validate the Nuvla deployment",
         "documentation": "https://nuv.la/module/apps/Containers/docker-swarm/swarm"}

isg_response = nuvla_api.add('infrastructure-service-group', group)
isg_id = isg_response.data['resource-id']
print("ISG id: %s\n" % isg_id)


#
# Swarm service
#

swarm_tpl = {"template": { "href": "infrastructure-service-template/generic",
                           "parent": isg_id,
                           "name": "Test Swarm",
                           "description": "Docker Swarm cluster for Nuvla validation",
                           "type": "swarm",
                           "endpoint": os.environ['SWARM_ENDPOINT'],
                           "state": "STARTED"}}

swarm_srv_response = nuvla_api.add('infrastructure-service', swarm_tpl)
swarm_id = swarm_srv_response.data['resource-id']
print("Swarm service id: %s\n" % swarm_id)

#
# Minio (S3) service
#

minio_tpl = {"template": { "href": "infrastructure-service-template/generic",
                           "parent": isg_id,
                           "name": "Test Minio (S3)",
                           "description": "Minio (S3) service for Nuvla validation",
                           "type": "s3",
                           "endpoint": os.environ['MINIO_ENDPOINT'],
                           "state": "STARTED"}}

minio_srv_response = nuvla_api.add('infrastructure-service', minio_tpl)
minio_id = minio_srv_response.data['resource-id']
print("Minio service id: %s\n" % minio_id)

#
# Swarm credential
#

swarm_cred_tpl = {"name": "Docker Swarm Credential",
                  "description": "Certificate, Key, and CA for test Docker Swarm cluster",
                  "template": {"href": "credential-template/infrastructure-service-swarm",
                               "parent": swarm_id,
                               "ca": "my-ca",
                               "cert": os.environ['SWARM_CERT'],
                               "key": os.environ['SWARM_KEY']}}

swarm_cred_response = nuvla_api.add('credential', swarm_cred_tpl)
swarm_cred_id = swarm_cred_response.data['resource-id']
print("Swarm credential id: %s\n" % swarm_cred_id)

#
# Credential for Minio (S3)
#

minio_cred_tpl = {"name": "Minio S3 Credential",
                  "description": "Credentials for Minio S3 test service",
                  "template": {"href": "credential-template/infrastructure-service-minio",
                               "parent": minio_id,
                               "access-key": os.environ['MINIO_ACCESS_KEY'],
                               "secret-key": os.environ['MINIO_SECRET_KEY']}}

minio_cred_response = nuvla_api.add('credential', minio_cred_tpl)
minio_cred_id = minio_cred_response.data['resource-id']
print("Minio credential id: %s\n" % minio_cred_id)

#
# Add dataset definitions.
#

data_set = {"name": "Random Text",
            "description": "Collection of files containing random text",
            "module-filter": "data-accept-content-types='text/plain'",
            "data-record-filter": "gnss:mission='random' and content-type='text/plain'"}

data_set_response = nuvla_api.add('data-set', data_set)
data_set_id = data_set_response.data['resource-id']
print("data-set id: %s\n" % data_set_id)

data_set = {"name": "Random Binary",
            "description": "Collection of files containing random binary data",
            "module-filter": "data-accept-content-types='application/octet-stream'",
            "data-record-filter": "gnss:mission='random' and content-type='application/octet-stream'"}

data_set_response = nuvla_api.add('data-set', data_set)
data_set_id = data_set_response.data['resource-id']
print("data-set id: %s\n" % data_set_id)

#
# setup prefixes for data-record resources
#

prefix_gnss = {"name": "GNSS Key Prefix",
               "description": "key prefix for GNSS Big Data attributes",
               "prefix": "gnss",
               "uri": "https://gssc.esa.int/nuvla/prefix/gnss"}

prefix_gnss_response = nuvla_api.add('data-record-key-prefix', prefix_gnss)
prefix_gnss_id = prefix_gnss_response.data['resource-id']
print("prefix gnss id: %s\n" % prefix_gnss_id)


#
# Add component for GNSS Python application
#

gnss_comp = {"author": "esa",
             "commit": "initial commit",
             "architecture": "x86",
             "image": {"repository": "sixsq",
                       "image-name": "gssc-jupyter",
                       "tag": "latest"},
             "output-parameters": [{"name": "jupyter-token", "description": "jupyter authentication token"}],
             "ports": [{"protocol": "tcp",
                        "target-port": 8888}],
             "urls": [["jupyter", "http://${hostname}:${tcp.8888}/?token=${jupyter-token}"]],
             }

gnss_module = {"name": "GNSS Jupyter Notebook",
               "description": "Jupyter notebook application integrated with Nuvla data management",
               "logo-url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/ESA_logo.svg/320px-ESA_logo.svg.png",
               "type": "COMPONENT",
               "path": "gssc-jupyter",
               "parent-path": "",
               "data-accept-content-types": ["text/plain", "application/octet-stream"],
               "content": gnss_comp}

gnss_module_response = nuvla_api.add('module', gnss_module)
gnss_module_id = gnss_module_response.data['resource-id']
print("module id: %s\n" % gnss_module_id)

