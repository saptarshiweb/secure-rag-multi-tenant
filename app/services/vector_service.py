from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from sentence_transformers import SentenceTransformer
import uuid

class VectorService:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        # Using a small, fast local model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384

    def ensure_collection(self, tenant_id: str):
        """
        Ensures a collection exists for the tenant.
        """
        collection_name = f"tenant_{tenant_id}"
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE)
            )

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()

    def upsert_vector(self, tenant_id: str, text: str, s3_uri: str, encrypted_dek: bytes):
        """
        Embeds text and stores the vector + metadata (S3 pointer, Encrypted DEK) in Qdrant.
        """
        self.ensure_collection(tenant_id)
        vector = self.embed_text(text)
        point_id = str(uuid.uuid4())
        
        # We store the Encrypted DEK as a hex string in metadata so we can retrieve it later
        encrypted_dek_hex = encrypted_dek.hex()

        self.client.upsert(
            collection_name=f"tenant_{tenant_id}",
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "s3_uri": s3_uri,
                        "encrypted_dek_hex": encrypted_dek_hex
                    }
                )
            ]
        )
        return point_id, vector

    def search(self, tenant_id: str, query_text: str, limit: int = 3):
        """
        Searches the tenant's collection.
        """
        self.ensure_collection(tenant_id)
        query_vector = self.embed_text(query_text)
        
        results = self.client.search(
            collection_name=f"tenant_{tenant_id}",
            query_vector=query_vector,
            limit=limit
        )
        return results, query_vector

    def list_tenants(self) -> list[str]:
        """
        Returns a list of tenant IDs based on existing Qdrant collections.
        """
        response = self.client.get_collections()
        # Filter collections that start with "tenant_" and strip the prefix
        tenants = []
        for collection in response.collections:
            if collection.name.startswith("tenant_"):
                tenants.append(collection.name.replace("tenant_", ""))
        return tenants
