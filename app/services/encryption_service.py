from cryptography.fernet import Fernet
import base64
from app.services.kms_service import KMSService

class EncryptionService:
    def __init__(self):
        self.kms = KMSService()

    def encrypt_text(self, tenant_id: str, text: str):
        """
        Encrypts text using Envelope Encryption.
        1. Generate DEK from KMS.
        2. Encrypt text with DEK.
        3. Return Encrypted Text + Encrypted DEK.
        """
        # 1. Get Data Key from KMS
        encrypted_dek, plaintext_dek = self.kms.generate_data_key(tenant_id)
        
        # 2. Encrypt text using plaintext DEK
        # Fernet requires 32-byte url-safe base64 encoded key. 
        # KMS returns 32 bytes (for AES_256). We need to encode it.
        f = Fernet(base64.urlsafe_b64encode(plaintext_dek))
        ciphertext = f.encrypt(text.encode())
        
        return {
            "ciphertext": ciphertext, # bytes
            "encrypted_dek": encrypted_dek # bytes
        }

    def decrypt_text(self, encrypted_data: bytes, encrypted_dek: bytes):
        """
        Decrypts text.
        1. Decrypt DEK using KMS.
        2. Decrypt text using DEK.
        """
        # 1. Decrypt DEK using KMS
        plaintext_dek = self.kms.decrypt_data_key(encrypted_dek)
        
        # 2. Decrypt text
        f = Fernet(base64.urlsafe_b64encode(plaintext_dek))
        return f.decrypt(encrypted_data).decode()
