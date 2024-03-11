docker_vars_filename="ksat_old_prod.yml"
sudo docker container ls -af label=docker_compose_file=compose_file_$docker_vars_filename

ansible-playbook playbooks/1_deploy_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename"

inventory="environments/development/inventory_$docker_vars_filename.ini"

# docker restart policy: keep containers running
docker update --restart unless-stopped $(docker container ls -af label=docker_compose_file=compose_file_$docker_vars_filename -q)


### tear down commands
#ansible-playbook playbooks/2_teardown_linux_containers.yml --extra-var "docker_vars_file=ksat_old_prod.yml"
