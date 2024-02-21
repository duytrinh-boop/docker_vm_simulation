#
You can put splunk installation files here, to predistribute them to docker images.

For example having installation files in this folder:
splunk-9.0.2-17e00c557dc1-Linux-x86_64.tgz
splunkforwarder-9.0.2-17e00c557dc1-Linux-x86_64.tgz

Then add these two variables in the docker_vars file
splunk_package_uf: "splunkforwarder-9.0.2-17e00c557dc1-Linux-x86_64.tgz"
splunk_package_full: "splunk-9.0.2-17e00c557dc1-Linux-x86_64.tgz" 