import io
import json
import os
from dotenv import load_dotenv
from minio import Minio
from utils import str_to_bool


load_dotenv()
BUCKET_URL = os.getenv("BUCKET_URL", "localhost:9000")
BUCKET_NAME = os.getenv("BUCKET_NAME", "haiku")
BUCKET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", None)
BUCKET_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
BUCKET_SECURE = str_to_bool(os.getenv("BUCKET_SECURE"), default=True)


minio_client = Minio(BUCKET_URL, access_key=BUCKET_ACCESS_KEY, secret_key=BUCKET_SECRET_KEY, secure=BUCKET_SECURE)


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
        print("Bucket created")
    else:
        print("Bucket already exists")

def upload_file(file: io.BytesIO, length: int, object_name: str):
    minio_client.put_object(BUCKET_NAME, object_name, file, length=length)
