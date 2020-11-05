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


import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.components as comp
import json
import time

create_dataset_op = comp.load_component_from_file(
  './create_dataset/dataset_component.yaml'
  )
import_data_op = comp.load_component_from_file(
  './import_data_from_gcs/import_component.yaml'
  )
train_model_op = comp.load_component_from_file(
    './create_model/model_component.yaml')
eval_model_op = comp.load_component_from_file(
    './create_model/evaluate_component.yaml')
deploy_model_op = comp.load_component_from_file(
    './deploy_model/deploy_component.yaml'
    )
config_firestore_op = comp.load_component_from_file(
    './param_firestore/firestore_component.yaml'
)

@dsl.pipeline(
  name='AutoML NLP',
  description='Demonstrate an AutoML NLP workflow'
)
def automl_nlp(  #pylint: disable=unused-argument
  gcp_project_id: str = '',
  gcp_region: str = 'us-central1',
  dataset_display_name: str = '',
  api_endpoint: str = '',
  gcs_path: str = '',
  model_prefix: str = 'nlpmodel',
  ):

  create_dataset = create_dataset_op(
    gcp_project_id=gcp_project_id,
    gcp_region=gcp_region,
    dataset_display_name=dataset_display_name,
    api_endpoint=api_endpoint
    )

  # Disable cache
  #task_never_use_cache = create_dataset
  #task_never_use_cache.execution_options.caching_strategy.max_cache_staleness = "P0D"

  import_data = import_data_op(
    gcp_project_id=gcp_project_id,
    gcp_region=gcp_region,
    dataset_id=create_dataset.outputs['dataset_id'],
    api_endpoint=api_endpoint,
    gcs_path=gcs_path
    )

  train_model = train_model_op(
    gcp_project_id=gcp_project_id,
    gcp_region=gcp_region,
    dataset_id=import_data.outputs['dataset_id'],
    api_endpoint=api_endpoint,
    model_prefix=model_prefix
    )
  
  import_data.after(create_dataset)
  train_model.after(import_data)

  eval_model = eval_model_op(
    gcp_project_id=gcp_project_id,
    gcp_region=gcp_region,
    api_endpoint=api_endpoint,
    model_name=train_model.outputs['model_name']
    )
  

  deploy_model = deploy_model_op(
      gcp_project_id=gcp_project_id,
      gcp_region=gcp_region,
      api_endpoint=api_endpoint,
      model_display_name=train_model.outputs['model_display_name'],
      model_id=train_model.outputs['model_id']
      )
      
  config_firestore = config_firestore_op(
      gcp_project_id=gcp_project_id,
      gcp_region=gcp_region,
      model_id=deploy_model.outputs['model_id']
  )
  eval_model.after(train_model)
  deploy_model.after(train_model)
  config_firestore.after(deploy_model)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(automl_nlp, __file__ + '.tar.gz')
