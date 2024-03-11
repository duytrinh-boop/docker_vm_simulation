# docker_vm_simulation
Project to spin up containers that are supposed to simulate Virtual Machines. These containers are quick to build, and quick to tear down.

This project does 2 things:
1. Spin up containers
2. creates an ansible inventory file of those containers

This will enable us to test ansible playbooks on containers, instead of in production.

## Prerequisites
```
# ensure group docker exists
sudo groupadd docker

#add current user to 'docker' group
sudo usermod -aG docker $USER

# refresh user groups
id -g
newgrp docker
```

## QUICKSTART
Spin up a predefined environment. 
Find predfined environments under 'environment/development/docker_vars'

E.g. ksat_old_prod.yml
```
# use predefined environment
docker_vars_filename="ksat_old_prod"

# run playbook 
ansible-playbook playbooks/1_deploy_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename.yml"
```

To verify
```
# Step 1: list all containers
docker container ls 

# Step 2: open a web browser and check that host can communicate directly
http://http-echo.test:5678

```


## SLOW START

