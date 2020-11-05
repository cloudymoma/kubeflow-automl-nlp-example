import kfp
import kfp_server_api
import time
import string
import json
import google.auth
import google.auth.transport.requests
import logging

def pipeline_deploy(request):
    request_json = request.get_json()
    kfp_id = request_json['kfp']
    pipeline_file_url = request_json.get('template_url' , 'https://storage.googleapis.com/your_bucket_name/pipeline.yaml')
    dataset_display_name = request_json['dataset_display_name']
    dataset_path = request_json['dataset_path']

    creds, projects = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    client = kfp.Client(host=kfp_id, existing_token=creds.token)

    #create pipeline using url
    suffix = request_json['name']
    pipeline_name = 'nlp-pipeline-'+ suffix
    run_name = 'nlp-run-' + suffix
    thread = client.pipelines.list_pipelines(async_req=True)
    result = thread.get()
    for pipeline in result.pipelines:
        if pipeline.name == pipeline_name:
            return 'Please specify a new name.'
    api_url = kfp_server_api.models.ApiUrl(pipeline_file_url)
    api_pipeline = kfp_server_api.models.ApiPipeline(
            name=pipeline_name,
            url=api_url)
    thread = client.pipelines.create_pipeline(api_pipeline, async_req=True)
    result = thread.get()
    default_version_id = result.default_version.id # pipeline id
    logging.info('pipeline id: {}'.format(default_version_id))
    
    # Create an experiment.
    experiment_name = 'nlp-experiment-' + suffix
    experiment = client.experiments.create_experiment(body={'name' : experiment_name})
    experiment_id = experiment.id
    logging.info('experiment id: {}'.format(experiment_id))
    
    # Create a run
    resource_references = []
    key = kfp_server_api.models.ApiResourceKey(id=experiment_id, type=kfp_server_api.models.ApiResourceType.EXPERIMENT)
    reference = kfp_server_api.models.ApiResourceReference(key=key, relationship=kfp_server_api.models.ApiRelationship.OWNER)
    resource_references.append(reference)
    
    parameters = []
    parameter = kfp_server_api.ApiParameter(name='gcp_project_id', value=projects)
    parameters.append(parameter)
    parameter = kfp_server_api.ApiParameter(name='gcp_region', value='us-central1')
    parameters.append(parameter)
    parameter = kfp_server_api.ApiParameter(name='dataset_display_name', value=dataset_display_name)
    parameters.append(parameter)
    parameter = kfp_server_api.ApiParameter(name='api_endpoint', value='')
    parameters.append(parameter) 
    parameter = kfp_server_api.ApiParameter(name='gcs_path', value=dataset_path)
    parameters.append(parameter) 
    parameter = kfp_server_api.ApiParameter(name='model_prefix', value='nlpmodel')
    parameters.append(parameter)     
    pipeline_spec = kfp_server_api.ApiPipelineSpec(parameters=parameters, pipeline_id=default_version_id)

    run = client.runs.create_run(body={'name':run_name, 'resource_references': resource_references, 'pipeline_spec': pipeline_spec})
    run_id = run.run.id
    logging.info('run id: {}'.format(run_id))

    return run_id