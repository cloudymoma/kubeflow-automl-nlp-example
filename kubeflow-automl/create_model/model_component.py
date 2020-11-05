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


def automl_create_model_for_nlp(
  gcp_project_id: str,
  gcp_region: str,
  dataset_id: str,
  api_endpoint: str = None,
  model_display_name: str = None,
  model_prefix: str = 'catmodel',
) -> NamedTuple('Outputs', [('model_display_name', str), ('model_name', str), ('model_id', str)]):

  import subprocess
  import sys
  # we could build a base image that includes these libraries if we don't want to do
  # the dynamic installation when the step runs.
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'googleapis-common-protos==1.6.0', '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-cloud-automl==0.9.0', '--quiet', '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)

  import google
  import logging
  from google.api_core.client_options import ClientOptions
  from google.cloud import automl
  import time

  logging.getLogger().setLevel(logging.INFO)  # TODO: make level configurable
  # TODO: we could instead check for region 'eu' and use 'eu-automl.googleapis.com:443'endpoint
  # in that case, instead of requiring endpoint to be specified.
  if api_endpoint:
    client_options = ClientOptions(api_endpoint=api_endpoint)
    client = automl.AutoMlClient(client_options=client_options)
  else:
    client = automl.AutoMlClient()

  # A resource that represents Google Cloud Platform location.
  project_location = client.location_path(gcp_project_id, gcp_region)

  metadata = automl.types.TextClassificationModelMetadata()
  if not model_display_name:
    model_display_name = '{}_{}'.format(model_prefix, str(int(time.time())))
  model = automl.types.Model(
    display_name=model_display_name,
    dataset_id=dataset_id,
    text_classification_model_metadata=metadata,
  )
  # Create a model with the model metadata in the region.
  logging.info('Training model {}...'.format(model_display_name))
  response = client.create_model(project_location, model)

  logging.info("Training operation: {}".format(response.operation))
  logging.info("Training operation name: {}".format(response.operation.name))
  logging.info("Training in progress. This operation may take multiple hours to complete.")
  
  # block termination of the op until training is finished.
  result = response.result()
  logging.info("Training completed: {}".format(result))
  model_name = result.name
  model_id = model_name.rsplit('/', 1)[-1]
  print('model name: {}, model id: {}'.format(model_name, model_id))
  return (model_display_name, model_name, model_id)



if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(automl_create_model_for_nlp,
      output_component_file='model_component.yaml',
      base_image='python:3.7')
