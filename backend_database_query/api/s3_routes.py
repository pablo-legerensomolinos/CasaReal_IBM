from fastapi import APIRouter

from backend_database_query.Logger import Logger
from backend_database_query.connectors.S3Client import S3Client
from backend_database_query.env import S3Config

logger = Logger("api_logger").logger

s3_bp = APIRouter(prefix='/api/s3', tags=['S3 Operations'])


@s3_bp.get('/test', summary="Retrieve and download file from object storage")
def s3_test():
    # s3 client established
    s3_client = S3Client(S3Config)
    
    OBJECT_KEY = "Demo Evaluation Checklist [watsonx.governance L3 Tech Sales].PDF"
    
    download_path = f"{OBJECT_KEY}.pdf"
    
    # Call the method to download the PDF
    s3_client.download_pdf_from_cos(S3Config.bucket, OBJECT_KEY, download_path)

    return {"status": 200, "message": "file downloaded successfully"}
