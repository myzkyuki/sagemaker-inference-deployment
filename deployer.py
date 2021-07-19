import argparse
from typing import Optional
import botocore
import sagemaker
from sagemaker.tensorflow import TensorFlowModel

import utils


ENTRY_POINT = 'inference.py'


class SagemakerClient:
    def __init__(self, deploy_role_arn: Optional[str] = None):
        self.sagemaker_session = None
        self.init_sagemaker_session(deploy_role_arn)

    def init_sagemaker_session(
            self, deploy_role_arn: Optional[str] = None):
        if deploy_role_arn is None:
            boto_session = None
        else:
            boto_session = utils.assume_role(
                deploy_role_arn, role_session_name='deployer-session')

        self.sagemaker_session = sagemaker.Session(boto_session=boto_session)

    def delete_old_model(self, model_name: str):
        try:
            self.sagemaker_session.delete_model(model_name)
            print(f'Delete old model {model_name}.')
        except botocore.exceptions.ClientError:
            pass

        try:
            self.sagemaker_session.delete_endpoint_config(model_name)
            print(f'Delete old endpoint config {model_name}.')
        except botocore.exceptions.ClientError:
            pass

        try:
            self.sagemaker_session.delete_endpoint(model_name)
            print(f'Delete old endpoint {model_name}.')
        except botocore.exceptions.ClientError:
            pass

    def deploy(self, model_path: str, exec_role_arn: str,
               tf_version: str, model_name: str,
               num_instances: int, instance_type: str):
        self.delete_old_model(model_name)

        model = TensorFlowModel(
            model_data=model_path,
            entry_point=ENTRY_POINT,
            role=exec_role_arn,
            framework_version=tf_version,
            name=model_name,
            sagemaker_session=self.sagemaker_session)

        model.deploy(
            initial_instance_count=num_instances,
            instance_type=instance_type,
            endpoint_name=model_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--deploy_role_arn', type=str)
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--exec_role_arn', type=str, required=True)
    parser.add_argument('--tf_version', type=str, default='2.3.1')
    parser.add_argument('--model_name', type=str, default='imagenet-resnet50')
    parser.add_argument('--num_instances', type=int, default=1)
    parser.add_argument('--instance_type', type=str, default='ml.t2.medium')
    args = parser.parse_args()

    sagemaker_client = SagemakerClient(deploy_role_arn=args.deploy_role_arn)
    sagemaker_client.deploy(
        model_path=args.model_path,
        exec_role_arn=args.exec_role_arn,
        tf_version=args.tf_version,
        model_name=args.model_name,
        num_instances=args.num_instances,
        instance_type=args.instance_type)
