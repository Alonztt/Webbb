from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from PIL import Image
from fastapi import HTTPException, UploadFile


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

THUMB_SIZES = {
    "sm": 320,
    "md": 720,
    "lg": 1280,
}


def ensure_dirs(base_dir: Path) -> dict[str, Path]:
    subdirs = {
        "orig": base_dir / "original",
        "sm": base_dir / "sm",
        "md": base_dir / "md",
        "lg": base_dir / "lg",
    }
    for p in subdirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return subdirs


def _normalized_ext_from_upload(file: UploadFile) -> str:
    filename = file.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext == ".jpeg":
        ext = ".jpg"
    return ext


def _guess_ext_from_mime(mime: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return mapping.get(mime, "")


def _strip_alpha(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        alpha = image.getchannel("A") if "A" in image.getbands() else None
        background.paste(image, mask=alpha)
        return background
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def _save_jpeg(image: Image.Image, path: Path) -> None:
    image.save(path.as_posix(), format="JPEG", quality=88, optimize=True, progressive=True)


def save_image_with_thumbs(file: UploadFile, uploads_dir: Path) -> dict:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    original_bytes = file.file.read()
    if not original_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        pil_image = Image.open(io.BytesIO(original_bytes))
        pil_image.load()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to parse image")

    width, height = pil_image.size
    size_bytes = len(original_bytes)

    uuid_hex = uuid4().hex

    dirs = ensure_dirs(uploads_dir)

    # Decide original extension
    ext = _normalized_ext_from_upload(file)
    if ext not in ALLOWED_EXTENSIONS:
        guessed = _guess_ext_from_mime(file.content_type or "")
        ext = guessed if guessed in ALLOWED_EXTENSIONS else ".jpg"

    # Save original as-is (re-encode only if needed)
    orig_path = (dirs["orig"] / f"{uuid_hex}{ext}")
    try:
        # If the uploaded image bytes are already in the same format and filename has proper ext,
        # save bytes directly; otherwise re-encode to keep integrity.
        if ext in {".jpg", ".jpeg"}:
            _save_jpeg(_strip_alpha(pil_image), orig_path)
        else:
            pil_image.save(orig_path.as_posix())
    except Exception:
        # Fallback to JPEG
        _save_jpeg(_strip_alpha(pil_image), orig_path.with_suffix(".jpg"))
        ext = ".jpg"

    # Generate thumbnails in JPEG
    thumb_ext = ".jpg"
    base_for_thumbs = _strip_alpha(pil_image)
    for key, max_side in THUMB_SIZES.items():
        thumb = base_for_thumbs.copy()
        thumb.thumbnail((max_side, max_side))
        _save_jpeg(thumb, (dirs[key] / f"{uuid_hex}{thumb_ext}"))

    return {
        "uuid": uuid_hex,
        "original_ext": ext.lstrip("."),
        "thumb_ext": thumb_ext.lstrip("."),
        "width": width,
        "height": height,
        "size_bytes": size_bytes,
    }