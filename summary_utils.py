# file: summary_utils.py
import json
import os
import logging
from typing import Dict, Any, List
from thore_client import SUMMARY_FILE

logger = logging.getLogger(__name__)

def append_summary(entry: Dict[str, Any]) -> None:
    """Append one policy's result to the JSON summary file."""
    try:
        data: List[Dict[str, Any]] = []
        if SUMMARY_FILE and os.path.exists(SUMMARY_FILE):
            with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f) or []
                except json.JSONDecodeError:
                    data = []
        data.append(entry)
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Summary updated for policy {entry.get('policyNumber')}")
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")


def load_summary() -> List[Dict[str, Any]]:
    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
