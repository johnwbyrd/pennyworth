import json
from aws_lambda_powertools import Logger
from billing import track_usage

# Set up Powertools logger for the Lambda package
logger = Logger(service="pennyworth")

def json_response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict)
    }

def log_event(event_type, details):
    # Basic logging to stdout (captured by CloudWatch in Lambda)
    print(f"[LOG] {event_type}: {json.dumps(details)}")
    # TODO: Enhance logging (structured logs, external systems) if needed 