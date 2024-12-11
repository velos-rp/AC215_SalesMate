echo "Container is running!!!"

# Authenticate gcloud using service account
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
# Set GCP Project Details
gcloud config set project $GCP_PROJECT
# Configure GCR
gcloud auth configure-docker us-docker.pkg.dev -q


gcloud compute project-info add-metadata --project dulcet-doodad-443815-n3 --metadata enable-oslogin=TRUE


echo "Adding Metadata to GCP Project..."
gcloud compute project-info add-metadata --project dulcet-doodad-443815-n3 --metadata enable-oslogin=TRUE

echo "Deploying Docker Images with Ansible..."
ansible-playbook deploy-docker-images.yml -i inventory.yml

echo "Deploying Kubernetes Cluster with Ansible..."
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present

echo "Kubernetes Cluster deployed successfully!"