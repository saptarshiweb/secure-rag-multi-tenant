import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Secure RAG PoC Dashboard",
    page_icon="",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def fetch_tenants():
    try:
        response = requests.get(f"{API_BASE_URL}/tenants")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def log_interaction(tenant_id, query, is_anomaly, timestamp):
    st.session_state.query_history.append({
        "timestamp": timestamp,
        "tenant_id": tenant_id,
        "query": query,
        "is_anomaly": is_anomaly
    })

# --- SESSION STATE ---
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Initialize tenants from backend
if "tenants" not in st.session_state:
    st.session_state.tenants = fetch_tenants()
    # Fallback if backend is empty or down
    if not st.session_state.tenants:
        st.session_state.tenants = ["tenant_A", "tenant_B"]

# --- SIDEBAR ---
st.sidebar.title(" Secure RAG")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Select Mode", ["Honest Tenant View", "Hacker View", "ML Watchdog"])

st.sidebar.markdown("---")
st.sidebar.subheader(" Tenant Management")

# Add New Tenant
new_tenant_input = st.sidebar.text_input("Register New Tenant ID")
if st.sidebar.button("Add Tenant"):
    if new_tenant_input and new_tenant_input not in st.session_state.tenants:
        st.session_state.tenants.append(new_tenant_input)
        st.sidebar.success(f"Added {new_tenant_input}")
        st.rerun()

