import os
from version import API_SEMANTIC_VERSION
from utils import tracer
from src.shared.constants import *

@tracer.capture_method
def version_handler():
    return {
        "Version": PENNYWORTH_API_VERSION,
        "SemanticVersion": PENNYWORTH_API_SEMANTIC_VERSION,
        "Commit": PENNYWORTH_GIT_COMMIT
    }, 200 