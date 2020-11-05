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

def config_firestore(
  gcp_project_id: str,
  gcp_region: str,
  model_id: str,
) -> NamedTuple('Outputs', [('collection', str), ('document', str)]):
  import sys
  import subprocess
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'googleapis-common-protos==1.6.0',
      '--no-warn-script-location'], env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)
  subprocess.run([sys.executable, '-m', 'pip', 'install', 'google-cloud-firestore==1.6.2', '--quiet',
      '--no-warn-script-location'], env={'PIP_DISABLE_PIP_VERSION_CHECK': '1'}, check=True)

  import google
  import logging
  from google.api_core.client_options import ClientOptions
  from google.cloud import firestore

  #logging.getLogger().setLevel(logging.INFO)  # TODO: make level configurable
  db = firestore.Client()
  collection_name = 'nlp_config'
  document_name = 'automl_config'
  app_template = db.collection('nlp_config').document('automl_config')
  app_template.set({'model_id': model_id})
  return (collection_name, document_name)


if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(config_firestore,
      output_component_file='firestore_component.yaml', base_image='python:3.7')
