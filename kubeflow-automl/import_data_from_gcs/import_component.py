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

def automl_import_data_for_nlp(
  # dataset_path,
  gcs_path: str,
  gcp_project_id: str,
  gcp_region: str,
  dataset_id: str,
  api_endpoint: str = None,
) -> NamedTuple('Outputs', [('dataset_id', str)]):
  import sys
  import subprocess
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'googleapis-common-protos==1.6.0',
      '--no-warn-script-location'], env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-cloud-automl==0.9.0', '--quiet',
      '--no-warn-script-location'], env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)

  import google
  import logging
  from google.api_core.client_options import ClientOptions
  from google.cloud import automl

  logging.getLogger().setLevel(logging.INFO)  # TODO: make level configurable

  if api_endpoint:
    client_options = ClientOptions(api_endpoint=api_endpoint)
    client = automl.AutoMlClient(client_options=client_options)
  else:
    client = automl.AutoMlClient()
  
  dataset_full_id = client.dataset_path(gcp_project_id, gcp_region, dataset_id)
  current_dataset = client.get_dataset(dataset_full_id)
  if current_dataset.example_count > 0:
    logging.info("Dataset has data already.")
    logging.info("Dataset example count: {}".format(current_dataset.example_count))

  # Get the multiple Google Cloud Storage URIs.
  input_uris = gcs_path.split(",")
  gcs_source = automl.types.GcsSource(input_uris=input_uris)
  input_config = automl.types.InputConfig(gcs_source=gcs_source)
  #dataset_full_id = client.dataset_path(gcp_project_id, gcp_region, dataset_id)

  response = client.import_data(dataset_full_id, input_config)

  logging.info("Processing import... This can take a while.")
  # synchronous check of operation status.
  logging.info("Data imported. {}".format(response.result()))
  logging.info("Response metadata: {}".format(response.metadata))
  logging.info("Operation name: {}".format(response.operation.name))

  logging.info("Dataset id: {}".format(dataset_id))
  return [dataset_id]


if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(automl_import_data_for_nlp,
      output_component_file='import_component.yaml', base_image='python:3.7')
