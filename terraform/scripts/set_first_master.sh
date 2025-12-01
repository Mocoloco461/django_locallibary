#!/bin/bash
apt install -y
apt install curl -y
curl -sfl https://get.k3s.io | sh -
server --cluster-init --token ${MASTER_TOKEN} --agent-token ${AGENT_TOKEN} --node-name k3s-master


# dbugging:

echo "master_token: ${MASTER_TOKEN} | agent_token: ${AGENT_TOKEN}" > test.txt