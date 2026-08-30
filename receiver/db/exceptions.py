"""Exceptions raised by the db package."""


class AdGuardHostMismatch(Exception):
    """Raised by insert_adguard_batch when the DB host differs from the expected host.

    This indicates a config change landed between the start of _poll() and the
    DB commit — the batch is discarded to prevent cursor corruption.
    """
