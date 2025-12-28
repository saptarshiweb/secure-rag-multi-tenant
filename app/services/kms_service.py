import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class KMSService:
    def __init__(self):
        self.client = boto3.client(
            "kms",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def create_key_for_tenant(self, tenant_id: str) -> str:
        """
        Ensures a CMK exists for the tenant. Returns the KeyId (or Alias).
        """
        alias_name = f"alias/tenant_{tenant_id}"
        
        try:
            # Check if alias exists by trying to describe it (or list aliases)
            # For simplicity in PoC, we try to create it, and if it fails, we assume it exists.
            # But create_alias doesn't return the key ID if it fails.
            # So let's try to generate a data key with the alias. If it works, key exists.
            self.client.generate_data_key(KeyId=alias_name, KeySpec='AES_256')
            return alias_name
        except ClientError:
            # If it fails (likely NotFound), create it.
            pass

        print(f"Creating new KMS key for tenant {tenant_id}...")
        try:
            response = self.client.create_key(
                Description=f"Key for tenant {tenant_id}",
                Tags=[{'TagKey': 'TenantID', 'TagValue': tenant_id}]
            )
            key_id = response['KeyMetadata']['KeyId']
            
            self.client.create_alias(
                AliasName=alias_name,
                TargetKeyId=key_id
            )
            return key_id
        except Exception as e:
            print(f"Error creating key: {e}")
            raise e

    def get_key_id(self, tenant_id: str) -> str:
        return f"alias/tenant_{tenant_id}"

    def generate_data_key(self, tenant_id: str):
        """
        Generates a DEK (Data Encryption Key) using the tenant's CMK.
        Returns (CiphertextBlob, PlaintextKey).
        """
        # Ensure key exists first
        self.create_key_for_tenant(tenant_id)
        
        key_id = self.get_key_id(tenant_id)
        response = self.client.generate_data_key(
            KeyId=key_id,
            KeySpec='AES_256'
        )
        return response['CiphertextBlob'], response['Plaintext']

    def decrypt_data_key(self, encrypted_key_blob: bytes) -> bytes:
        """
        Decrypts the DEK using KMS.
        """
        response = self.client.decrypt(
            CiphertextBlob=encrypted_key_blob
        )
        return response['Plaintext']
