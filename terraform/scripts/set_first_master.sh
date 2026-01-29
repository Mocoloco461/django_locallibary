#!/bin/bash
# apt install -y
apt install curl -y
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --token ${AGENT_TOKEN}" sh -
sleep 15
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

until kubectl get nodes; do
  echo "Waiting for K3s API server..."
  sleep 5
done

# set up argo cd:
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# pull the app config repo:
git clone https://github.com/Mocoloco461/locallibary-configs
sleep 5
kubectl apply -f locallibary-configs/argocd.yml


# git clone -b prodtest https://gitlab.com/Mocoloco461/django_locallibary.git
# kubectl apply -f /django_locallibary/k3s


