from utils import logger


class APIException(Exception):
    status_code = 500

    def __init__(self, message):
        logger.warning(message)
        super().__init__(message)
        self.message = message


class ForbiddenException(APIException):
    status_code = 403


class BadRequestException(APIException):
    status_code = 400


class NotFoundException(APIException):
    status_code = 404


class NotImplementedException(APIException):
    status_code = 501
