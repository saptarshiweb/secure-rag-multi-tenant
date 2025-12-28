# Secure Multi-Tenant RAG PoC

This project demonstrates a "Defense-in-Depth" architecture for preventing data leakage in cloud-hosted RAG systems.

## Architecture

1.  **Identity:** JWT-based tenant isolation.
2.  **Vector DB:** Qdrant with per-tenant collections.
3.  **Storage:** AWS S3 (LocalStack) with Envelope Encryption (AWS KMS).
4.  **ML Defense:** PII Redaction (BERT) and Anomaly Detection (Isolation Forest).

## Setup

1.  **Start Infrastructure:**
    ```bash
    docker-compose up -d
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run API:**
    ```bash
    uvicorn app.main:app --reload
    ```

4.  **Run Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```
