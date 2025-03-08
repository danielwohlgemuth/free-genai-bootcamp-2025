import os
from minio import Minio


MINIO_URL = os.getenv("MINIO_URL", "http://localhost:9000")
BUCKET_NAME = os.getenv("BUCKET_NAME", "haiku")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", None)
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", None)


minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
create_bucket_if_not_exists()


def create_bucket_if_not_exists():
    try:
        minio_client.make_bucket(BUCKET_NAME)
    except Exception as e:
        print(f"Bucket {BUCKET_NAME} already exists or could not be created: {e}")

def upload_file(file_path: str, object_name: str):
    minio_client.fput_object(BUCKET_NAME, object_name, file_path)
