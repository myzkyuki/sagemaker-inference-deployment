import boto3

REGION_NAME = 'ap-northeast-1'


def assume_role(role_arn: str, role_session_name: str) -> boto3.Session:

    client = boto3.Session(profile_name='default').client('sts')
    res = client.assume_role(RoleArn=role_arn,
                             RoleSessionName=role_session_name,
                             DurationSeconds=60 * 60 * 6)
    access_key_id = res['Credentials']['AccessKeyId']
    secret_access_key = res['Credentials']['SecretAccessKey']
    session_token = res['Credentials']['SessionToken']
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=REGION_NAME)

    return session
