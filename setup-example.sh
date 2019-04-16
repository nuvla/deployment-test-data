#!/bin/bash -xe

export INFRA_IP='0.0.0.0'

export NUVLA_ENDPOINT='https://localhost'

export MINIO_ENDPOINT="http://${INFRA_IP}:9000"
export MINIO_ACCESS_KEY='...'
export MINIO_SECRET_KEY='...'

export SWARM_ENDPOINT="https://${INFRA_IP}:2376"
export SWARM_CERT='...'
export SWARM_KEY='...'
