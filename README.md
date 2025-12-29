# Secure Multi-Tenant RAG PoC

This project demonstrates a **"Defense-in-Depth" architecture** for preventing data leakage in cloud-hosted Retrieval-Augmented Generation (RAG) systems. It integrates Cloud-Native Security (AWS KMS/S3 via LocalStack) with Machine Learning Defenses (NER & Anomaly Detection).

##  Architecture

1.  **Intelligent Pre-processing:** PII Redaction using BERT-NER.
2.  **Vector Isolation:** Qdrant with dedicated collections per tenant.
3.  **Cloud-Native Encryption:** Envelope Encryption using AWS KMS and S3 (simulated via LocalStack).
4.  **Runtime Defense:** Anomaly Detection using Isolation Forest to detect scraping attacks.

---

##  Getting Started

### 1. Prerequisites
*   **Docker Desktop** (must be running)
*   **Python 3.10+**
*   **Git**

### 2. Clone & Setup Environment

First, navigate to the project directory:
```bash
cd secure_rag_poc
```

#### Create a Virtual Environment (Recommended)

It is highly recommended to use a virtual environment to manage dependencies.

**Windows (PowerShell):**
```powershell
# Create the venv
python -m venv venv

# Activate the venv
.\venv\Scripts\activate
```

**Mac / Linux:**
```bash
# Create the venv
python3 -m venv venv

# Activate the venv
source venv/bin/activate
```

*You should see `(venv)` appear at the start of your terminal prompt.*

### 3. Install Dependencies

With your virtual environment activated, install the required Python packages:

```bash
pip install -r requirements.txt
```

---

##  Running the Project

You will need **three** separate terminal windows (or tabs) to run the full stack.

### Terminal 1: Infrastructure (Docker)
Start the LocalStack (AWS Simulator) and Qdrant (Vector DB) containers.

```bash
docker-compose up -d
```
*Wait a few moments for the containers to fully initialize.*

### Terminal 2: Backend API
Activate your venv and start the FastAPI server.

```bash
# Windows
.\venv\Scripts\activate
uvicorn app.main:app --reload

# Mac/Linux
source venv/bin/activate
uvicorn app.main:app --reload
```
*The API will be available at `http://localhost:8000`.*

### Terminal 3: Frontend Dashboard
Activate your venv and launch the Streamlit dashboard.

```bash
# Windows
.\venv\Scripts\activate
streamlit run dashboard.py

# Mac/Linux
source venv/bin/activate
streamlit run dashboard.py
```
*The dashboard should automatically open in your browser at `http://localhost:8501`.*

---

##  How to Use the Dashboard

The dashboard has three modes accessible via the Sidebar:

1.  **Honest Tenant View:**
    *   **Register/Select Identity:** Create a new tenant (e.g., `tenant_A`) or select an existing one.
    *   **Ingest:** Upload a document. You will see how it is redacted (PII removed) and encrypted before storage.
    *   **Query:** Ask questions. The system uses an LLM to generate answers based *only* on that tenant's data.

2.  **Hacker View:**
    *   **Attacker:** Select who you are pretending to be (e.g., `tenant_B`).
    *   **Target:** Select who you want to steal from (e.g., `tenant_A`).
    *   **Attack:** Try to query the victim's data. The system should return **0 results** due to vector isolation and encryption keys.

3.  **ML Watchdog:**
    *   Monitor the system for anomalies.
    *   If you spam queries or use SQL injection patterns in the other views, you will see alerts appear here.

---

##  Stopping the Project

To stop the infrastructure and clean up:

```bash
# Stop containers
docker-compose down

# Deactivate venv
deactivate
```

---

## Troubleshooting

### Common Issue: "NoSuchKey" Error after Restarting Docker

If you restart the Docker containers and encounter an error like:
`An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.`

**Why this happens:**
This is caused by a data synchronization mismatch between the services:
1.  **Qdrant (Vector DB)** is configured to persist data in the `./qdrant_data` folder. It "remembers" the documents you uploaded previously.
2.  **LocalStack (S3)** is configured to be ephemeral. It starts with an empty bucket every time you restart the container.
3.  **The Conflict:** Qdrant finds the document metadata and tells the app to fetch the file from S3, but S3 is empty, resulting in a `NoSuchKey` error.

**How to fix it:**
You need to reset the environment so both services start fresh.

1.  Stop the containers:
    ```bash
    docker-compose down
    ```

2.  **Delete the `qdrant_data` folder** in your project directory. This clears the vector database.

3.  Restart the containers:
    ```bash
    docker-compose up -d
    ```

4.  Re-ingest your documents via the dashboard.

