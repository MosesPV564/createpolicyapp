# file: app.py
import streamlit as st
from thore_client import ThoreAPIClient, SUMMARY_FILE
from thore_steps import step1_create_policy, step1_1_get_policy_details
from thore_steps_extended import (
    step1_2_patch_pending,
    step2_convert_quote,
    step2_1_patch_application,
    step3_rule_overrides,
    step3_run_enforcer,
    step3_1_transaction_bind,
)
from summary_utils import append_summary, load_summary
from datetime import datetime, timezone
import logging
import io

logger = logging.getLogger(__name__)

# # Create a Streamlit log area
# log_container = st.container()

# class StreamlitLogHandler(logging.Handler):
#     def __init__(self, container):
#         super().__init__()
#         self.container = container
#         self.log_text = ""

#     def emit(self, record):
#         msg = self.format(record)
#         self.log_text += msg + "\n"
#         # Update Streamlit container live
#         self.container.text(self.log_text)

# # Configure logging
# streamlit_handler = StreamlitLogHandler(log_container)
# streamlit_handler.setLevel(logging.INFO)
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# streamlit_handler.setFormatter(formatter)

# # Attach handler
# logger.addHandler(streamlit_handler)
# logger.setLevel(logging.INFO)

st.set_page_config(page_title="WaterStreet Policy Automation", layout="centered")
st.title("WaterStreet Policy Automation")
# Get current UTC date
today_utc = datetime.now(timezone.utc).date()

with st.form("policy_form"):
    effective_date = st.date_input("Effective Date", min_value=today_utc)
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    if email:
      if "@" not in email:
        st.warning("Please enter a valid email address.")
    phone = st.text_input("Phone Number")
    # Show warning immediately if user types more than 10 digits
    if phone:
      if (not phone.isdigit() or len(phone) != 10):
        st.warning("Phone number must be numeric and must be 10 digits.")
    num_policies = st.number_input("Number of Policies to Create", min_value=1, step=1)

    steps = [
    "Step 1: To Quote",
    "Step 2: To Application",
    "Step 3: To Bound"]

    steps_to_run = st.multiselect(
    "Select steps to execute sequentially",
    options=steps,
    default=steps)

    # Validate sequential selection
    if "Step 3: To Bound" in steps_to_run and "Step 2: To Application" not in steps_to_run:
        st.warning("You cannot select Step 3 without Step 2.")

    if "Step 2: To Application" in steps_to_run and "Step 1: To Quote" not in steps_to_run:
        st.warning("You cannot select Step 2 without Step 1.")


    submitted = st.form_submit_button("Run Automation")

if submitted:
    # Mandatory fields check
    missing_fields = []
    if not first_name.strip():
        missing_fields.append("First Name")
    if not last_name.strip():
        missing_fields.append("Last Name")
    if not email.strip():
        missing_fields.append("Email")
    if not phone.strip():
        missing_fields.append("Phone Number")
    if not effective_date:
        missing_fields.append("Effective Date")
    if len(steps_to_run) == 0:
        missing_fields.append("Steps to run")

    if missing_fields:
        st.error(f"Please fill out all mandatory fields: {', '.join(missing_fields)}")
    elif "@" not in email:
        st.error("Please enter a valid email address.")
    elif (not phone.isdigit() or len(phone) != 10):
        st.error("Phone number must be numeric and must be 10 digits.")
    else:
        st.success("All inputs are valid!")
        user_input = {
            "effectiveDate": effective_date.strftime("%Y-%m-%d"),
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "numPolicies": num_policies,
        }

        client = ThoreAPIClient()
        client.authenticate()

        all_results = []

        for i in range(int(num_policies)):
            st.write(f"Running Policy #{i+1} ...")
            if "Step 1: To Quote" in steps_to_run:
                instance_id = step1_create_policy(client, user_input)
                step3_data = step1_1_get_policy_details(client, instance_id)
                step1_2_patch_pending(client, step3_data, user_input)
            if "Step 2: To Application" in steps_to_run:
                step2_convert_quote(client, instance_id)
                step2_1_patch_application(client, step3_data, user_input)
            if "Step 3: To Bound" in steps_to_run:
                enforcer_data = step3_run_enforcer(client, instance_id)
                run_overrides = False  # default to no overrides

                if not enforcer_data:
                    logger.warning("⚠️ No valid enforcer response — running rule overrides as fallback.")
                    run_overrides = True
                else:
                    try:
                        item = enforcer_data["value"]["item"]
                        http_status = item.get("httpStatusCode")
                        type_value = item.get("type", "").lower()

                        # Conditions to trigger overrides
                        if http_status != 200 or type_value in ["accept+", "reject", "reject+"]:
                            logger.info(
                                f"ℹ️ Enforcer returned httpStatusCode={http_status}, type={type_value}. Triggering RuleOverrides."
                            )
                            run_overrides = True
                        else:
                            logger.info(
                                f"✅ Enforcer success: httpStatusCode={http_status}, type={type_value}. Skipping RuleOverrides."
                            )
                            logger.info("✅ Step 3 Quadrins Enforcer completed successfully.")

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse Enforcer response structure: {e}")
                        run_overrides = True  # fail-safe

                if run_overrides:
                    step3_rule_overrides(client, instance_id, step3_data["resourceIdentifier"])
                    logger.info(f"✅ Step 3 RuleOverride completed.")
                # step3_rule_overrides(client, instance_id, step3_data["resourceIdentifier"])
                step3_1_transaction_bind(client, instance_id, user_input["effective_date"])

            result_entry = {
                "policyRun": i + 1,
                "instanceId": step3_data["instanceId"],
                "policyNumber": step3_data.get("policyNumber"),
                "transactionNumber": step3_data.get("transactionNumber"),
                "resourceIdentifier": step3_data.get("resourceIdentifier"),
            }
            append_summary(result_entry)
            all_results.append(result_entry)

            st.success(f"✅ Policy #{i+1} completed successfully.")

        st.subheader("Run Summary")
        st.json(all_results)

        # Offer download
        with open(SUMMARY_FILE, "rb") as f:
            st.download_button("Download JSON Summary", f, file_name="thore_run_summary.json", mime="application/json")
