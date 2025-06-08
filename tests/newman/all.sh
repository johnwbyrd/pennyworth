#!/bin/bash

# Exit on error
set -e

newman run ../postman/collection/api.json \
  -e ../postman/env/prod.json \
  ${BASE_DOMAIN:+--env-var "base_domain=api.${BASE_DOMAIN}"} \
  -r cli,json \
  --bail 