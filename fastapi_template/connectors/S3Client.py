import boto3
from botocore.client import Config

from fastapi_template.connectors.Singleton import Singleton
from fastapi_template.Logger import Logger

from fastapi_template.env import LogConfig


class S3Client(metaclass=Singleton):
    def __init__(self, S3Config):
        try:
            self.logger = Logger('app_logger', LogConfig.misc_level).logger
            self.local_logger = Logger('s3_client', LogConfig.misc_level).logger

            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=S3Config.hmac_access_key_id,
                aws_secret_access_key=S3Config.hmac_secret_access_key,
                config=Config(signature_version='s3v4'),
                endpoint_url=f"https://{S3Config.endpoint_url}"
            )
            
            self.logger.info("S3 Client successfully initialized.")
        except Exception as e:
            self.logger.error("Failed to initialize S3 Client:", e)
            raise
        
    def download_pdf_from_cos(self, bucket_name, object_key, download_path):
        self.logger.info("Downloading file")
        try:
            # Retrieve the object from the specified bucket and key
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            
            # Read the object's content
            file_content = response['Body'].read()

            # Save the content as a PDF file
            with open(download_path, 'wb') as pdf_file:
                pdf_file.write(file_content)

            self.logger.info(f"PDF file {object_key} downloaded successfully to {download_path}.")
        except Exception as e:
            self.logger.error(f"Error retrieving object {object_key} from bucket {bucket_name}: {e}")


