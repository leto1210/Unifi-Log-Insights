"""URL normalization helpers for local network integrations."""

from urllib.parse import urlparse, urlunparse


def normalize_integration_base_url(raw_url: str, *, strip_admin_path: bool = False) -> str:
    """Validate and normalize an HTTP(S) integration base URL.

    Bare hostnames are treated as HTTP URLs for LAN-friendly configuration.
    Userinfo, query strings, and fragments are rejected so callers always build
    their own API paths from a plain base URL.
    """
    value = (raw_url or '').strip()
    if not value:
        raise ValueError('Invalid URL')

    if '://' not in value:
        value = f'http://{value}'

    try:
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('Invalid URL')
        if not parsed.hostname:
            raise ValueError('Invalid URL')
        if parsed.username or parsed.password or parsed.params or parsed.query or parsed.fragment:
            raise ValueError('Invalid URL')
        # Accessing .port validates malformed port strings.
        port = parsed.port
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('Invalid URL') from exc

    hostname = parsed.hostname
    if ':' in hostname and not hostname.startswith('['):
        hostname = f'[{hostname}]'

    netloc = f'{hostname}:{port}' if port is not None else hostname
    path = (parsed.path or '').rstrip('/')
    if strip_admin_path and path == '/admin':
        path = ''

    return urlunparse((parsed.scheme, netloc, path, '', '', ''))


def build_integration_url(base_url: str, api_path: str) -> str:
    """Build an API URL from a normalized integration base and absolute path."""
    normalized = normalize_integration_base_url(base_url)
    base = urlparse(normalized)
    path = f"{base.path.rstrip('/')}/{api_path.lstrip('/')}"
    return urlunparse((base.scheme, base.netloc, path, '', '', ''))
