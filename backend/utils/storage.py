import uuid
from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps

# backend/utils/storage.py -> parent = utils/ -> parent.parent = backend/
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

STATIC_URL_PREFIX = "/static"


def _public_url(key: str) -> str:
    return f"{STATIC_URL_PREFIX}/{key}"


def save_image_bytes(
    content: bytes,
    filename: str,
    folder: str = "movies",
) -> dict[str, str]:
    """
    Save raw image bytes under uploads/<folder>/.
    Returns {'url': ..., 'key': ...}
    """
    # uuid μπροστά από το όνομα: αποφεύγουμε συγκρούσεις ονομάτων
    # και "καθαρίζουμε" ό,τι περίεργο φέρει το filename του χρήστη
    safe_name = Path(filename).name
    key = f"{folder}/{uuid.uuid4()}-{safe_name}"

    file_path = UPLOAD_DIR / key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)

    return {"url": _public_url(key), "key": key}


def create_and_save_thumbnail(
    image_bytes: bytes,
    size: Tuple[int, int] = (400, 400),
    folder: str = "movies/thumbnails",
    quality: int = 85,
) -> dict[str, str]:
    """
    Create a thumbnail (max width/height = size) and save it as WEBP.
    Returns {'url': ..., 'key': ...}
    """
    with Image.open(BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail(size, resample=Image.Resampling.LANCZOS)

        buf = BytesIO()
        img.save(buf, format="WEBP", quality=quality, method=6)

        return save_image_bytes(
            content=buf.getvalue(),
            filename=f"thumbnail_{uuid.uuid4()}.webp",
            folder=folder,
        )


def delete_object(key: str) -> None:
    """Delete a stored file. Ignores missing files."""
    file_path = (UPLOAD_DIR / key).resolve()
    # safety: μην επιτρέψεις ποτέ διαγραφή εκτός του uploads/
    if UPLOAD_DIR.resolve() not in file_path.parents:
        return
    file_path.unlink(missing_ok=True)
