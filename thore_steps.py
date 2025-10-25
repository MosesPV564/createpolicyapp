# file: thore_steps.py
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any

import requests
from thore_client import ThoreAPIClient, format_effective_date

logger = logging.getLogger(__name__)

# ----------------------------
# Step 1 – Create Policy
# ----------------------------

def step1_create_policy(client: ThoreAPIClient, user_input: Dict[str, Any]) -> int:
    """
    Create a new policy term transaction.
    Returns the created instance ID (integer).
    """

    url = (
        f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX"
        "?parentTypeGroup=Organization.Agencies&parentId=49&productName=HOATX"
    )

    body = {
        "id": 0,
        "entityType": "PolicyTermTransaction.HOATX",
        "versionNumber": None,
        "data": {
            "effectiveDate": format_effective_date(user_input["effectiveDate"]),
            "interests": [
                {
                    "type": "NamedInsured",
                    "subType": "Primary",
                    "characteristics": {
                        "name": {
                            "type": "Individual",
                            "legalName": None,
                            "legalStructure": None,
                            "prefix": None,
                            "firstName": user_input["firstName"],
                            "middleName": None,
                            "lastName": user_input["lastName"],
                            "suffix": None,
                        }
                    },
                }
            ],
            "termLength": 525600,
        },
    }

    headers = client.headers()
    resp = client._request("POST", url, headers=headers, json=body)

    # Wait for the POST to complete (expect 201)
    while resp.status_code != 201:
        logger.info(f"Waiting for policy creation... status {resp.status_code}")
        time.sleep(3)

    location = resp.headers.get("Location") or resp.headers.get("location")
    if not location:
        raise RuntimeError("No Location header returned from policy creation.")

    logger.info(f"Location header: {location}")
    match = re.search(r"/(\d+)$", location)
    if not match:
        raise RuntimeError("Could not parse instance ID from Location header.")
    instance_id = int(match.group(1))

    logger.info(f"✅ Step 1 completed: Policy created with instanceId={instance_id}")
    return instance_id


# ----------------------------
# Step 1.1 – Get Policy Details
# ----------------------------

def step1_1_get_policy_details(client: ThoreAPIClient, instance_id: int) -> Dict[str, Any]:
    """
    Fetch policy details and extract key fields.
    Returns dict with resourceIdentifier, policyNumber, transactionNumber.
    """

    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}"
    headers = client.headers()

    resp = client._request("GET", url, headers=headers)

    while resp.status_code != 200:
        logger.info(f"Waiting for policy details... status {resp.status_code}")
        time.sleep(3)
        resp = client._request("GET", url, headers=headers)

    data = resp.json()
    resource_identifier = data.get("resourceIdentifier")
    policy_number = data.get("data", {}).get("policyNumber")
    transaction_number = data.get("data", {}).get("transactionNumber")

    result = {
        "instanceId": instance_id,
        "resourceIdentifier": resource_identifier,
        "policyNumber": policy_number,
        "transactionNumber": transaction_number,
    }

    logger.info(f"✅ Step 1.1 completed: {json.dumps(result, indent=2)}")
    return result
