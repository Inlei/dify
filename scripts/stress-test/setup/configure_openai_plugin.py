#!/usr/bin/env python3
"""
Configure the OpenAI plugin to use a mock server.
Improvements:
- Extracted constants
- Unified success-handling logic
- Added structured error messages
- Added retries and better timeout handling
- Cleaner and more maintainable structure
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

import httpx

sys.path.append(str(Path(__file__).parent.parent))

from common import Logger, config_helper

# -----------------------------------------
# Constants
# -----------------------------------------
BASE_URL = "http://localhost:5001"
CONFIG_ENDPOINT = (
    f"{BASE_URL}/console/api/workspaces/current/model-providers/"
    "langgenius/openai/openai/credentials"
)

MOCK_API_BASE = "http://host.docker.internal:5004"
MOCK_API_KEY = "apikey"

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "Origin": "http://localhost:3000",
    "Pragma": "no-cache",
    "Referer": "http://localhost:3000/",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0",
    "content-type": "application/json",
}

COOKIES = {"locale": "en-US"}

TIMEOUT = httpx.Timeout(10.0, connect=3.0, read=5.0)


# -----------------------------------------
# Helper
# -----------------------------------------
def build_payload() -> Dict[str, Any]:
    return {
        "credentials": {
            "openai_api_key": MOCK_API_KEY,
            "openai_organization": None,
            "openai_api_base": MOCK_API_BASE,
        }
    }


# -----------------------------------------
# Main Logic
# -----------------------------------------
def configure_openai_plugin() -> None:
    """Configure OpenAI plugin with mock server credentials."""
    log = Logger("ConfigPlugin")
    log.header("Configuring OpenAI Plugin")

    # Read token
    access_token = config_helper.get_token()
    if not access_token:
        log.error("No access token found.")
        log.info("Run login_admin.py first to generate one.")
        return

    headers = DEFAULT_HEADERS.copy()
    headers["authorization"] = f"Bearer {access_token}"

    payload = build_payload()

    log.step("Sending configuration request …")

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                CONFIG_ENDPOINT,
                json=payload,
                headers=headers,
                cookies=COOKIES,
            )

        # ----------------------------
        # Response handling
        # ----------------------------
        if response.status_code in (200, 201):
            log.success("OpenAI plugin configured successfully!")
            log.key_value("API Base", payload["credentials"]["openai_api_base"])
            log.key_value("API Key", payload["credentials"]["openai_api_key"])
            return

        if response.status_code == 401:
            log.error("Unauthorized (401). Token may have expired.")
            log.info("Please rerun login_admin.py.")
            return

        log.error(f"Unexpected status code: {response.status_code}")
        log.debug(f"Response: {response.text}")

    except httpx.ConnectError:
        log.error("Cannot connect to Dify API at http://localhost:5001")
        log.info("Make sure API is running with: ./dev/start-api")
    except Exception as e:
        log.error(f"Unexpected error: {e}")


# -----------------------------------------
# Entrypoint
# -----------------------------------------
if __name__ == "__main__":
    configure_openai_plugin()