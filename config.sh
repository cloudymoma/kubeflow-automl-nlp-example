source env.sh
#enable services
gcloud services enable 'translate.googleapis.com'
gcloud services enable 'cloudfunctions.googleapis.com'
gcloud services enable 'language.googleapis.com'
gcloud services enable 'automl.googleapis.com'
gcloud services enable 'firestore.googleapis.com'

# create firestore
gcloud app create --region='us-central' || echo "App already created, skip"
gcloud alpha firestore databases create --region='us-central'

# create bucket
gsutil mb gs://$BUCKET_NAME/ || echo "bucket already exists, skip creation"

#copy kubeflow pipeline template to your bucket and make it public
gsutil cp kubeflow-automl/pipeline.yaml gs://$BUCKET_NAME/kubeflow/pipeline.yaml
gsutil acl ch -u AllUsers:R gs://$BUCKET_NAME/kubeflow/pipeline.yaml

#deploy all the functions, please go the folder and deploy it.
#in function-kubeflow/pipeline_deploy folder
gcloud functions deploy automl_deploy --entry-point pipeline_deploy --runtime python37 --trigger-http
#in function-kubeflow/inquire_run_status folder
gcloud functions deploy get_automl_status --entry-point run_status --runtime python37 --trigger-http