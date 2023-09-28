import boto3
from botocore.exceptions import NoRegionError, NoCredentialsError
from src.config import AWS_KEY_ID, AWS_KEY_SECRET, AWS_REGION


def create_aws_client(service_name):

    region = AWS_REGION
    pk = AWS_KEY_ID
    sk = AWS_KEY_SECRET

    try:
        if pk and sk:
            session = boto3.Session(
                aws_access_key_id=pk,
                aws_secret_access_key=sk,
            )
            client = session.client(service_name, region_name=region)
        else:
            client = boto3.client(service_name, region_name=region)
        return client
    except (NoRegionError, NoCredentialsError) as e:
        print("Error from Botocore", e)