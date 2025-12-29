# Technical Stack & Reasoning

This document explains the specific technologies, models, and libraries chosen for the Secure RAG PoC and the reasoning behind them.

## 1. Core Infrastructure

### **FastAPI** (Backend Framework)
*   **Why:** High performance (async support), automatic OpenAPI documentation (Swagger UI), and strict type validation with Pydantic. It is the industry standard for Python AI microservices.

### **LocalStack** (Cloud Simulation)
*   **Why:** Allows us to simulate AWS services (S3, KMS) locally without incurring costs or needing an internet connection. It provides a realistic "cloud-native" development environment.

### **Qdrant** (Vector Database)
*   **Why:**
    *   **Rust-based:** Extremely fast and memory-efficient.
    *   **Collection-based Architecture:** Supports the strict isolation pattern we need (one collection per tenant).
    *   **Developer Friendly:** Easy to run via Docker and has a great Python client.

---

## 2. Machine Learning Models

### **A. Named Entity Recognition (NER)**
*   **Model:** `dslim/bert-base-NER`
*   **Source:** HuggingFace Transformers
*   **Reasoning:**
    *   This is a fine-tuned version of BERT specifically for NER.
    *   It is robust and widely used for detecting standard entities (Person, Organization, Location).
    *   **Why not a larger LLM?** BERT is much faster and lighter than using GPT-4 for simple extraction tasks, reducing latency in the ingestion pipeline.

### **B. Text Embeddings**
*   **Model:** `sentence-transformers/all-MiniLM-L6-v2`
*   **Source:** HuggingFace / SentenceTransformers
*   **Reasoning:**
    *   **Speed vs. Quality:** It offers one of the best trade-offs between speed and semantic accuracy.
    *   **Size:** Very small (~80MB), making it perfect for a local PoC running on a CPU.
    *   **Dimensions:** Outputs 384-dimensional vectors, which is efficient for storage and search.

### **C. Generative LLM (The "G" in RAG)**
*   **Model:** `google/flan-t5-small`
*   **Source:** HuggingFace Transformers
*   **Reasoning:**
    *   **Local Execution:** We wanted a model that runs entirely locally to ensure no data leaves the secure environment (Zero-Trust).
    *   **Task Suitability:** FLAN-T5 is fine-tuned for instruction following and Q&A tasks.
    *   **Resource Efficiency:** The "small" variant runs easily on standard CPUs without needing a GPU, making the PoC accessible to everyone.

### **D. Anomaly Detection**
*   **Model:** `Isolation Forest`
*   **Library:** `scikit-learn`
*   **Reasoning:**
    *   **Unsupervised:** We don't need labeled "attack data" to train it. It learns what "normal" looks like on the fly.
    *   **High-Dimensional Data:** It works reasonably well with high-dimensional data (like our 384-dim embeddings) to detect outliers.
    *   **Efficiency:** Very fast to train and predict, adding negligible latency to the query pipeline.

---

## 3. Security Components

### **AWS KMS (Key Management Service)**
*   **Why:** Implements **Envelope Encryption**.
*   **Reasoning:**
    *   We don't want to manage encryption keys in our application code (hardcoded keys are a security sin).
    *   KMS handles the lifecycle, rotation, and access control of the master keys.
    *   Using unique keys per tenant ensures **Cryptographic Erasure**—if we delete a tenant's key in KMS, all their data in S3 and Qdrant becomes instantly unreadable garbage.

### **AWS S3 (Simple Storage Service)**
*   **Why:** Scalable object storage for the encrypted document blobs.
*   **Reasoning:** Vector databases are expensive storage for raw text. It is best practice to store only vectors in the DB and keep the actual content (encrypted) in cheap object storage like S3.
