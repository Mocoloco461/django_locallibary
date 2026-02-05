# locallibary project

#### First step configs:

create s3 on aws for terraform remote state

> [!NOTE]
when create s3 use deiffult setting for, only give a name

on main.tf replace this:

```terrafrom
backend "s3" {
    bucket = "mybucket" #replace with your s3 name
    region = "us-east-1" #replace with region
  }
```

add that secret
```bash
export AWS_ACCESS_KEY_ID="ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="SECRET_KEY"
```

and run
```bash
terraform init
```

---


> the source is mirroring from [gitlab](https://gitlab.com/Mocoloco461/django_locallibary)

## For run the app:

to get secret_keu:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

# Leran goals

## Active:
- webdevelopment
- terraform
- k3s kubrn
- helm
- argo cd

## waiting:
- secret mangmant (infisical)

## external tools I uesed:
- kubeconform (good for get feeadback about helm files <countine>)


---

# Next Steps:

- [x] orgnize the project files
- [ ] rules for branch and for the ci/cd
- [ ] setup - [Ansible](https://spacelift.io/blog/ansible-devops) (Also read this blog)

- [ ] terraform real secrity setup

### On Prem
- [ ] proxmox etc...