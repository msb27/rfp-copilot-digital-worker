# rag/download_vectorstore.py
import os
import boto3
from botocore.exceptions import ClientError

BUCKET = "rfp-copilot-vectorstore"
S3_PREFIX = "vectorstore/"
LOCAL_PATH = "rag/vectorstore"

def download():
    if os.path.exists(LOCAL_PATH):
        print("Vectorstore already downloaded.")
        return

    print(f"Downloading vectorstore from s3://{BUCKET}/{S3_PREFIX}")
    s3 = boto3.client('s3')
    os.makedirs(LOCAL_PATH, exist_ok=True)

    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=BUCKET, Prefix=S3_PREFIX):
            for obj in page.get('Contents', []):
                key = obj['Key']
                rel_path = os.path.relpath(key, S3_PREFIX)
                local_file = os.path.join(LOCAL_PATH, rel_path)
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                s3.download_file(BUCKET, key, local_file)
                print(f"Downloaded: {key}")
        print("Vectorstore ready.")
    except ClientError as e:
        if 'NoSuchKey' in str(e):
            print("No vectorstore in S3. RAG disabled.")
        else:
            raise

if __name__ == "__main__":
    download()