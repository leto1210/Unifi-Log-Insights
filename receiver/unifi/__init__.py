"""UniFi Controller API client package.

Public surface:
- UniFiAPI: the controller client (Classic + Integration APIs, polling, firewall management).
- UniFiPermissionError: raised on 401/403 from the Integration API.
"""

from .core import UniFiAPI
from .exceptions import UniFiPermissionError

__all__ = ['UniFiAPI', 'UniFiPermissionError']
