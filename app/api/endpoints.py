from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.pii_service import PIIScrubber
from app.services.encryption_service import EncryptionService
from app.services.storage_service import StorageService
from app.services.vector_service import VectorService
from app.services.anomaly_service import AnomalyDetector
from app.services.llm_service import LLMService
import uuid

router = APIRouter()

# Initialize Services
pii_scrubber = PIIScrubber()
encryption_service = EncryptionService()
storage_service = StorageService()
vector_service = VectorService()
anomaly_detector = AnomalyDetector()
llm_service = LLMService()

class IngestRequest(BaseModel):
    tenant_id: str
    text: str

class QueryRequest(BaseModel):
    tenant_id: str
    query: str

@router.get("/tenants")
def get_tenants():
    """
    Returns a list of all registered tenants (based on Vector DB collections).
    """
    try:
        return vector_service.list_tenants()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
def ingest_document(request: IngestRequest):
    """
    Secure Ingestion Pipeline:
    1. Redact PII (ML)
    2. Encrypt Text (KMS + Local)
    3. Upload to S3 (LocalStack)
    4. Embed & Index (Qdrant)
    """
    try:
        # 1. PII Redaction
        scrubbed_text = pii_scrubber.scrub(request.text)
        
        # 2. Encryption
        encryption_result = encryption_service.encrypt_text(request.tenant_id, scrubbed_text)
        ciphertext = encryption_result["ciphertext"]
        encrypted_dek = encryption_result["encrypted_dek"]
        
        # 3. Storage (S3)
        file_key = f"{request.tenant_id}/{uuid.uuid4()}.enc"
        s3_uri = storage_service.upload_file(file_key, ciphertext)
        
        # 4. Vector Indexing
        # Note: We embed the SCRUBBED text, so we can search for it.
        # But we store the ENCRYPTED text in S3.
        point_id, vector = vector_service.upsert_vector(
            request.tenant_id, 
            scrubbed_text, 
            s3_uri, 
            encrypted_dek
        )
        
        return {
            "status": "success", 
            "point_id": point_id, 
            "s3_uri": s3_uri,
            "scrubbed_preview": scrubbed_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
def query_document(request: QueryRequest):
    """
    Secure Retrieval Pipeline:
    1. Anomaly Check (ML)
    2. Vector Search (Qdrant)
    3. Fetch Encrypted Blob (S3)
    4. Decrypt (KMS)
    """
    try:
        # 1. Anomaly Detection (Pre-search)
        # We need the query vector to check for anomalies.
        query_vector = vector_service.embed_text(request.query)
        
        # Log and check
        anomaly_detector.log_query(request.tenant_id, query_vector)
        if anomaly_detector.is_anomalous(request.tenant_id, query_vector):
            # In a real app, we might block. For PoC, we flag it in response.
            print(f"DEBUG: Anomaly DETECTED for {request.tenant_id}")
            is_flagged = True
        else:
            print(f"DEBUG: Query normal for {request.tenant_id}")
            is_flagged = False

        # 2. Vector Search
        search_results, _ = vector_service.search(request.tenant_id, request.query)
        
        documents = []
        for res in search_results:
            payload = res.payload
            s3_uri = payload["s3_uri"]
            encrypted_dek_hex = payload["encrypted_dek_hex"]
            
            # 3. Fetch from S3
            # s3://bucket/key -> extract key
            file_key = s3_uri.replace(f"s3://{storage_service.bucket}/", "")
            encrypted_data = storage_service.download_file(file_key)
            
            # 4. Decrypt
            encrypted_dek = bytes.fromhex(encrypted_dek_hex)
            plaintext = encryption_service.decrypt_text(encrypted_data, encrypted_dek)
            
            documents.append({
                "score": res.score,
                "content": plaintext,
                "s3_uri": s3_uri
            })
            
        # 5. Generate Answer (RAG)
        context = " ".join([doc["content"] for doc in documents])
        generated_answer = llm_service.generate_answer(context, request.query)

        return {
            "results": documents,
            "generated_answer": generated_answer,
            "anomaly_detected": is_flagged
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
