import json
import logging
from billing import track_usage

# Set up a logger for the Lambda package
logger = logging.getLogger("pennyworth")
# In the future, a custom handler can be added in log.py for CloudWatch or other destinations

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