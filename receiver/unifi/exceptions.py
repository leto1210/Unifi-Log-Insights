"""Exceptions raised by the UniFi API client."""


class UniFiPermissionError(Exception):
    """Raised when the UniFi Integration API returns 401 (auth failure) or 403 (insufficient permissions)."""
    def __init__(self, message, status_code=403):
        """Store the HTTP status code alongside the error message."""
        super().__init__(message)
        self.status_code = status_code
