"""Shared test helpers. Every test runs with the network switched off."""

import json
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
# The fetcher is a script inside the skill folder, not a package, so its folder goes on the path.
sys.path.insert(0, str(REPO_DIR / "files" / ".claude" / "skills" / "youtube-summary"))


def _no_network(*args, **kwargs):
    raise RuntimeError("network disabled in tests")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", _no_network)
    monkeypatch.setattr(socket.socket, "connect_ex", _no_network)
    monkeypatch.setattr(socket, "create_connection", _no_network)


def snippets_from(rows):
    """Caption snippets as the fetcher reads them: only .text and .start are used."""
    return [SimpleNamespace(**row) for row in rows]


@pytest.fixture
def manual_rows():
    return json.loads((FIXTURES / "captions_manual.json").read_text(encoding="utf-8"))
