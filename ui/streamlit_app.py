import streamlit as st
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="Agentic AI Loan Approval",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Agentic AI Intelligent Loan Approval System")
st.markdown(
    "Submit your loan application and get an instant AI-powered decision with full explainability."
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Loan Application Form")

    applicant_id = st.text_input(
        "Applicant ID",
        value="APP001",
        help="Unique identifier for the applicant",
    )

    age = st.slider("Age", min_value=18, max_value=80, value=35)

    income = st.number_input(
        "Annual Income ($)",
        min_value=10000,
        max_value=1000000,
        value=60000,
        step=5000,
    )

    employment_type = st.selectbox(
        "Employment Type",
        ["salaried", "self_employed", "business"],
    )

    credit_score = st.slider(
        "Credit Score",
        min_value=300,
        max_value=850,
        value=720,
        help="FICO credit score",
    )

    loan_amount = st.number_input(
        "Loan Amount ($)",
        min_value=5000,
        max_value=1000000,
        value=100000,
        step=10000,
    )

    tenure_months = st.number_input(
        "Loan Tenure (Months)",
        min_value=12,
        max_value=360,
        value=60,
        step=12,
    )

    existing_liabilities = st.number_input(
        "Existing Liabilities ($)",
        min_value=0,
        max_value=500000,
        value=20000,
        step=5000,
    )

    location = st.text_input(
        "Location",
        value="New York",
    )

    submit_button = st.button("📤 Submit Application", use_container_width=True)

with col2:
    st.subheader("📊 Decision Output")

    if submit_button:
        with st.spinner("Processing your application..."):
            try:
                payload = {
                    "applicant_id": applicant_id,
                    "applicant_profile": {
                        "age": age,
                        "income": income,
                        "employment_type": employment_type,
                    },
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "tenure_months": tenure_months,
                    "existing_liabilities": existing_liabilities,
                    "location": location,
                }

                response = requests.post(f"{API_URL}/loan/submit", json=payload)

                if response.status_code == 200:
                    submit_response = response.json()
                    application_id = submit_response["application_id"]

                    import time
                    for _ in range(30):
                        status_response = requests.get(
                            f"{API_URL}/loan/status/{application_id}"
                        )

                        if status_response.json()["status"] == "completed":
                            decision_response = requests.get(
                                f"{API_URL}/loan/decision/{application_id}"
                            )

                            if decision_response.status_code == 200:
                                decision = decision_response.json()

                                classification = decision["classification"]
                                if classification == "APPROVED":
                                    color = "green"
                                    icon = "✅"
                                elif classification == "REJECTED":
                                    color = "red"
                                    icon = "❌"
                                else:
                                    color = "orange"
                                    icon = "⚠️"

                                st.markdown(
                                    f"<h2 style='color: {color};'>{icon} {classification}</h2>",
                                    unsafe_allow_html=True,
                                )

                                col_metrics = st.columns(3)
                                with col_metrics[0]:
                                    st.metric(
                                        "Risk Score",
                                        f"{decision['risk_score']:.1f}/100",
                                    )

                                with col_metrics[1]:
                                    st.metric(
                                        "Confidence",
                                        f"{decision['confidence_level']*100:.1f}%",
                                    )

                                with col_metrics[2]:
                                    st.metric("Case ID", decision["case_id"])

                                st.subheader("📌 Decision Factors")
                                for factor in decision["decision_factors"]:
                                    st.write(f"• {factor}")

                                st.subheader("📖 Explanation")
                                st.info(decision["explanation"])

                                if decision.get("llm_explanation"):
                                    st.subheader("🤖 AI-Powered Analysis")
                                    st.markdown(decision["llm_explanation"])

                                if decision.get("execution_trace"):
                                    with st.expander("🔍 Execution Trace (Debug Info)"):
                                        for trace in decision["execution_trace"]:
                                            st.write(
                                                f"**{trace['node']}** ({trace['status']}) @ {trace['timestamp']}"
                                            )
                                            for key, val in trace["details"].items():
                                                st.write(f"  - {key}: {val}")

                                break
                        else:
                            time.sleep(0.5)

                else:
                    st.error(f"Error submitting application: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to API server. Please ensure the FastAPI backend is running on http://localhost:8000"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; margin-top: 20px;'>"
    "Powered by Agentic AI with Claude Sonnet 4.6 | "
    "Architecture: LangGraph + FastAPI + Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
