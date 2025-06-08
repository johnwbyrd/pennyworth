import json
from aws_lambda_powertools import Logger

# Set up Powertools logger for the Lambda package
logger = Logger(service="pennyworth")