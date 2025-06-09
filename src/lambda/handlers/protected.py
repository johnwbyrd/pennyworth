from utils import tracer


@tracer.capture_method
def protected_handler():
    import os

    return 200
