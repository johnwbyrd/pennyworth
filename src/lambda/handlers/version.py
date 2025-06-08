import os
from version import API_SEMANTIC_VERSION
from utils import tracer

PENNYWORTH_API_VERSION = os.environ.get("PENNYWORTH_API_VERSION", "v1")
GIT_COMMIT = os.environ.get("GIT_COMMIT", "unknown")

@tracer.capture_method
def version_handler():
    return {
        "Version": PENNYWORTH_API_VERSION,
        "SemanticVersion": API_SEMANTIC_VERSION,
        "Commit": GIT_COMMIT
    }, 200 