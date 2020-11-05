PROJECT_ID='******'

# bucket to store intermediate data
BUCKET_NAME=$PROJECT_ID
GCP_REGION='us-central1'

echo "project id: $PROJECT_ID  bucket: $BUCKET_NAME region: $GCP_REGION"

#set project name in cli
gcloud config set project $PROJECT_ID