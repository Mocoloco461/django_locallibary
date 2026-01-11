#!/bin/bash
apt install
apt install curl -y
curl -sfL https://get.k3s.io | K3S_URL=https://${MASTER_A_IP}:6443 K3S_TOKEN=${AGENT_TOKEN} sh -

# set here a agent - need a vpc to get a static ip etc.
#server --cluster-init --token ${AGENT_TOKEN} --node-name k3s-master 