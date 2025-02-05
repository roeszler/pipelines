"""AutoML Pipeline Finalizer component spec."""

# Copyright 2023 The Kubeflow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Optional

from kfp import dsl


@dsl.container_component
def automl_tabular_finalizer(
    project: str,
    location: str,
    root_dir: str,
    gcp_resources: dsl.OutputPath(str),
    encryption_spec_key_name: Optional[str] = '',
):
  # fmt: off
  """Finalizer for AutoML Tabular pipelines.

  Args:
      project (str): Required. Project to run Cross-validation trainer.
      location (str): Location for running the Cross-validation trainer.
      root_dir (str): The Cloud Storage location to store the output.
      encryption_spec_key_name (Optional[str]): Customer-managed encryption key.

  Returns:
      gcp_resources (str):
          GCP resources created by this component.
          For more details, see
          https://github.com/kubeflow/pipelines/blob/master/components/google-cloud/google_cloud_pipeline_components/proto/README.md.
  """
  # fmt: on

  return dsl.ContainerSpec(
      # LINT.IfChange
      image='gcr.io/ml-pipeline/google-cloud-pipeline-components:1.0.44',
      # LINT.ThenChange(//depot/google3/cloud/ml/pipelines/shared/pipeline_data_access_layer/first_party_components_config.h)
      command=[
          'python3',
          '-u',
          '-m',
          'google_cloud_pipeline_components.container.v1.custom_job.launcher',
      ],
      args=[
          '--type',
          'CustomJob',
          '--project',
          project,
          '--location',
          location,
          '--gcp_resources',
          gcp_resources,
          '--payload',
          dsl.ConcatPlaceholder(
              items=[
                  (
                      '{"display_name":'
                      f' "automl-tabular-finalizer-{dsl.PIPELINE_JOB_ID_PLACEHOLDER}-{dsl.PIPELINE_TASK_ID_PLACEHOLDER}",'
                      ' "encryption_spec": {"kms_key_name":"'
                  ),
                  encryption_spec_key_name,
                  (
                      '"}, "job_spec": {"worker_pool_specs": [{"replica_count":'
                      ' 1, "machine_spec": {"machine_type": "n1-standard-8"},'
                      ' "container_spec": {"image_uri":"'
                  ),
                  'us-docker.pkg.dev/vertex-ai-restricted/automl-tabular/training:20230605_0125',
                  '", "args": ["cancel_l2l_tuner", "--error_file_path=',
                  root_dir,
                  (
                      f'/{dsl.PIPELINE_JOB_ID_PLACEHOLDER}/{dsl.PIPELINE_TASK_ID_PLACEHOLDER}/error.pb",'
                      ' "--cleanup_lro_job_infos='
                  ),
                  root_dir,
                  f'/{dsl.PIPELINE_JOB_ID_PLACEHOLDER}/lro"' + ']}}]}}',
              ]
          ),
      ],
  )
