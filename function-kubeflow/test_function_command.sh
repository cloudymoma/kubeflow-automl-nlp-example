
#automl_deploy function request:
{
    "kfp":"abcdes****-dot-us-central2.pipelines.googleusercontent.com", #AI platform pipeline instance client
    "template_url": "https://storage.googleapis.com/your_bucket_name/kubeflow/pipeline.yaml", # use your pipeline url
    "dataset_display_name": "abc_123", #automl dataset name
    "dataset_path":"gs://your_bucket_name/data/automl/text_training.csv", #dataset file gcs uri
    "name": "abc_123" #name suffix for kubeflow job
}
#After run, the runid will be in the response.

#get_automl_status function request:
check kubeflow status:
{
    "kfp": "abcdes****-dot-us-central2.pipelines.googleusercontent.com",
    "runid": "2b245945-e504-4403-a24f-ac851ee6c481"
}

