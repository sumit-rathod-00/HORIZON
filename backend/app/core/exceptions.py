class HorizonException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UserNotFoundException(HorizonException):
    def __init__(self):
        super().__init__("User not found", 404)


class ProjectNotFoundException(HorizonException):
    def __init__(self):
        super().__init__("Project not found", 404)


class AssetNotFoundException(HorizonException):
    def __init__(self):
        super().__init__("Asset not found", 404)


class VulnerabilityNotFoundException(HorizonException):
    def __init__(self):
        super().__init__("Vulnerability not found", 404)


class ScanNotFoundException(HorizonException):
    def __init__(self):
        super().__init__("Scan not found", 404)


class UnauthorizedException(HorizonException):
    def __init__(self):
        super().__init__("Unauthorized", 401)


class ForbiddenException(HorizonException):
    def __init__(self):
        super().__init__("Forbidden", 403)


class BadRequestException(HorizonException):
    def __init__(self, message: str):
        super().__init__(message, 400)


class ConflictException(HorizonException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)


class ValidationException(HorizonException):
    def __init__(self, message: str):
        super().__init__(message, 422)