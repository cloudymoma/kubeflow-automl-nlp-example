# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import NamedTuple

def automl_deploy_nlp_model(
  gcp_project_id: str,
  gcp_region: str,
  model_display_name: str,
  model_id,
  api_endpoint: str = None,
) -> NamedTuple('Outputs', [('model_display_name', str), ('model_id', str), ('status', str)]):
  import subprocess
  import sys
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'googleapis-common-protos==1.6.0', '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-cloud-automl==0.9.0', '--quiet', '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)

  import google
  import logging
  from google.api_core.client_options import ClientOptions
  from google.api_core import exceptions
  from google.cloud import  automl
  from google.cloud.automl import enums

  logging.getLogger().setLevel(logging.INFO)  # TODO: make level configurable

  if api_endpoint:
    client_options = ClientOptions(api_endpoint=api_endpoint)
    client = automl.AutoMlClient(client_options=client_options)
  else:
    client = automl.AutoMlClient()

  try:
      logging.info('Deploying model {}'.format(model_display_name))
      model_full_id = client.model_path(gcp_project_id, gcp_region, model_id)
      response = client.deploy_model(model_full_id)
      # synchronous wait
      logging.info("Model deployed. {}".format(response.result()))
      status = 'deployed'
  except exceptions.NotFound as e:
    logging.warning(e)
    status = 'not_found'
  except Exception as e:
    logging.warning(e)
    status = 'undeployed'
  logging.info('Model status: {}'.format(status))

  
  return (model_display_name, model_id, status)



if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(
      automl_deploy_nlp_model, output_component_file='deploy_component.yaml',
      base_image='python:3.7')
