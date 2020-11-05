import kfp
import kfp_server_api
import time
import string
import json
import google.auth
import google.auth.transport.requests

def run_finished(run_status: string) -> bool:
    return run_status in {'Succeeded', 'Failed', 'Error', 'Skipped', 'Terminated'}

def run_succeeded(run_status: string) -> bool:
    return run_status in {'Succeeded'}

def get_node_status(run_obj):
    node_status = []
    #overall_status = []
    manifest = json.loads(run_obj.pipeline_runtime.workflow_manifest)
    for item in manifest['status']['nodes']:
        if '.' in manifest['status']['nodes'][item]['name']:
            node_status.append({
                'name': manifest['status']['nodes'][item]['name'].split(".")[-1], 
                'phase': manifest['status']['nodes'][item]['phase'], 
                'startTime': manifest['status']['nodes'][item]['startedAt']
            })
        else:
            overal_status= manifest['status']['nodes'][item]['phase']

    node_status.sort(key = lambda x : x['startTime'])
    print('overal_status: {}'.format(overal_status))
    for item in node_status:
        print('{}: {}'.format(item['name'],item['phase']))
    return overal_status, node_status

def get_metrics(run_obj):
    metrics = []
    print('Final metrics:')
    for i in range(len(run_obj.run.metrics)):
        print('{}: {}'.format(run_obj.run.metrics[i].name, run_obj.run.metrics[i].number_value))
        metrics.append({'name': run_obj.run.metrics[i].name, 'value': run_obj.run.metrics[i].number_value})
    return metrics

def get_model_id(run_obj):
    manifest = json.loads(run_obj.pipeline_runtime.workflow_manifest)
    for item in manifest['status']['nodes']:
        if 'create-model' in manifest['status']['nodes'][item]['name']:
            for entity in manifest['status']['nodes'][item]['outputs']['parameters']:
                if 'model_id' in entity['name']:
                    print('model id: {}'.format(entity['value']))
                    model_id = entity['value']
                    break
    return model_id

def run_status(request):
    request_json = request.get_json()

    creds, projects = google.auth.default()

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    kfp_id = request_json['kfp']
    client = kfp.Client(host=kfp_id, existing_token=creds.token)
    run_id = request_json['runid']
    
    run_current = client.runs.get_run(run_id)

    response_body = {}
    if run_succeeded(run_current.run.status):
        overal_status, node_status = get_node_status(run_current)
        response_body['status'] = overal_status
        response_body['nodes'] = node_status
        response_body['metrics'] = get_metrics(run_current)
        response_body['model_id'] = get_model_id(run_current)

    else:   
        overal_status, node_status = get_node_status(run_current)
        response_body['status'] = overal_status
        response_body['nodes'] = node_status
        response_body['metrics'] = ''
        response_body['model_id'] = ''
    response_json = json.dumps(response_body)
    return response_json