import os
from version import API_SEMANTIC_VERSION

PENNYWORTH_API_VERSION = os.environ.get("PENNYWORTH_API_VERSION", "v1")
PENNYWORTH_BUILD_ID = os.environ.get("PENNYWORTH_BUILD_ID", "unknown")

def version_handler():
    return {
        "Version": PENNYWORTH_API_VERSION,
        "SemanticVersion": API_SEMANTIC_VERSION,
        "BuildId": PENNYWORTH_BUILD_ID
    }, 200 