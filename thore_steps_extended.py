import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from thore_client import ThoreAPIClient
import email.utils
import requests

logger = logging.getLogger(__name__)

def _utc_now_iso():
    """Return current UTC datetime in ISO format with milliseconds and -05:00 offset."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "-05:00"


# ----------------------------
# Step 1.2 – PATCH Pending
# ----------------------------

def step1_2_patch_pending(client: ThoreAPIClient, step3_data: Dict[str, Any], user_input: Dict[str, Any]) -> None:
    """PATCH policy to Pending status."""
    global shared_data
    shared_data = {}
    
    instance_id = step3_data["instanceId"]
    resource_id = step3_data["resourceIdentifier"]
    policy_no = step3_data["policyNumber"]
    txn_no = step3_data["transactionNumber"]
    effective_date_only = step3_data.get("effectiveDate", user_input["effectiveDate"])
    # effective_date_with_time = f"{effective_date_only}T05:00:00.000-05:00"
    effective_date_with_time = f"{effective_date_only}T06:00:00Z"

    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}"

    patch_body = {
        "id": instance_id,
        "resourceIdentifier": resource_id,
        "versionNumber": 1,
        "data": {
            "policyNumber": policy_no,
            "transactionNumber": txn_no,
            "basedOnTransactionNumber": None,
            "type": "NewBusiness",
            "subType": "Standard",
            "status": "Pending",
            "effectiveDate": effective_date_with_time,
            "keyDates": {
                "quoteDate": _utc_now_iso(),
                "accountingDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00.000-05:00"),
            },
            "interests": [
                {
                    "type": "NamedInsured",
                    "subType": "Primary",
                    "characteristics": {
                        "name": {
                            "type": "Individual",
                            "firstName": user_input["firstName"],
                            "lastName": user_input["lastName"],
                            "displayName": f"{user_input['firstName']} {user_input['lastName']}",
                        },
                        "phones": [{"type": "Mobile", "number": user_input["phone"]}],
                        "emails": [{"address": user_input["email"]}],
                        "addresses": [{"type": "Mailing"}],
                        "hasCompanionPolicy": True,
                        "birthDate": "1980-01-01T00:00:00.000-06:00"
                    },
                }
            ],
            "assets": [
            {
                "type": "Dwelling",
                "characteristics": {
                    "addresses": [
                        {
                            "type": "Physical",
                            "subType": "Primary",
                            "state": "TX",
                            "address": "17426 STRALOCH LN",
                            "city": "RICHMOND",
                            "postalCode": "77407",
                            "county": "FORT BEND",
                        }
                    ],
                    "limits": {
                        "otherStructures": 250,
                        "personalProperty": 0.25,
                        "lossOfUse": 0.1,
                        "personalLiability": 25000,
                        "medicalPaymentsToOthers": 500,
                        "waterDamage": 5000,
                        "additionalWaterDamage": 0,
                        # "unscheduledJewelryWatchesFurs": 500,
                        "unscheduledJewelryWatchesFurs": 3000,
                        # "animalLiability": 0,
                        "animalLiability": 25000,
                        "dwelling": 740000,
                    },
                    "modifier": {
                        "hasPersonalPropertyReplacementCost": True,
                        "isRoofExcluded": True,
                        "hasGlass": True,
                        "hasActualCashValueLossSettlement": True,
                        "hasNonStructuralHailLoss": True,
                        "isPoolExcluded": True,
                        # "isRoofExcluded": False,
                        # "hasGlass": False,
                        # "hasActualCashValueLossSettlement": False,
                        # "hasNonStructuralHailLoss": False,
                        # "isPoolExcluded": False,
                        "hasOtherStructuresExclusion": False,
                        "hasContentsExclusion": False,
                        "hasRateAdjustment": False,
                    },
                    "deductibles": {
                        "aop": 0.01,
                        "windHail": 0.02,
                    },
                    "building": {
                        "construction": {
                            "burglarAlarmType": "None",
                            "fireAlarmType": "None",
                            "isRoofStandardConstructionCompliant": False,
                            "constructedDate": "2018-01-01T00:00:00.000-06:00",
                            "roofInstallationDate": "2018-01-01T00:00:00.000-06:00",
                            "type": "BrickVeneer",
                            "squareFootage": 3748,
                            "numberOfFloors": "1.5Story",
                            "hasFireExtinguisher": False,
                            "groundLevelWaterAppliances": False,
                            "steepRoof": False,
                        },
                        "usage": {
                            "occupancy": "OwnerPrimary",
                            "numberOfResidents": 2,
                        },
                    },
                    "geolocation": {
                        "hasCommunitySecurity": False,
                        "isFireStationWithin": "UnderEqualTo5Miles",
                        "fireProtectionClass": "2",
                        "isFireHydrantWithin": "UnderEqualTo1000FT",
                        "fireStationName": "NORTH EAST FORT BEND FS 2",
                        "latitude": "29.646506",
                        "longitude": "-95.689794",
                    },
                    "property": {
                        "hasHadPriorInsuranceOnProperty": False,
                        "hasPoolOnPremises": False,
                        "newPurchaseClosingDate": "2018-11-29T00:00:00.000-06:00",
                    },
                    "displayDescription": "TX",
                },
            }
        ],
        "characteristics": {
            "renewalTerm": 0,
            "isVeriskAPlusRequested": False,
            "veriskLocationData": "29.646506 | -95.689794 | NORTH EAST FORT BEND FS 2 | UnderEqualTo5Miles | 2",
            "veriskLocationAddressInfo": "Verified",
            "veriskLocationTrackingId": "355003f9-b1ef-4703-8ebd-6ceff1d25ffc",
            "isVeriskLocationAccepted": True,
            "veriskLocationOverride": True,
            "quadrINS": {"result": "Unverified"},
            "veriskLocationActualDistanceToCoast": "51.88",
        },
            "termLength": 525600,
        },
        "entityType": "PolicyTermTransaction.HOATX",
        "createDate": _utc_now_iso(),
        "changeDate": _utc_now_iso(),
        "createdById": 9742,
        "changedById": 9742,
    }

    # ... build patch_body
    shared_data.update({
        "quotedate": patch_body["data"]["keyDates"]["quoteDate"],
        "accountingdate": patch_body["data"]["keyDates"]["accountingDate"],
        "createdate": patch_body["createDate"],
    })

    resp = client._request("PATCH", url, headers=client.headers(), json=patch_body)
    while resp.status_code != 204:
        logger.info(f"Waiting for PATCH (Pending)... {resp.status_code}")
        time.sleep(3)
        resp = client._request("PATCH", url, headers=client.headers(), json=patch_body)

    logger.info(f"✅ Step 1.2 completed (Pending updated).")


# ----------------------------
# Step 2 – Convert Quote to Application
# ----------------------------

def step2_convert_quote(client: ThoreAPIClient, instance_id: int):
    global shared_data
    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}/actions/ConvertQuoteToApplication"
    resp = client._request("POST", url, headers=client.headers())
    while resp.status_code != 200:
        logger.info(f"Waiting ConvertQuoteToApplication... {resp.status_code}")
        time.sleep(3)
        resp = client._request("POST", url, headers=client.headers())
    date_header = resp.headers.get("Date")
    if date_header:
        # Parse it into a datetime object
        dt = email.utils.parsedate_to_datetime(date_header)
        # Make sure it's timezone aware in UTC
        dt_utc = dt.astimezone(timezone.utc)
        # Format like your _utc_now_iso() style
        formatted_utc = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "-05:00"
        logger.info("Server Date in UTC format: %s", formatted_utc)
        shared_data.update({
            "convertdate": formatted_utc,
        })
        # return formatted_utc
    else:
        logger.info("Date header not found in response")
        # return None
    logger.info("✅ Step 2 ConvertQuoteToApplication completed.")


# ----------------------------
# Step 2.1 – PATCH Application Status
# ----------------------------

def step2_1_patch_application(client: ThoreAPIClient, step3_data: Dict[str, Any], user_input: Dict[str, Any]):
    global shared_data
    logger.info("Data in shared_data: %s", shared_data)
    instance_id = step3_data["instanceId"]
    resource_id = step3_data["resourceIdentifier"]
    policy_no = step3_data["policyNumber"]
    txn_no = step3_data["transactionNumber"]
    effective_date_only = step3_data.get("effectiveDate", user_input["effectiveDate"])
    # effective_date_with_time = f"{effective_date_only}T05:00:00.000-05:00"
    effective_date_with_time = f"{effective_date_only}T06:00:00Z"

    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}"


    patch_body = {
        "id": instance_id,
        "resourceIdentifier": resource_id,
        "versionNumber": 1,
        "data": {
            "policyNumber": policy_no,
            "transactionNumber": txn_no,
            "basedOnTransactionNumber": None,
            "type": "NewBusiness",
            "subType": "Standard",
            "status": "Application",
            "effectiveDate": effective_date_with_time,
            "keyDates": {
                "quoteDate": shared_data["quotedate"],
                "accountingDate": shared_data["accountingdate"],
                "convertDate": shared_data["convertdate"],
            },
            "interests": [
                {
                    "type": "NamedInsured",
                    "subType": "Primary",
                    "characteristics": {
                        "name": {
                            "type": "Individual",
                            "firstName": user_input["firstName"],
                            "lastName": user_input["lastName"],
                            "displayName": f"{user_input['firstName']} {user_input['lastName']}",
                        },
                        "phones": [{"type": "Mobile", "number": user_input["phone"]}],
                        "emails": [{"address": user_input["email"]}],
                        "addresses": [
                            {
                                "type": "Mailing",
                                "country": "USA",
                                "city": "RICHMOND",
                                "state": "TX",
                                "postalCode": "77407",
                                "address": "17426 STRALOCH LN",
                            }
                        ],
                        "hasCompanionPolicy": True,
                        "hasConvictionArsonFelonyOrFraud": False,
                        "hasCoverageCancelledDeclinedNonRenewed": False,
                        "birthDate": "1980-01-01T00:00:00.000-06:00"
                    },
                }
            ],
            "assets": [
            {
                "type": "Dwelling",
                "characteristics": {
                    "addresses": [
                        {
                            "type": "Physical",
                            "subType": "Primary",
                            "state": "TX",
                            "address": "17426 STRALOCH LN",
                            "city": "RICHMOND",
                            "postalCode": "77407",
                            "county": "FORT BEND",
                        }
                    ],
                    "limits": {
                        "otherStructures": 250,
                        "personalProperty": 0.25,
                        "lossOfUse": 0.1,
                        "personalLiability": 25000,
                        "medicalPaymentsToOthers": 500,
                        "waterDamage": 5000,
                        "additionalWaterDamage": 0,
                        "unscheduledJewelryWatchesFurs": 500,
                        "animalLiability": 0,
                        "dwelling": 740000,
                    },
                    "modifier": {
                        "hasPersonalPropertyReplacementCost": True,
                        "isRoofExcluded": False,
                        "hasGlass": False,
                        "hasActualCashValueLossSettlement": False,
                        "hasNonStructuralHailLoss": False,
                        "isPoolExcluded": False,
                        "hasOtherStructuresExclusion": False,
                        "hasContentsExclusion": False,
                        "hasRateAdjustment": False,
                    },
                    "deductibles": {
                        "aop": 0.01,
                        "windHail": 0.02,
                    },
                    "building": {
                        "construction": {
                            "burglarAlarmType": "None",
                            "fireAlarmType": "None",
                            "isRoofStandardConstructionCompliant": False,
                            "constructedDate": "2018-01-01T00:00:00.000-06:00",
                            "roofInstallationDate": "2018-01-01T00:00:00.000-06:00",
                            "type": "BrickVeneer",
                            "squareFootage": 3748,
                            "numberOfFloors": "1.5Story",
                            "hasFireExtinguisher": False,
                            "groundLevelWaterAppliances": False,
                            "steepRoof": False,
                            "foundation": "ConcreteSlab",
                            "residenceType": "SingleFamilyHome",
                            "plumbingType": "PEX",
                            "electricalType": "CircuitBreakerPanel",
                            "roof": "ShingleComposition30Yr",
                            "hasExistingDamage": False,
                            "anyBarsOnWindows": False,
                            "isUndergoingRenovations": False,

                        },
                        "usage": {
                            "occupancy": "OwnerPrimary",
                            "numberOfResidents": 2,
                            "isOccupancyExpectedWithinNumberOfDays": False,
                        }
                    },
                    "geolocation": {
                        "hasCommunitySecurity": False,
                        "isFireStationWithin": "UnderEqualTo5Miles",
                        "fireProtectionClass": "2",
                        "isFireHydrantWithin": "UnderEqualTo1000FT",
                        "fireStationName": "NORTH EAST FORT BEND FS 2",
                        "latitude": "29.646506",
                        "longitude": "-95.689794",
                    },
                    "property": {
                        "hasHadPriorInsuranceOnProperty": False,
                        "hasPoolOnPremises": False,
                        "newPurchaseClosingDate": "2018-11-29T00:00:00.000-06:00",
                        "isPropertyForSale": False,
                        "hasLargeAcreage": False,
                        "isPropertyOwnedByBusiness": False,
                        "isOverWaterOrAccessibleByBoatOnly": False,
                        "hasLapseInCoverage": False,
                        "hasSolarPanel": False

                    },
                    "displayDescription": "17426 STRALOCH LN RICHMOND, TX 77407",
                },
            }
        ],
        "characteristics": {
            "nonEligibilityAcknowledgement": True,
            "purchaseDate": "2018-11-29T00:00:00.000-06:00",
            "termEffectiveDate": "2025-10-24T00:00:00.000-05:00",
            "renewalTerm": 0,
            "isVeriskAPlusRequested": True,
            "veriskLocationData": "29.646506 | -95.689794 | NORTH EAST FORT BEND FS 2 | UnderEqualTo5Miles | 2",
            "veriskLocationAddressInfo": "Verified",
            "isVeriskLocationAccepted": True,
            "veriskLocationOverride": True,
            "quadrINS": {"result": "Unverified"},
            "veriskLocationActualDistanceToCoast": "51.88",
        },
            "termLength": 525600,
        },
        "entityType": "PolicyTermTransaction.HOATX",
        "createDate": shared_data["createdate"],
        "changeDate": _utc_now_iso(),
        "createdById": 9742,
        "changedById": 9742,
    }

    resp = client._request("PATCH", url, headers=client.headers(), json=patch_body)
    while resp.status_code != 204:
        logger.info(f"Waiting PATCH (Application)... {resp.status_code}")
        time.sleep(3)
        resp = client._request("PATCH", url, headers=client.headers(), json=patch_body)
    logger.info("✅ Step2.1 completed (Application PATCH).")


# ------------------------------------------------
# Steps 3 – Rule Violation Overrides or run quadrins
# ------------------------------------------------

def step3_rule_overrides(client: ThoreAPIClient, instance_id: int, resource_identifier: str):
    base_url = f"{client.base_url}/v1/entityInstanceRuleViolationOverrides"
    payloads = [
        {
            "instanceId": instance_id,
            "ruleDefinitionId": 566,
            "workflowActionDefinitionId": 648,
            "reason": "test",
            "resourceIdentifier": resource_identifier,
        },
        # {
        #     "instanceId": instance_id,
        #     "ruleDefinitionId": 565,
        #     "workflowActionDefinitionId": 648,
        #     "reason": "test",
        #     "resourceIdentifier": resource_identifier,
        # },
        # {
        #     "instanceId": instance_id,
        #     "ruleDefinitionId": 565,
        #     "workflowActionDefinitionId": 668,
        #     "reason": "test",
        #     "resourceIdentifier": resource_identifier,
        # },
    ]
    #both payload with ruleDefinitionId: 565 are only necessary when the enforcer is not used at all

    for i, body in enumerate(payloads, start=1):
        resp = client._request("POST", base_url, headers=client.headers(), json=body)
        while resp.status_code != 201:
            logger.info(f"Waiting RuleOverride number {i}... {resp.status_code}")
            time.sleep(3)
            resp = client._request("POST", base_url, headers=client.headers(), json=body)
        # logger.info(f"✅ Step {i} RuleOverride completed.")
        # logger.info(f"✅ Step 3 RuleOverride completed.")

def step3_run_enforcer(client: ThoreAPIClient, instance_id: int):
    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}/actions/RequestThoreQuadrinsValidation"
    while True:
        resp = client._request("POST", url, headers=client.headers())
        if resp.status_code == 200:
            logger.info("Quadrins Enforcer response returned successfully.")
            try:
                data = resp.json()
                return data  # return parsed response JSON
            except Exception as e:
                logger.warning(f"⚠️ Could not parse enforcer response JSON: {e}")
                return None
        else:
            logger.info(f"Waiting Run_Enforcer... {resp.status_code}")
            time.sleep(3)

        # while resp.status_code != 200:
        #     logger.info(f"Waiting Run_Enforcer... {resp.status_code}")
        #     time.sleep(3)
        #     resp = client._request("POST", url, headers=client.headers())
        # logger.info("✅ Step 3 Quadrins Enforcer completed.")


# ----------------------------
# Step 3.1 – Transaction Bind
# ----------------------------

def step3_1_transaction_bind(client: ThoreAPIClient, instance_id: int):
    url = f"{client.base_url}/v1/entityInstances/PolicyTermTransaction.HOATX/{instance_id}/actions/TransactionBind"


    try:
        logger.info(f"Request: POST {url}")
        resp = client._request("POST", url, headers=client.headers())
        resp.raise_for_status()
        logger.info("✅ Step 3.1 TransactionBind completed successfully.")
        return {"success": True, "message": "Transaction successfully bound."}

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            # Parse the API’s JSON error for a cleaner message
            try:
                error_json = e.response.json()
                description = error_json.get("description", "Action could not be completed.")
                details = (
                    error_json.get("messages", [{}])[0]
                    .get("description", "")
                    .replace("PLEASE IGNORE. INTERNAL.", "")
                    .strip()
                )
                if not details:
                    details = "The transaction is not in a valid state to be bound."
                friendly_message = f"{description} {details}".strip()
            except Exception:
                friendly_message = "The transaction could not be bound due to invalid status or business rule."

            logger.warning(f"⚠️ TransactionBind blocked: {friendly_message}")
            return {"success": False, "message": friendly_message}

        elif e.response.status_code == 500:
            logger.error("❌ Server error during transaction bind.")
            return {"success": False, "message": "A server error occurred. Please try again later."}

        else:
            logger.error(f"❌ Unexpected HTTP error: {e}")
            return {"success": False, "message": "An unexpected error occurred. Please contact support."}

    except Exception as e:
        logger.exception("❌ Unexpected failure in step3_1_transaction_bind")
        return {"success": False, "message": "An unexpected system error occurred."}






    
    # resp = client._request("POST", url, headers=client.headers())
    # while resp.status_code != 200:
    #     logger.info(f"Waiting TransactionBind... {resp.status_code}")
    #     time.sleep(3)
    #     resp = client._request("POST", url, headers=client.headers())
    # logger.info("✅ Step 3.1 TransactionBind completed.")




def step3_2_transaction_issue(client: ThoreAPIClient, instance_id: int):
    url = f"{client.base_url}/v1/entityInstances/PolicyTerms/{instance_id}/actions/IssueNewBusiness"

    try:
        resp = client._request("POST", url, headers=client.headers())
        resp.raise_for_status()  # Raises HTTPError for non-2xx
        logger.info("✅ Step 3.2 TransactionIssue completed successfully.")
        return {"success": True, "message": "Policy issued successfully."}

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            # Extract a user-friendly message if available
            try:
                error_json = e.response.json()
                description = error_json.get("description", "Action could not be completed.")
                rule_message = (
                    error_json.get("messages", [{}])[0]
                    .get("description", "")
                    .replace("PLEASE IGNORE. INTERNAL.", "")
                    .strip()
                )
                friendly_message = f"{description} {rule_message}".strip()
            except Exception:
                friendly_message = "The policy could not be issued due to a validation rule."

            logger.warning(f"⚠️ IssueNewBusiness blocked: {friendly_message}")
            return {"success": False, "message": friendly_message}

        elif e.response.status_code == 500:
            logger.error("❌ Server error during policy issue.")
            return {"success": False, "message": "A server error occurred. Please try again later."}

        else:
            logger.error(f"❌ Unexpected error: {e}")
            return {"success": False, "message": "An unexpected error occurred. Please contact support."}

    except Exception as e:
        logger.exception("❌ Unexpected failure in step3_2_transaction_issue")
        return {"success": False, "message": "An unexpected system error occurred."}


    
    # resp = client._request("POST", url, headers=client.headers())
    # while resp.status_code != 200:
    #     logger.info(f"Waiting TransactionIssue... {resp.status_code}")
    #     time.sleep(3)
    #     resp = client._request("POST", url, headers=client.headers())
    # logger.info("✅ Step 3.2 TransactionIssue completed.")
