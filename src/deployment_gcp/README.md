Setup to run deployment container:

Make sure that you have the following files in a `secrets` subfolder at this directory:
    - `src/deployment_gcp/secrets/deployment-shared.json` - Deployment Permissions
    - `src/deployment_gcp/secrets/llm-service-account.json` - For finetuned LLMs
    - `src/deployment_gcp/secrets/gcp-service-shared.json` - General Access
    - `src/deployment_gcp/secrets/ssh-key-deployment` - SSH Key - these can be generated
    - `src/deployment_gcp/secrets/ssh-key-deployment.pub` - SSH Key


## Deployment Setup (Adapted from AC215 Class Tutorial)

#### Run `deployment` container
- cd into `deployment`
- Go into `docker-shell.sh` and change `GCP_PROJECT` to your project id
- Run `sh docker-shell.sh`
- make sure that GCP authentication works, run `gcloud auth list`



#### SSH Setup
##### Configuring OS Login for service account
Run this within the `deployment` container
```
gcloud compute project-info add-metadata --project dulcet-doodad-443815-n3 --metadata enable-oslogin=TRUE
```

##### Create SSH key for service account (If given and loaded already, don't run this)
```
cd /secrets
ssh-keygen -f ssh-key-deployment
cd /app
```


##### Providing public SSH keys to instances
```
gcloud compute os-login ssh-keys add --key-file=/secrets/ssh-key-deployment.pub
```
From the output of the above command keep note of the username and place it in the `ansible_user` variable in the `inventory.yml` file. Here is a snippet of the output
```
- accountId: ac215-project
    gid: '3906553998'
    homeDirectory: /home/sa_100110341521630214262
    name: users/deployment@ac215-project.iam.gserviceaccount.com/projects/ac215-project
    operatingSystemType: LINUX
    primary: true
    uid: '3906553998'
	...
    username: sa_100110341521630214262
```
The username is `sa_100110341521630214262`


## Deployment: Run Ansible Scripts

First make sure that the setup is complete and enter the shell of the deployment container (by running `sh docker-shell.sh`).

#### Build and Push Docker Containers to GCR (Google Artifact Registry)
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

#### Create Compute Instance (VM) Server in GCP
```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
```
Once the command runs successfully get the IP address of the compute instance from GCP Console and update the appserver>hosts in inventory.yml file

#### Provision Compute Instance in GCP
Install and setup all the required things for deployment.
```
ansible-playbook deploy-provision-instance.yml -i inventory.yml
```

#### Setup Docker Containers in the  Compute Instance
```
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```

#### Setup Webserver on the Compute Instance
```
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```
Once the command runs go to `http://<External IP>/`


## Deployment: Kubernetes

#### Build and Push Docker Containers to GCR (Google Artifact Registry), do this if not already done
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

#### Create & Deploy Cluster
```
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present
```