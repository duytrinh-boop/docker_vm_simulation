docker_vars_filename="deploymentlab.yml"
sudo docker container ls -af label=docker_compose_file=compose_file_$docker_vars_filename

ansible-playbook playbooks/1_deploy_linux_containers.yml --extra-var "docker_vars_file=$docker_vars_filename"

inventory="environments/development/inventory_$docker_vars_filename.ini"

# ansible-playbook -i $inventory playbooks/3_deploy_eventgen.yml --extra-var "docker_vars_file=$docker_vars_filename.yml"

# docker restart policy: keep containers running
docker update --restart unless-stopped $(docker container ls -af label=docker_compose_file=compose_file_$docker_vars_filename -q)



#ansible-playbook  playbooks/single-task.yml --vault-password-file=.vault_pass --extra-var "deployment_task=adhoc_tintin_populate_shc_group.yml"     

# basic install splunk
# ansible-playbook -i $inventory  playbooks/splunk_install_or_upgrade.yml --vault-password-file=.vault_pass
# ansible-playbook -i $inventory playbooks/patch_servers.yml --vault-password-file=.vault_pass 


### tear down commands
#ansible-playbook playbooks/2_teardown_linux_containers.yml --extra-var "docker_vars_file=deploymentlab.yml"
