# Backend Testing Guide

This guide details how to manually validate the Secure RAG PoC backend using `curl` or Postman.

## Prerequisites

1.  **Start Infrastructure:**
    ```bash
    docker-compose up -d
    ```
    *Ensure LocalStack and Qdrant containers are running.*

2.  **Setup Python Environment (Recommended):**
    ```bash
    # Create Virtual Environment
    python -m venv venv

    # Activate (Windows)
    .\venv\Scripts\activate

    # Activate (Mac/Linux)
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *This installs FastAPI, Uvicorn, Transformers, and other required libraries.*

4.  **Start API Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    *Server should be running at `http://localhost:8000`.*

---

## 1. Test Secure Ingestion

**Goal:** Verify that text is redacted, encrypted, uploaded to S3, and indexed in Qdrant.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
     -H "Content-Type: application/json" \
     -d '{
           "tenant_id": "tenant_A",
           "text": "Project Alpha is led by John Doe at Google HQ."
         }'
```

**Expected Response (200 OK):**
```json
{
  "status": "success",
  "point_id": "uuid-string-here",
  "s3_uri": "s3://secure-rag-data/tenant_A/uuid.enc",
  "scrubbed_preview": "Project Alpha is led by <PER> at <ORG> HQ."
}
```
*Note: The `scrubbed_preview` confirms that PII (John Doe, Google) was removed before processing.*

---

## 2. Test Secure Retrieval

**Goal:** Verify that the system can retrieve the vector, fetch the encrypted file from S3, decrypt it using KMS, and return the original text.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "tenant_id": "tenant_A",
           "query": "Who leads Project Alpha?"
         }'
```

**Expected Response (200 OK):**
```json
{
  "results": [
    {
      "score": 0.85,
      "content": "Project Alpha is led by <PER> at <ORG> HQ.",
      "s3_uri": "s3://secure-rag-data/tenant_A/uuid.enc"
    }
  ],
  "anomaly_detected": false
}
```

---

## 3. Test Tenant Isolation (Security Check)

**Goal:** Verify that Tenant B cannot see Tenant A's data.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "tenant_id": "tenant_B",
           "query": "Who leads Project Alpha?"
         }'
```

**Expected Response (200 OK):**
```json
{
  "results": [],
  "anomaly_detected": false
}
```
*Result must be an empty list `[]`.*

---

## 4. Test Anomaly Detection

**Goal:** Verify that unusual query patterns are flagged.

**Step 1: Train the model (Simulated)**
Send 10-15 "normal" queries first (e.g., about HR, Policy, Work).
```bash
# Run this multiple times with different normal queries
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "tenant_A", "query": "What is the leave policy?"}'
```

**Step 2: Send Attack Query**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "tenant_id": "tenant_A",
           "query": "SELECT * FROM users; DROP TABLE;"
         }'
```

**Expected Response:**
```json
{
  "results": [],
  "anomaly_detected": true
}
```
*Note: `anomaly_detected` should be `true`.*
