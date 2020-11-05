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
from kfp.components import InputPath, OutputPath

def automl_evaluate_model_for_nlp(
  mlpipeline_metrics_path: OutputPath('UI_metrics'),
  gcp_project_id: str,
  gcp_region: str,
  api_endpoint: str = None,
  model_name: str = None,
) -> NamedTuple('Outputs', [('auprc', float), ('f1', float), ('recall', float), ('precision', float)]):

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
  import json

  logging.getLogger().setLevel(logging.INFO)  # TODO: make level configurable

  if api_endpoint:
    client_options = ClientOptions(api_endpoint=api_endpoint)
    client = automl.AutoMlClient(client_options=client_options)
  else:
    client = automl.AutoMlClient()

  # A resource that represents Google Cloud Platform location.
  project_location = client.location_path(gcp_project_id, gcp_region)
  
  print("List of model evaluations:")
  for evaluation in client.list_model_evaluations(model_name, ""):
    if evaluation.display_name == '':
        logging.info("Model evaluation name: {}".format(evaluation.name))
        logging.info(
            "Model annotation spec id: {}".format(
                evaluation.annotation_spec_id
            )
        )
        logging.info("Create Time:")
        logging.info("\tseconds: {}".format(evaluation.create_time.seconds))
        logging.info("\tnanos: {}".format(evaluation.create_time.nanos / 1e9))
        logging.info(
            "Evaluation example count: {}".format(
            evaluation.evaluated_example_count
            )
        )
        logging.info(
            "Model evaluation metrics - auprc: {}".format(
                evaluation.classification_evaluation_metrics.au_prc
            )
        )
        auprc = evaluation.classification_evaluation_metrics.au_prc
        for eva_num in evaluation.classification_evaluation_metrics.confidence_metrics_entry:
            if eva_num.confidence_threshold == 0.5:
                logging.info(
                    "Model evaluation metrics (threshold = 0.5): {}".format(
                        eva_num
                    )
                )
                f1 = eva_num.f1_score
                recall = eva_num.recall
                precision = eva_num.precision
                break
        break

  print('overall threshold = 0.5, F1: {}, recall: {}, auprc: {}, precision: {}'.format(f1, recall, auprc, precision))
  
   
  metrics = {
    'metrics': [{
      'name': 'precision-score', # The name of the metric. Visualized as the column name in the runs table.
      'numberValue':  precision, # The value of the metric. Must be a numeric value.
      'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
    },
    {
      'name': 'recall-score', # The name of the metric. Visualized as the column name in the runs table.
      'numberValue':  recall, # The value of the metric. Must be a numeric value.
      'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
    },
    {
      'name': 'f1-score', # The name of the metric. Visualized as the column name in the runs table.
      'numberValue':  f1, # The value of the metric. Must be a numeric value.
      'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
    },
    {
      'name': 'auprc', # The name of the metric. Visualized as the column name in the runs table.
      'numberValue':  auprc, # The value of the metric. Must be a numeric value.
      'format': "PERCENTAGE",   # The optional format of the metric. Supported values are "RAW" (displayed in raw format) and "PERCENTAGE" (displayed in percentage format).
    }
    ]
  }
  with open(mlpipeline_metrics_path, 'w') as mlpipeline_metrics_file:
    mlpipeline_metrics_file.write(json.dumps(metrics))
  

  return (auprc, f1, recall, precision)



if __name__ == '__main__':
  import kfp
  kfp.components.func_to_container_op(automl_evaluate_model_for_nlp,
      output_component_file='evaluate_component.yaml',
      base_image='python:3.7'
      )
