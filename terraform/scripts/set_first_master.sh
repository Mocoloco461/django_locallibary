#!/bin/bash
apt install
apt install curl -y
curl -sfl https://get.k3s.io | sh -
server --cluster-init --token ${AGENT_TOKEN} --node-name k3s-master