# app/utils/file_handler.py
import os
from pathlib import Path
from fastapi import UploadFile
from typing import Tuple, Optional
import aiofiles
import uuid
from datetime import datetime

# Optional: boto3 for S3
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    HAS_BOTO = True
except Exception:
    HAS_BOTO = False

UPLOAD_DIR = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_file_local(upload_file: UploadFile, subfolder: str = "") -> Tuple[str, int]:
    """
    Save UploadFile to local disk under uploads/<subfolder>/ and return (file_path, size).
    """
    dest_dir = UPLOAD_DIR / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    extension = Path(upload_file.filename).suffix
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{extension}"
    dest_path = dest_dir / filename
    size = 0
    async with aiofiles.open(dest_path, "wb") as out_file:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            await out_file.write(chunk)
            size += len(chunk)
    # reset file pointer if needed by caller
    return str(dest_path), size

def upload_to_s3_local_fallback(file_path: str, bucket: str, key: Optional[str] = None) -> Optional[str]:
    """
    Upload a local file to S3 if boto3 is available and credentials configured.
    Returns S3 object URL or None if not uploaded.
    """
    if not HAS_BOTO:
        return None
    # check environment variables are present for AWS keys
    s3_client = boto3.client("s3")
    if key is None:
        key = Path(file_path).name
    try:
        s3_client.upload_file(file_path, bucket, key)
        # build URL (public bucket assumed)
        region = s3_client.meta.region_name
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    except (BotoCoreError, ClientError) as e:
        # log in real app
        return None
