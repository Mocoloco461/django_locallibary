#!/bin/bash
apt install -y
apt install curl -y
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --token ${AGENT_TOKEN}" sh -

git clone -b conf-k3s-files git@gitlab.com:Mocoloco461/django_locallibary.git