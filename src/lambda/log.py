import logging

class PennyworthLogHandler(logging.Handler):
    """
    Custom log handler for Pennyworth.
    Stub: does nothing for now. Can be expanded to emit logs directly to CloudWatch or other destinations.
    """
    def emit(self, record):
        # Stub: do nothing for now
        # TODO: Expand to send logs directly to CloudWatch or other services
        pass 