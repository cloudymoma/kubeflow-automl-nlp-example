gcloud functions deploy get_automl_status --entry-point run_status --runtime python37 --trigger-http

gcloud functions deploy automl_deploy --entry-point pipeline_deploy --runtime python37 --trigger-http
