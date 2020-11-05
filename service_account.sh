#!/bin/bash
source env.sh

# exit if any subcommand has error
set -euxo pipefail

#create service account and config it
ADMIN_NAME='******'

gcloud iam service-accounts create $ADMIN_NAME
gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:$ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role "roles/owner"
gcloud iam service-accounts keys create ~/$ADMIN_NAME.json --iam-account $ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com


export GOOGLE_APPLICATION_CREDENTIALS=key-file
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$ADMIN_NAME@appspot.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$ADMIN_NAME --role='roles/automl.editor'
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role=roles/logging.logWriter
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role=roles/monitoring.metricWriter
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role=roles/monitoring.viewer
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$ADMIN_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role=roles/storage.objectViewer
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role, bindings.members)" --filter="bindings.role:roles/container.admin OR bindings.role:roles/viewer"
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role, bindings.members)" --filter="bindings.role:roles/iam.serviceAccountAdmin"
