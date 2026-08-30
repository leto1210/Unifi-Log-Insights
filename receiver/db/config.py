"""API key encryption and system_config helpers.

The ``get_config`` / ``set_config`` module-level functions are thin
delegates over a :class:`Database` instance — kept for the public API
that legacy callers rely on (``from db import get_config, set_config``).
"""

import base64
import json
import logging
import os

logger = logging.getLogger(__name__)


# ── API Key Encryption ────────────────────────────────────────────────────────

def _derive_fernet_key(postgres_password: str) -> bytes:
    """Derive a Fernet encryption key from POSTGRES_PASSWORD."""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'unifi-log-insight-v1',
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(postgres_password.encode()))


def _get_secret_key() -> str:
    """Return the encryption secret: SECRET_KEY > POSTGRES_PASSWORD > DB_PASSWORD."""
    return (os.environ.get('SECRET_KEY')
            or os.environ.get('POSTGRES_PASSWORD')
            or os.environ.get('DB_PASSWORD', ''))


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage in system_config."""
    from cryptography.fernet import Fernet
    secret = _get_secret_key()
    if not secret:
        raise ValueError("SECRET_KEY or POSTGRES_PASSWORD required for encryption")
    f = Fernet(_derive_fernet_key(secret))
    return f.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted: str) -> str:
    """Decrypt API key from system_config. Returns empty string on failure."""
    from cryptography.fernet import Fernet, InvalidToken
    secret = _get_secret_key()
    if not secret or not encrypted:
        return ''
    try:
        f = Fernet(_derive_fernet_key(secret))
        return f.decrypt(encrypted.encode()).decode()
    except (InvalidToken, Exception) as e:
        logger.warning("Failed to decrypt API key (SECRET_KEY/POSTGRES_PASSWORD may have changed): %s", e)
        return ''


# ── system_config module-level helpers ───────────────────────────────────────

def get_config(db, key: str, default=None):
    """Standalone helper: fetch config using Database instance."""
    return db.get_config(key, default)


def set_config(db, key: str, value):
    """Standalone helper: set config using Database instance."""
    return db.set_config(key, value)


def get_wan_ips_from_config(db) -> list[str]:
    """Derive ordered WAN IP list from wan_ip_by_iface + wan_interfaces.

    Falls back to legacy 'wan_ips' config key if 'wan_ip_by_iface' doesn't
    exist (pre-multi-WAN installs that haven't re-run the wizard).
    Returns list of WAN IP strings (may be empty).
    """
    wan_ip_by_iface = db.get_config('wan_ip_by_iface')
    if wan_ip_by_iface:
        wan_interfaces = db.get_config('wan_interfaces', [])
        # Derive ordered list following wan_interfaces order
        return [wan_ip_by_iface[iface] for iface in wan_interfaces
                if iface in wan_ip_by_iface and wan_ip_by_iface[iface]]
    # Legacy fallback: use wan_ips config key directly
    return db.get_config('wan_ips') or []


def parse_vpn_config(raw) -> dict:
    """Parse vpn_networks config value into a dict, handling all storage forms."""
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}
