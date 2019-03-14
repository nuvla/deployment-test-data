
import os

#
# Creates the services and credenials needed for the ESA Swarm/Minio
# infrastructure for GNSS.
#

from nuvla.api import Api as nuvla_Api

nuvla_api = nuvla_Api(os.environ['NUVLA_ENDPOINT'], insecure=True)

nuvla_api.login_internal('super', 'supeRsupeR')

#
# Create infrastructure-service-group to hold the services running at
# ESA.
#

group = {"name": "GNSS Big Data",
         "description": "Services running at ESA for the GNSS Big Data project",
         "documentation": "https://gssc.esa.int/"}

isg_response = nuvla_api.add('infrastructure-service-group', group)
isg_id = isg_response.data['resource-id']
print("ISG id: %s\n" % isg_id)


#
# Swarm service
#

swarm_tpl = {"template": { "href": "infrastructure-service-template/generic",
                           "parent": isg_id,
                           "name": "GNSS Swarm",
                           "description": "Docker Swarm cluster at ESA for GNSS",
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
                           "name": "GNSS Minio (S3)",
                           "description": "Minio (S3) service at ESA for GNSS",
                           "type": "s3",
                           "endpoint": os.environ['MINIO_ENDPOINT'],
                           "state": "STARTED"}}

minio_srv_response = nuvla_api.add('infrastructure-service', minio_tpl)
minio_id = minio_srv_response.data['resource-id']
print("Minio service id: %s\n" % minio_id)

#
# Swarm credential
#

swarm_cred_tpl = {"name": "GNSS Swarm Credential",
                  "description": "Certificate, Key, and CA for GNSS Swarm",
                  "template": {"href": "credential-template/infrastructure-service-swarm",
                               "infrastructure-services": [swarm_id],
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
                  "description": "Credentials for Minio S3",
                  "template": {"href": "credential-template/infrastructure-service-minio",
                               "infrastructure-services": [minio_id],
                               "access-key": os.environ['MINIO_ACCESS_KEY'],
                               "secret-key": os.environ['MINIO_SECRET_KEY']}}

minio_cred_response = nuvla_api.add('credential', minio_cred_tpl)
minio_cred_id = minio_cred_response.data['resource-id']
print("Minio credential id: %s\n" % minio_cred_id)

#
# Add dataset definitions.
#

data_set = {"name": "GREAT (CLK)",
            "description": "GREAT (CLK) data at ESA",
            "module-filter": "data-accept-content-types='application/x-clk'",
            "data-record-filter": "resource:type='DATA' and gnss:mission='great' and data:contentType='application/x-clk'"}

data_set_response = nuvla_api.add('data-set', data_set)
data_set_id = data_set_response.data['resource-id']
print("data-set id: %s\n" % data_set_id)


data_set = {"name": "GOCE (HDR)",
            "description": "GOCE (HDR) data at ESA",
            "module-filter": "data-accept-content-types='application/x-hdr'",
            "data-record-filter": "resource:type='DATA' and gnss:mission='goce' and data:contentType='application/x-hdr'"}

data_set_response = nuvla_api.add('data-set', data_set)
data_set_id = data_set_response.data['resource-id']
print("data-set id: %s\n" % data_set_id)


data_set = {"name": "Random (TXT)",
            "description": "Random text data at ESA",
            "module-filter": "data-accept-content-types='text/plain'",
            "data-record-filter": "resource:type='DATA' and gnss:mission='random' and data:contentType='text/plain'"}

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


prefix_data = {"name": "Data Key Prefix",
               "description": "key prefix for general data attributes",
               "prefix": "data",
               "uri": "https://gssc.esa.int/nuvla/prefix/data"}

prefix_data_response = nuvla_api.add('data-record-key-prefix', prefix_data)
prefix_data_id = prefix_data_response.data['resource-id']
print("prefix data id: %s\n" % prefix_data_id)


prefix_resource = {"name": "Resource Key Prefix",
                   "description": "key prefix for general resource attributes",
                   "prefix": "resource",
                   "uri": "https://sixsq.com/nuvla/prefix/resource"}

prefix_resource_response = nuvla_api.add('data-record-key-prefix', prefix_resource)
prefix_resource_id = prefix_resource_response.data['resource-id']
print("prefix resource id: %s\n" % prefix_resource_id)


#
# Add component for GNSS Python application
#

gnss_comp = {"author": "esa",
             "commit": "initial commit",
             "architecture": "x86",
             "image": "sixsq/gssc-jupyter:latest",
             "output-parameters": [{"name": "jupyter-token", "description": "jupyter authentication token"}],
             "ports": ["tcp::8888"],
             "urls": [["jupyter", "http://${hostname}:${tcp.8888}/?token=${jupyter-token}"]],
             }

gnss_module = {"name": "GNSS Jupyter Notebook",
               "description": "Jupyter notebook application integrated with Nuvla data management",
               "logo-url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/ESA_logo.svg/320px-ESA_logo.svg.png",
               "type": "COMPONENT",
               "path": "gssc-jupyter",
               "parent-path": "",
               "data-accept-content-types": ["application/x-hdr", "application/x-clk", "text/plain"],
               "content": gnss_comp}

gnss_module_response = nuvla_api.add('module', gnss_module)
gnss_module_id = gnss_module_response.data['resource-id']
print("module id: %s\n" % gnss_module_id)


#
# create deployment
#

#deployment = {"module": {"href": gnss_module_id},
#              "infrastructure-service-id": swarm_id,
#              "credential-id": swarm_cred_id}

#deployment_response = nuvla_api.add('deployment', deployment)
#deployment_id = deployment_response.data['resource-id']
#print("deployment id: %s\n" % deployment_id)

