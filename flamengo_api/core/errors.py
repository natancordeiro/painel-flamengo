from __future__ import annotations

class ApiError(Exception):
    def __init__(self, message: str, *, status: int = 400, code: str = "bad_request", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.details = details or {}


class NotFound(ApiError):
    def __init__(self, message: str = "Not found", *, details: dict | None = None):
        super().__init__(message, status=404, code="not_found", details=details)


class Unauthorized(ApiError):
    def __init__(self, message: str = "Unauthorized", *, details: dict | None = None):
        super().__init__(message, status=401, code="unauthorized", details=details)


class Conflict(ApiError):
    def __init__(self, message: str = "Conflict", *, details: dict | None = None):
        super().__init__(message, status=409, code="conflict", details=details)
