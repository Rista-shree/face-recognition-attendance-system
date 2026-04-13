# ─────────────────────────────────────────────
#  desktop/services/auth_service.py
#  Manages the API token used by the desktop
#  app to authenticate with the FastAPI backend.
#
#  Tokens are stored in a local encrypted file
#  so the user doesn't have to re-login after
#  restarting the app.
# ─────────────────────────────────────────────

import base64
import hashlib
import json
import logging
import os
from pathlib import Path
from typing  import Optional

import requests
import platform
from config.settings import API_BASE_URL

logger = logging.getLogger(__name__)

# Where the token is persisted locally
_TOKEN_FILE = Path(__file__).resolve().parent.parent / "config" / ".auth_token"

# Simple obfuscation key derived from machine hostname
# (not true encryption — use keyring for production)
_OBFUSCATION_KEY = hashlib.sha256(
    os.environ.get("COMPUTERNAME", platform.node()).encode()
).digest()

class AuthService:
    """
    Handles login, logout, and token persistence for the desktop app.

    Token lifecycle:
        1. On startup, try to load a saved token from disk.
        2. If none, prompt user to login (via login() method).
        3. Token is attached to every outbound API request via
           get_auth_headers().
        4. On logout, token is deleted from disk and memory.
    """

    def __init__(self):
        self._token:    Optional[str] = None
        self._username: Optional[str] = None
        self._load_token()

    # ── Public API ─────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate against the backend API.

        Returns:
            (True, "")           on success
            (False, error_msg)   on failure
        """
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )

            if resp.status_code == 200:
                data           = resp.json()
                self._token    = data.get("access_token")
                self._username = username
                self._save_token()
                logger.info("Logged in as %s", username)
                return True, ""

            # Handle known error responses
            detail = resp.json().get("detail", "Login failed")
            logger.warning("Login failed for %s: %s", username, detail)
            return False, detail

        except requests.ConnectionError:
            msg = "Cannot reach the backend server. Check that it is running."
            logger.error(msg)
            return False, msg

        except requests.Timeout:
            msg = "Login request timed out."
            logger.error(msg)
            return False, msg

        except Exception as e:
            logger.exception("Unexpected login error")
            return False, str(e)

    def logout(self):
        """Clear the in-memory token and delete the saved token file."""
        self._token    = None
        self._username = None
        if _TOKEN_FILE.exists():
            _TOKEN_FILE.unlink()
        logger.info("Logged out")

    def get_auth_headers(self) -> dict:
        """
        Return HTTP headers needed to authenticate API requests.
        Attach these to every requests.Session or individual call.

        Example:
            headers = auth_service.get_auth_headers()
            resp = requests.get(url, headers=headers)
        """
        if not self._token:
            return {}
        return {"Authorization": f"Bearer {self._token}"}

    def refresh_token(self) -> bool:
        """
        Ask the backend for a new token using the refresh endpoint.
        Returns True if the token was refreshed successfully.
        """
        if not self._token:
            return False

        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/auth/refresh",
                headers=self.get_auth_headers(),
                timeout=10,
            )
            if resp.status_code == 200:
                self._token = resp.json().get("access_token")
                self._save_token()
                logger.info("Token refreshed for %s", self._username)
                return True

            logger.warning("Token refresh failed: %s", resp.status_code)
            return False

        except requests.RequestException as e:
            logger.error("Token refresh error: %s", e)
            return False

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def token(self) -> Optional[str]:
        return self._token

    # ── Token Persistence ──────────────────────────────────────────────────────

    def _save_token(self):
        """
        Persist the token to disk with simple XOR obfuscation.
        The file is only readable by the current OS user (mode 600).
        """
        if not self._token:
            return

        payload = json.dumps({
            "token":    self._token,
            "username": self._username,
        }).encode()

        obfuscated = _xor_bytes(payload, _OBFUSCATION_KEY)
        encoded    = base64.b64encode(obfuscated)

        _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_FILE.write_bytes(encoded)

        # Restrict file permissions to owner-only on Unix
        try:
            _TOKEN_FILE.chmod(0o600)
        except (AttributeError, NotImplementedError):
            pass  # Windows doesn't support chmod the same way

        logger.debug("Token saved to %s", _TOKEN_FILE)

    def _load_token(self):
        """Load and deobfuscate a saved token from disk, if it exists."""
        if not _TOKEN_FILE.exists():
            return

        try:
            encoded    = _TOKEN_FILE.read_bytes()
            obfuscated = base64.b64decode(encoded)
            payload    = _xor_bytes(obfuscated, _OBFUSCATION_KEY)
            data       = json.loads(payload.decode())

            self._token    = data.get("token")
            self._username = data.get("username")
            logger.info("Restored session for %s", self._username)

        except Exception:
            # If anything goes wrong (corrupt file, wrong key), start fresh
            logger.warning("Could not restore saved token – starting fresh")
            self._token    = None
            self._username = None
            if _TOKEN_FILE.exists():
                _TOKEN_FILE.unlink()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR *data* against *key* (repeated to match length)."""
    key_repeated = (key * (len(data) // len(key) + 1))[:len(data)]
    return bytes(a ^ b for a, b in zip(data, key_repeated))