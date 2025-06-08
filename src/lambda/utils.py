import json
from aws_lambda_powertools import Logger, Tracer

# Set up Powertools logger for the Lambda package
logger = Logger(service="pennyworth")
tracer = Tracer(service="pennyworth")