from typing import Optional, Dict, Any

class BaseAPIException(Exception):
    def __init__(self, error: str, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class NotFoundException(BaseAPIException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__("NOT_FOUND", message, 404, details)

class ForbiddenException(BaseAPIException):
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__("FORBIDDEN", message, 403, details)

class ConflictException(BaseAPIException):
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__("CONFLICT", message, 409, details)

class RateLimitException(BaseAPIException):
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__("RATE_LIMIT", message, 429, details)

class ExternalServiceException(BaseAPIException):
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__("EXTERNAL_SERVICE_ERROR", message, 502, details)

class InsufficientCreditsException(BaseAPIException):
    def __init__(self, message: str = "Insufficient credits", details: Optional[Dict[str, Any]] = None):
        super().__init__("INSUFFICIENT_CREDITS", message, 402, details)

class StorageLimitException(BaseAPIException):
    def __init__(self, message: str = "Storage limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__("STORAGE_LIMIT", message, 413, details)

class ValidationException(BaseAPIException):
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__("VALIDATION_ERROR", message, 422, details)

class BadRequestException(BaseAPIException):
    def __init__(self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None):
        super().__init__("BAD_REQUEST", message, 400, details)
