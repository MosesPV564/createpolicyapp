# file: thore_client.py
import os
import time
import base64
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import streamlit as st
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# from dotenv import load_dotenv

# ----------------------------
# ENV + LOGGING SETUP
# ----------------------------

# load_dotenv()

# BASE_URL = os.getenv("BASE_URL", "https://sandbox02.api.thore.exchange")
# USERNAME = os.getenv("USERNAME")
# PASSWORD = os.getenv("PASSWORD")
# APPLICATION_KEY = os.getenv("APPLICATION_KEY")


USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
BASE_URL = st.secrets["BASE_URL"]
APPLICATION_KEY = st.secrets["APPLICATION_KEY"]
LOG_FILE = "thore_client.log"
SUMMARY_FILE = "thore_run_summary.json"

# clear both on each run
for f in [LOG_FILE, SUMMARY_FILE]:
    try:
        open(f, "w").close()
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        # logging.StreamHandler()  # optional: also log to console
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------
# API CLIENT WITH RETRY LOGIC
# ----------------------------

class ThoreAPIClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.username = USERNAME
        self.password = PASSWORD
        self.application_key = APPLICATION_KEY
        self.token = None

    @staticmethod
    def _now_iso(offset_hours=-5) -> str:
        """Return current UTC datetime in the exact required format."""
        now = datetime.now(timezone.utc)
        # mimic `2025-10-24T00:45:02.880-05:00`
        local_time = now.replace(microsecond=880000)
        offset = f"{offset_hours:+03d}:00"
        return local_time.strftime(f"%Y-%m-%dT%H:%M:%S.%f")[:-3] + offset

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Wrapper around requests with logging and retry."""
        logger.info(f"Request: {method} {url}")
        try:
            resp = requests.request(method, url, timeout=60, **kwargs)
            logger.info(f"Response {resp.status_code} for {url}")
            if not resp.ok:
                logger.warning(f"Response body: {resp.text}")
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Request failed for {url}: {e}\nResponse body: {e.response.text}")
            else:
                logger.error(f"Request failed for {url}: {e}")
            raise

    def authenticate(self) -> str:
        """Step 1: Authenticate and store token from headers."""
        url = f"{self.base_url}/v1/Authenticate?application={self.application_key}"
        raw = f"{self.username}:{self.password}".encode("utf-8")
        auth_header = base64.b64encode(raw).decode("utf-8")

        headers = {"Authorization": f"Basic {auth_header}"}
        resp = self._request("POST", url, headers=headers)

        token = resp.headers.get("token")
        if not token:
            raise RuntimeError("Authentication succeeded but no token in response headers")

        self.token = token
        logger.info("Successfully authenticated and obtained token")
        return token

    def headers(self) -> Dict[str, str]:
        """Common headers for all requests after authentication."""
        if not self.token:
            raise ValueError("Token not available. Authenticate first.")
        return {"token": self.token, "Content-Type": "application/json"}


# ----------------------------
# DATE HELPER
# ----------------------------
def format_effective_date(date_str: str) -> str:
    """Convert user-entered date (YYYY-MM-DD) into required format."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y-%m-%dT00:00:00.000-05:00")
