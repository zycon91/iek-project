from PIL import Image, ImageOps
import os
import uuid
import mimetypes
from io import BytesIO
from typing import Tuple, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(override=True)

B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
B2_ENDPOINT = os.getenv("B2_ENDPOINT")
B2_DOWNLOAD_URL = os.getenv("B2_DOWNLOAD_URL")
# CDN_BASE_URL = os.getenv("CDN_BASE_URL")

if not all([B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME, B2_ENDPOINT]):
    raise RuntimeError("Missing B2_* environment variables")

s3 = boto3.client(
    "s3",
    endpoint_url = B2_ENDPOINT,
    aws_access_key_id = B2_KEY_ID,
    aws_secret_access_key = B2_APPLICATION_KEY,
    region_name = "eu-central-003",
    config = Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

def _public_url(key: str) -> str:
    # Use CDN URL if available, otherwise fallback to direct B2 URL
    base_url = B2_DOWNLOAD_URL
    return f"{base_url}/file/{B2_BUCKET_NAME}/{key}"

def upload_image_bytes(
    content: bytes,
    filename: str,
    folder: str = "movies",
    content_type: Optional[str] = None,
) -> dict[str, str]:
    """
    Upload raw image bytes to B2. Returns {'url': ..., 'key': ...}
    """
    ct = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    key = f"{folder}/{uuid.uuid4()}-{filename}"

    try:
        s3.put_object(
            Bucket = B2_BUCKET_NAME,
            Key = key,
            Body = content,
            ContentType = ct,
            CacheControl = "public, max-age=31536000, immutable",
        )
    except ClientError as e:
        raise RuntimeError(f"B2 upload failed: {e}")

    return {"url": _public_url(key), "key": key, "content_type": ct}

def create_and_upload_thumbnail(
    image_bytes: bytes,
    size: Tuple[int, int] = (250, 250),
    folder: str = "movies/thumbnails",
    quality: int = 85,
) -> dict[str, str]:
    """
    Create a thumbnail (max width/height = size) and upload it.
    Returns {'url': ..., 'key': ...}
    """
    with Image.open(BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail(size, resample=Image.Resampling.LANCZOS)

        buf = BytesIO()
        img.save(buf, format = "WEBP", quality = quality, method = 6)
        buf.seek(0)

        thumb_filename = f"thumbnail_{uuid.uuid4()}.webp"

        return upload_image_bytes(
            content = buf.getvalue(),
            filename = thumb_filename,
            folder = folder,
            content_type = "image/webp",
        )

def delete_object(key: str) -> None:
    """Delete an object from B2. Ignores missing keys."""
    try:
        s3.delete_object(Bucket=B2_BUCKET_NAME, Key=key)
    except ClientError:
        pass