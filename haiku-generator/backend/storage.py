import io
import json
import os
from dotenv import load_dotenv
from minio import Minio


load_dotenv()
MINIO_URL = os.getenv("MINIO_URL", "localhost:9000")
BUCKET_NAME = os.getenv("BUCKET_NAME", "haiku")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", None)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", None)


minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)


def create_bucket_if_not_exists():
    found = minio_client.bucket_exists(BUCKET_NAME)
    if not found:
        minio_client.make_bucket(BUCKET_NAME)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*",
                },
            ],
        }
        minio_client.set_bucket_policy(BUCKET_NAME, json.dumps(policy))


create_bucket_if_not_exists()


def upload_file(file: io.BytesIO, length: int, object_name: str):
    minio_client.put_object(BUCKET_NAME, object_name, file, length=length)
