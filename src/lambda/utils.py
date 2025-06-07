import json
from aws_lambda_powertools import Logger
from billing import track_usage

# Set up Powertools logger for the Lambda package
logger = Logger(service="pennyworth")