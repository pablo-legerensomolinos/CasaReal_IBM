import ibm_boto3
from ibm_botocore.client import Config, ClientError
import json
import io

from backend_database_query.connectors.Singleton import Singleton
from backend_database_query.Logger import Logger

from backend_database_query.env import LogConfig


class CosClient(metaclass=Singleton):
    def __init__(self, CosConfig):
        try:
            self.logger = Logger('app_logger', LogConfig.misc_level).logger
            self.local_logger = Logger('cos_client', LogConfig.misc_level).logger

            self.api_key = CosConfig.api_key
            self.service_instance_id = CosConfig.service_instance_id
            self.endpoint_url = CosConfig.endpoint_url
            self.bucket = CosConfig.bucket

            self.cos = ibm_boto3.client(
                's3',
                ibm_api_key_id=self.api_key,
                ibm_service_instance_id=self.service_instance_id,
                config=Config(signature_version='oauth'),
                endpoint_url=f"https://{self.endpoint_url}")

            self.logger.info("COS Client successfully initialized.")
        except Exception as e:
            self.logger.error("Failed to initialize COS Client:", e)
            raise

    def get_buckets(self):
        self.logger.info("Retrieving list of buckets")
        try:
            response = self.cos.list_buckets()

           # Accessing the buckets list
            if 'Buckets' in response:
                buckets = [bucket['Name'] for bucket in response['Buckets']]
                return buckets
            else:
                self.logger.error(
                    "No buckets found or incorrect response structure.")
                return []
        except ClientError as be:
            self.logger.info("CLIENT ERROR: {0}\n".format(be))
            return []
        except Exception as e:
            self.logger.error(f"Failed to retrieve buckets: {e}")
            return []

    def upload_file(self, file_name, file_path, aux):
        self.logger.info("Uploading file to COS and return its public URL")
        try:
            # Open the file in binary read mode
            with open(file_path, 'rb') as file_data:
                if aux:
                    self.cos.upload_fileobj(
                        Fileobj=file_data, Bucket=self.bucket, Key=file_name)
                    public_url = f"https://{self.bucket}."
                    f"{self.endpoint_url}/{file_name}"
                else:
                    self.cos.upload_fileobj(
                        Fileobj=file_data, Bucket=self.bucket, Key=file_name)
                    # Construct the public URL
                    public_url = f"https://{self.bucket}."
                    f"{self.endpoint_url}/{file_name}"

            self.logger.info(f"Successfully uploaded {file_name} to bucket.")

            return public_url
        except Exception as e:
            self.logger.error(f"Failed to upload file "
                              f"{file_name} in the bucket and retrieve its URL: {e}")
            raise

    def upload_json(self, json_dict, file_name, time_log=False):
        '''
        Upload json dict to COS bucket
        '''
        try:
            json_str = json.dumps(json_dict, indent=4)
            bucket_name = self.bucket
            if time_log:
                bucket_name = self.bucket_time
            # Upload JSON data to IBM COS
            self.cos.put_object(Bucket=bucket_name,
                                Key=file_name, Body=json_str)

            public_url = f"https://{bucket_name}."
            f"{self.endpoint_url}/{file_name}"

            self.logger.info(f"Successfully uploaded JSON data to "
                             f"{file_name} in bucket {bucket_name}.")

            return public_url
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to convert data to JSON: {e}")

        except self.cos.exceptions.NoSuchBucket as e:
            self.logger.error(f"Bucket {bucket_name} does not exist: {e}")

        except self.cos.exceptions.ClientError as e:
            self.logger.error(
                f"Client error during uploading json to COS: {e}")

        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred uploading json to COS: {e}")

    def upload_string(self, data, file_name):
        '''
        Upload string to COS  bucket
        '''
        try:
            # Convert the string data to a byte stream
            byte_data = io.BytesIO(data.encode())
            self.cos.put_object(Bucket=self.bucket,
                                Key=file_name, Body=byte_data)
            # Close the byte stream
            byte_data.close()

            public_url = f"https://{self.bucket}."
            f"{self.endpoint_url}/{file_name}"

            self.logger.info(f"Successfully uploaded string data to "
                             f"{file_name} in bucket {self.bucket}.")

            return public_url
        except self.cos.exceptions.NoSuchBucket as e:
            self.logger.error(f"Bucket {self.bucket} does not exist: {e}")

        except self.cos.exceptions.ClientError as e:
            self.logger.error(
                f"Client error during uploading string to COS: {e}")

        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred uploading string to COS: {e}")

    def get_object(self, file_name):
        # get an object from COS. Returns a stream: https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python&locale=es#python-examples-get-file-contents
        try:

            cos_file = self.cos.get_object(Bucket=self.bucket, Key=file_name)

            self.logger.info(f"Successfully downloaded JSON data to "
                             f"{file_name} from bucket {self.bucket}.")

            return {"data": cos_file["Body"].read(), "ContentType": cos_file['ContentType']}

        except self.cos.exceptions.ClientError as e:
            self.logger.error(f"Client error during downloading file "
                              f"{file_name} from bucket {self.bucket} from COS: {e}")

        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred downloading file from COS: {e}")
            
    def list_objects(self):
        try:
            response = self.cos.list_objects_v2(Bucket=self.bucket)
            return [obj['Key'] for obj in response['Contents']]
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred listing files on COS: {e}")
