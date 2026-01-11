#!/bin/bash
apt install -y
apt install curl -y
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --token ${AGENT_TOKEN}" sh -
sleep 15
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
git clone -b conf-k3s-files https://gitlab.com/Mocoloco461/django_locallibary.git
kubectl apply -f django_locallibary/k3s