# python
import argparse
import os
import sys
import boto3
import botocore

def s3_client(endpoint_url, region, access_key, secret_key):
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=botocore.client.Config(signature_version="s3v4"),
    )

def ensure_bucket(s3, bucket):
    try:
        s3.create_bucket(Bucket=bucket)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass
    except botocore.exceptions.ClientError as e:
        # BucketExistsWithDifferentName or other errors are ignored if already there
        code = e.response.get("Error", {}).get("Code", "")
        if code not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            raise

def upload_file(s3, bucket, key, filename):
    s3.upload_file(filename, bucket, key)

def main():
    p = argparse.ArgumentParser(description="Upload a file to LocalStack S3")
    p.add_argument("--file", "-f", default="cards_data.csv", help="Path to local file to upload")
    p.add_argument("--bucket", "-b", default="my-bucket", help="S3 bucket name")
    p.add_argument("--key", "-k", help="S3 object key (defaults to filename)")
    p.add_argument("--endpoint", "-e", default=os.getenv("S3_ENDPOINT", "http://localhost:4566"), help="S3 endpoint (LocalStack)")
    p.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    p.add_argument("--access-key", default=os.getenv("AWS_ACCESS_KEY_ID", "test"))
    p.add_argument("--secret-key", default=os.getenv("AWS_SECRET_ACCESS_KEY", "test"))
    args = p.parse_args()

    if not os.path.isfile(args.file):
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    key = args.key or os.path.basename(args.file)
    s3 = s3_client(args.endpoint, args.region, args.access_key, args.secret_key)

    ensure_bucket(s3, args.bucket)
    upload_file(s3, args.bucket, key, args.file)
    print(f"Uploaded `{args.file}` to s3://{args.bucket}/{key} via {args.endpoint}")

if __name__ == "__main__":
    main()