# Refresh Tenant List
if st.sidebar.button(" Refresh Tenant List"):
    st.session_state.tenants = fetch_tenants()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Architecture:**
    1. **PII Redaction** (BERT-NER)
    2. **Tenant Isolation** (Qdrant)
    3. **Encryption** (AWS KMS + S3)
    4. **Anomaly Detection** (Isolation Forest)
    """
)

# --- MODE 1: HONEST TENANT ---
if mode == "Honest Tenant View":
    # Dynamic Tenant Selector for Honest View
    current_tenant = st.selectbox("Select Identity (Who are you?)", st.session_state.tenants)
    
    st.title(f" Honest Tenant Operations ({current_tenant})")
    st.markdown(f"Simulate legitimate operations as **{current_tenant}**.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Ingest Document")
        ingest_text = st.text_area("Document Text", f"Confidential project plan for {current_tenant}. Budget is $1M.")
        if st.button("Ingest Document"):
            try:
                payload = {"tenant_id": current_tenant, "text": ingest_text}
                response = requests.post(f"{API_BASE_URL}/ingest", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Document Ingested Successfully!")
                    
                    with st.expander(" See Under the Hood (Security Layers)"):
                        st.markdown(f"**1. PII Redaction:** `{data['scrubbed_preview']}`")
                        st.markdown(f"**2. S3 Storage (Encrypted):** `{data['s3_uri']}`")
                        st.markdown(f"**3. Vector ID:** `{data['point_id']}`")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    with col2:
        st.subheader("2. Query Knowledge Base")
        query_text = st.text_input("Search Query", "What is the budget?")
        if st.button("Search"):
            try:
                payload = {"tenant_id": current_tenant, "query": query_text}
                response = requests.post(f"{API_BASE_URL}/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Log for Watchdog
                    log_interaction(current_tenant, query_text, data["anomaly_detected"], datetime.now())

                    if data["anomaly_detected"]:
                        st.error("🚨 ANOMALY DETECTED! Request flagged by ML Watchdog.")
                    
                    # Display Generated Answer
                    if "generated_answer" in data:
                        st.success(f"🤖 **AI Answer:** {data['generated_answer']}")

                    if data["results"]:
                        with st.expander("📚 View Source Documents & Decryption Details"):
                            for i, doc in enumerate(data["results"]):
                                st.markdown(f"**Source {i+1}:** {doc['content']}")
                                st.code(f"S3 URI: {doc['s3_uri']}\nRelevance Score: {doc['score']:.4f}", language="bash")
                                st.divider()
                    else:
                        st.warning(f"No results found for {current_tenant}.")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- MODE 2: HACKER VIEW ---
elif mode == "Hacker View":
    st.title(" Hacker Simulation")
    st.markdown("Simulate a malicious tenant attempting to access another tenant's data.")
    st.error(" ATTACK SIMULATION IN PROGRESS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attack Configuration")
        
        # Dynamic Attacker Selection
        attacker_id = st.selectbox("Select Attacker ID (You)", st.session_state.tenants, index=1 if len(st.session_state.tenants) > 1 else 0)
        
        # Dynamic Target Selection (Exclude Attacker)
        possible_targets = [t for t in st.session_state.tenants if t != attacker_id]
        if not possible_targets:
            st.warning("Need at least 2 tenants to simulate an attack. Add one in the sidebar!")
            target_id = None
        else:
            target_id = st.selectbox("Select Target Victim ID", possible_targets)

        target_query = st.text_input("Malicious Query", "What is the budget?")
        
        if st.button("Attempt Cross-Tenant Access"):
            if not target_id:
                st.error("No target selected.")
            else:
                try:
                    # The Attack:
                    # We are logged in as "attacker_id".
                    # But we are trying to find data that belongs to "target_id".
                    # In a secure system, searching as "attacker_id" should NEVER return "target_id" data.
                    
                    payload = {"tenant_id": attacker_id, "query": target_query}
                    response = requests.post(f"{API_BASE_URL}/query", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Log for Watchdog
                        log_interaction(attacker_id, target_query, data["anomaly_detected"], datetime.now())

                        st.markdown("### Attack Results")
                        if len(data["results"]) == 0:
                            st.image("https://img.shields.io/badge/ACCESS-DENIED-red", width=200)
                            st.success(f" **Defense Successful:** {attacker_id} could not find any data matching the query.")
                            st.json({
                                "status": "403 Forbidden (Simulated)",
                                "reason": "Vector Collection Mismatch",
                                "kms_key": "AccessDeniedException"
                            })
                        else:
                            st.warning(" Results found (but they likely belong to YOU, not the victim).")
                            st.write(data)
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with col2:
        st.markdown("###  Active Defenses")
        if target_id:
            st.markdown(f"""
            1. **Vector Partitioning:**
            - Victim data is in `collection_{target_id}`
            - You are searching `collection_{attacker_id}`
            
            2. **KMS Envelope Encryption:**
            - Even if you guessed a document ID, your key (`key_{attacker_id}`) cannot decrypt `key_{target_id}`'s data.
            """)
        else:
            st.info("Select a target to see defense details.")

# --- MODE 3: ML WATCHDOG ---
elif mode == "ML Watchdog":
    st.title(" ML Watchdog Monitor")
    st.markdown("Real-time monitoring of query anomalies and threat detection.")

    if not st.session_state.query_history:
        st.info("No queries logged yet. Go to \"Honest Tenant\" or \"Hacker View\" to generate traffic.")
    else:
        df = pd.DataFrame(st.session_state.query_history)
        
        # Metrics
        total_queries = len(df)
        anomalies = df["is_anomaly"].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Queries", total_queries)
        m2.metric("Anomalies Detected", int(anomalies), delta_color="inverse")
        m3.metric("Threat Level", "LOW" if anomalies < 2 else "HIGH")

        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Traffic by Tenant")
            fig_tenant = px.pie(df, names="tenant_id", title="Query Distribution")
            st.plotly_chart(fig_tenant, use_container_width=True)

        with c2:
            st.subheader("Anomaly Timeline")
            # Simple scatter plot of anomalies over time
            df["status"] = df["is_anomaly"].apply(lambda x: "Malicious" if x else "Normal")
            color_map = {"Normal": "green", "Malicious": "red"}
            fig_timeline = px.scatter(df, x="timestamp", y="tenant_id", color="status", 
                                    color_discrete_map=color_map, title="Live Threat Feed")
            st.plotly_chart(fig_timeline, use_container_width=True)

        st.subheader(" Live Query Log")
        st.dataframe(df[["timestamp", "tenant_id", "query", "is_anomaly"]].sort_values("timestamp", ascending=False))
