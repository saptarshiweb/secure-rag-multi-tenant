# Project Overview: Secure Multi-Tenant RAG

## 1. Introduction
The **Secure RAG PoC** is a reference implementation for building **Zero-Trust Retrieval-Augmented Generation (RAG)** systems in multi-tenant cloud environments. It addresses the critical security challenges that arise when multiple tenants (customers) share the same underlying AI infrastructure.

## 2. The Problem: Risks in Multi-Tenant RAG
As SaaS platforms increasingly adopt GenAI, they face unique security risks that standard RAG pipelines do not address:

### 🚨 1. Cross-Tenant Data Leakage
*   **Risk:** A bug in the application logic or vector search filter could allow Tenant A to retrieve Tenant B's documents.
*   **Impact:** Severe breach of confidentiality, legal liability, and loss of trust.

### 🚨 2. PII Exposure
*   **Risk:** Users inadvertently upload documents containing Personally Identifiable Information (PII) like names, emails, or SSNs.
*   **Impact:** If this data is embedded and stored, it becomes difficult to remove (GDPR "Right to be Forgotten") and can be leaked in model outputs.

### 🚨 3. Embedding Inversion Attacks
*   **Risk:** If an attacker gains access to the vector database, they might try to reconstruct the original text from the vector embeddings.
*   **Impact:** Exposure of raw data even if the database only contains numbers.

### 🚨 4. Abusive Scraping & Extraction
*   **Risk:** A malicious tenant might send thousands of queries to map out the latent space of the vector database, effectively "scraping" the knowledge base.
*   **Impact:** Intellectual property theft and system degradation.

---

## 3. Our Solution: Defense-in-Depth
We move beyond simple "metadata filtering" (which is fragile) and implement a **5-Layer Defense Architecture**.

### How We Improve Upon Standard RAG

| Feature | Standard RAG | Secure RAG (Our Solution) |
| :--- | :--- | :--- |
| **Isolation** | Metadata filters (`filter={tenant_id: "A"}`) | **Physical/Logical Separation** (Distinct Collections per Tenant) |
| **Data Privacy** | PII often stored as-is | **AI-Driven Redaction** (PII removed *before* storage) |
| **Encryption** | Server-Side Encryption (SSE) | **Envelope Encryption** (Unique KMS Key per Tenant) |
| **Access Control** | App-level checks | **Cryptographic Enforcement** (Tenant A's key cannot decrypt Tenant B's data) |
| **Monitoring** | Basic API logs | **Semantic Anomaly Detection** (ML Watchdog) |

## 4. Business Value
1.  **Compliance Ready:** Built-in PII scrubbing and encryption helps meet GDPR, HIPAA, and SOC2 requirements.
2.  **Trust:** Customers can be assured that their data is cryptographically isolated from competitors.
3.  **Resilience:** Even if the database is dumped, the data remains encrypted and useless without the specific KMS keys.
