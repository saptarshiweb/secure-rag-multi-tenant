import boto3
from app.core.config import settings
import io

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def upload_file(self, file_key: str, file_content: bytes):
        """
        Uploads bytes to S3.
        """
        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_key,
            Body=file_content
        )
        return f"s3://{self.bucket}/{file_key}"

    def download_file(self, file_key: str) -> bytes:
        """
        Downloads bytes from S3.
        """
        response = self.s3.get_object(Bucket=self.bucket, Key=file_key)
        return response['Body'].read()
