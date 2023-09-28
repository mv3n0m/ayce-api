import json
import requests
from .utils import create_aws_client
from src.config import LAMBDA_FUNCTION_URL, LAMBDA_FUNCTION_NAME


lambda_client = create_aws_client("lambda")

def enqueue_transaction(payload):

    payload = json.dumps(payload)

    if LAMBDA_FUNCTION_URL:
        response = requests.post(LAMBDA_FUNCTION_URL, data=payload)
    else:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="Event",
            LogType="Tail",
            Payload=payload,
        )
    return response
