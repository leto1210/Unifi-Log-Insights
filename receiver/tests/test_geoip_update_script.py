"""geoip-update.sh must refuse to download when it cannot install the result."""

import os
import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / 'geoip-update.sh'


def _run(tmp_path, db_dir):
    """Run the script with a stub geoipupdate that records each invocation."""
    stub_dir = tmp_path / 'bin'
    stub_dir.mkdir()
    calls = tmp_path / 'calls'
    stub = stub_dir / 'geoipupdate'
    stub.write_text(f'#!/bin/sh\necho called >> "{calls}"\n')
    stub.chmod(0o755)
    env = {**os.environ, 'PATH': f'{stub_dir}:{os.environ["PATH"]}',
           'GEOIP_DB_DIR': str(db_dir)}
    result = subprocess.run(['bash', str(SCRIPT), '--force'], env=env,
                            capture_output=True, text=True, timeout=30)
    return result, calls


@pytest.mark.skipif(os.geteuid() == 0, reason='root ignores directory permissions')
def test_unwritable_directory_fails_before_any_download(tmp_path):
    """A 555 directory exits 1 with a clear message and never calls geoipupdate."""
    db_dir = tmp_path / 'maxmind'
    db_dir.mkdir()
    db_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        result, calls = _run(tmp_path, db_dir)
    finally:
        db_dir.chmod(0o755)
    assert result.returncode == 1
    assert 'not writable' in result.stdout
    assert not calls.exists()


def test_writable_directory_runs_the_update(tmp_path):
    """A writable directory reaches geoipupdate and succeeds."""
    db_dir = tmp_path / 'maxmind'
    db_dir.mkdir()
    result, calls = _run(tmp_path, db_dir)
    assert result.returncode == 0, result.stdout
    assert calls.read_text().count('called') == 1


def test_missing_directory_fails_before_any_download(tmp_path):
    """A missing directory is rejected the same way."""
    result, calls = _run(tmp_path, tmp_path / 'absent')
    assert result.returncode == 1
    assert not calls.exists()
