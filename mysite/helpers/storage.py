import os

import boto3
from django.conf import settings
from botocore.client import Config
import uuid
from datetime import datetime


def generate_media_presigned_url(key: str, expires_in: int = 300):
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=Config(signature_version="s3v4")
    )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )
    return url

def generate_post_image_path(instance, filename):
    user_id = instance.user.id
    now = datetime.utcnow()

    img_uuid = uuid.uuid4().hex
    shard = img_uuid[:2]

    prefix = "dev/" if settings.DEBUG else ""

    folder = f"{prefix}posts/images/{now.year}/{now.month}/{now.day}/{shard}/{user_id}"
    filename = f"{img_uuid}.webp"

    return f"{folder}/{filename}"