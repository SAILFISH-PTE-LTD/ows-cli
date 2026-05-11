class OwsError(Exception):
    """Base exception for all ows errors."""
    pass


class AuthError(OwsError):
    """Authentication failed — credentials invalid or token unusable."""
    pass


class APIError(OwsError):
    """API returned a non-200 response code."""
    def __init__(self, code: int, message: str, data: object = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"[{code}] {message}")


class NetworkError(OwsError):
    """HTTP connection or timeout error."""
    pass
