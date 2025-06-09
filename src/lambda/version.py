# src/lambda/version.py
import os

API_SEMANTIC_VERSION = os.environ.get("PENNYWORTH_API_SEMANTIC_VERSION", "0.1.0")
