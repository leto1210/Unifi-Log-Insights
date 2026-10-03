"""Pi-hole v6 settings, connection test endpoints."""

import logging
import os

from fastapi import APIRouter, HTTPException

from db import get_config, encrypt_api_key
from deps import enricher_db, signal_receiver, pihole_poller
from pihole_api import _validate_pihole_url
from service.integration_urls import same_integration_destination

logger = logging.getLogger('api.pihole')

router = APIRouter()


@router.get("/api/settings/pihole")
def get_pihole_settings():
    """Current Pi-hole settings (merged: env + DB + defaults)."""
    return pihole_poller.get_settings_info()


@router.put("/api/settings/pihole")
def update_pihole_settings(body: dict):
    """Save Pi-hole settings to system_config."""
    with pihole_poller._config_lock:
        result = _update_pihole_settings_locked(body)
    pihole_poller.reload_config()
    signal_receiver()
    return result


def _update_pihole_settings_locked(body: dict):
    """Persist host and password under the shared client lock."""
    # Validate all fields before persisting anything
    interval = None
    if 'poll_interval' in body:
        try:
            interval = int(body['poll_interval'])
        except (ValueError, TypeError):
            raise HTTPException(400, 'poll_interval must be an integer')
        if interval < 15 or interval > 86400:
            raise HTTPException(400, 'poll_interval must be between 15 and 86400 seconds')
    if 'enrichment' in body:
        if body['enrichment'] not in ('none', 'geoip', 'threat', 'both'):
            raise HTTPException(400, 'enrichment must be one of: none, geoip, threat, both')
    
    # Validate host URL if provided
    normalized_host = None
    if 'host' in body:
        raw_host = body['host']
        if raw_host:
            try:
                normalized_host = _validate_pihole_url(raw_host)
            except ValueError as e:
                raise HTTPException(400, str(e))
        else:
            normalized_host = ''

    changed = False
    if normalized_host and os.environ.get('PIHOLE_PASSWORD') and not os.environ.get('PIHOLE_HOST'):
        raise HTTPException(400, 'PIHOLE_HOST is required with PIHOLE_PASSWORD')
    if normalized_host:
        bound_host = get_config(enricher_db, 'pihole_host', '')
        saved_password = get_config(enricher_db, 'pihole_password', '')
        try:
            changed = (not bound_host and bool(saved_password)) or (
                bool(bound_host) and not same_integration_destination(
                    normalized_host, bound_host, strip_admin_path=True))
        except ValueError:
            changed = True
        if changed and (not body.get('password') or os.environ.get('PIHOLE_PASSWORD')):
            raise HTTPException(400, 'New password is required when changing the Pi-hole host')

    # All valid — persist in one transaction, so a failure (e.g. encryption)
    # cannot leave the old password wiped while the new host is stored.
    current_host = get_config(enricher_db, 'pihole_host', '')
    updates = {}

    if 'enabled' in body:
        updates['pihole_enabled'] = body['enabled']
        if not body['enabled']:
            updates['pihole_poll_status'] = None
    if 'host' in body:
        if changed:
            updates['pihole_password'] = ''
        updates['pihole_host'] = normalized_host
    if body.get('password'):
        password_host = normalized_host or current_host
        if not password_host:
            raise HTTPException(400, 'A Pi-hole host is required to save a password')
        updates['pihole_password_host'] = password_host
        updates['pihole_password'] = encrypt_api_key(body['password'])
    if interval is not None:
        updates['pihole_poll_interval'] = interval
    if 'enrichment' in body:
        updates['pihole_enrichment'] = body['enrichment']

    # Reset cursor when host changes so we re-fetch from the new instance
    if normalized_host is not None and normalized_host != current_host:
        updates['pihole_last_cursor'] = 0
    enricher_db.set_config_many(updates)

    return {"success": True}


@router.post("/api/settings/pihole/test")
def test_pihole_connection(body: dict):
    """Test Pi-hole connectivity and authentication."""
    host = body.get('host', '').strip()
    password = body.get('password', '')

    result = pihole_poller.test_connection(host, password)
    return result
