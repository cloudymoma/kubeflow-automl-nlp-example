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


def automl_create_dataset_for_nlp(
  gcp_project_id: str,
  gcp_region: str,
  dataset_display_name: str,
  api_endpoint: str = None,
) -> NamedTuple('Outputs', [('dataset_path', str), ('dataset_status', str), ('dataset_id', str)]):

  import sys
  import subprocess
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'googleapis-common-protos==1.6.0',
      '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-cloud-automl==0.9.0',
      '--quiet', '--no-warn-script-location'],
      env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)

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
  
  status = 'created'
  project_location = client.location_path(gcp_project_id, gcp_region)
  # Check if dataset is existed.
  for element in client.list_datasets(project_location):
    if element.display_name == dataset_display_name:
      status = 'created but existed'
      if element.example_count == 0:
        status = 'existed but empty'
        return (element.name, status, element.name.rsplit('/', 1)[-1])
  try:
    metadata = automl.types.TextClassificationDatasetMetadata(classification_type=automl.enums.ClassificationType.MULTICLASS)
    dataset = automl.types.Dataset(display_name=dataset_display_name, text_classification_dataset_metadata=metadata,)
    # Create a dataset with the given display name
    response = client.create_dataset(project_location, dataset)
    created_dataset = response.result()
    # Log info about the created dataset
    logging.info("Dataset name: {}".format(created_dataset.name))
    logging.info("Dataset id: {}".format(created_dataset.name.split("/")[-1]))
    logging.info("Dataset display name: {}".format(dataset.display_name))
    logging.info("Dataset example count: {}".format(dataset.example_count))
    logging.info("Dataset create time:")
    logging.info("\tseconds: {}".format(dataset.create_time.seconds))
    logging.info("\tnanos: {}".format(dataset.create_time.nanos))
    
    dataset_id = created_dataset.name.rsplit('/', 1)[-1]
    return (created_dataset.name, status, dataset_id)
  except google.api_core.exceptions.GoogleAPICallError as e:
    logging.warning(e)
    raise e


if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(automl_create_dataset_for_nlp,
      output_component_file='dataset_component.yaml', base_image='python:3.7')
