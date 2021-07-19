import json
import argparse
import boto3
import utils


def predict(endpoint_name: str, predict_role_arn: str,
            image_bucket: str, image_s3_key: str):

    if predict_role_arn is None:
        boto_session = boto3.Session()
    else:
        boto_session = utils.assume_role(
            predict_role_arn, role_session_name='predictor-session')

    sagemaker_client = boto_session.client('sagemaker-runtime')

    response = sagemaker_client.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=json.dumps({
            'bucket': image_bucket,
            's3_key': image_s3_key
        }),
        ContentType='application/json'
    )

    result = json.load(response['Body'])
    for label, confidence in zip(
            result['labels'][0], result['confidences'][0]):
        print(f'{label:<20}: {confidence:0.6f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint_name', type=str,
                        default='imagenet-resnet50')
    parser.add_argument('--predict_role_arn', type=str)
    parser.add_argument('--image_bucket', type=str, required=True)
    parser.add_argument('--image_s3_key', type=str, required=True)
    args = parser.parse_args()

    predict(endpoint_name=args.endpoint_name,
            predict_role_arn=args.predict_role_arn,
            image_bucket=args.image_bucket,
            image_s3_key=args.image_s3_key)
