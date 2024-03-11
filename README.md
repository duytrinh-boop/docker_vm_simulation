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
Find predefined environments under 'environment/development/docker_vars'

E.g. ksat_old_prod.yml
```
# use predefined environment
docker_vars_filename="ksat_old_prod.yml"

# run playbook 
ansible-playbook playbooks/1_deploy_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename"

# On first time run, the playbook may fail. In that case, just run it again

```

**To verify**
```
# Step 1: list all containers
docker container ls 

# Step 2: open a web browser and check that host can communicate directly
http://http-echo.test:5678

# Step 3: run ansible test on the new inventory
ansible all -m ping -i environments/development/inventory_$docker_vars_filename.ini

```

This means we can take the inventory file and use it.


**To destroy the containers:**
```
# remember to replace with the correct 'docker_vars_filename'
docker_vars_filename="ksat_old_prod.yml"
ansible-playbook playbooks/2_teardown_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename"
```

**spin up the containers again:**
```
# use predefined environment
docker_vars_filename="ksat_old_prod"

# run playbook 
ansible-playbook playbooks/1_deploy_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename.yml"
```




## SLOW START

