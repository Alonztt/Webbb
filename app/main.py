from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Literal

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Image
from .image_utils import save_image_with_thumbs, THUMB_SIZES


APP_ROOT = Path("/workspace")
STATIC_DIR = APP_ROOT / "static"
UPLOADS_DIR = APP_ROOT / "uploads"


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Photo Hosting", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Ensure directories
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    # Create tables
    Base.metadata.create_all(bind=engine)


# Static files for frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR.as_posix()), name="static")


@app.get("/", include_in_schema=False)
async def root_index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path.as_posix())


@app.post("/api/upload")
async def upload_images(
    files: List[UploadFile] = File(..., description="One or more image files"),
    db: Session = Depends(get_db),
):
    saved_items = []
    for f in files:
        info = save_image_with_thumbs(f, UPLOADS_DIR)
        image = Image(
            uuid=info["uuid"],
            original_filename=f.filename or info["uuid"],
            original_ext=info["original_ext"],
            content_type=f.content_type or "image/jpeg",
            width=info["width"],
            height=info["height"],
            size_bytes=info["size_bytes"],
            thumb_ext=info["thumb_ext"],
            is_public=True,
            created_at=datetime.utcnow(),
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        saved_items.append(_image_to_dto(image))
    return {"items": saved_items}


@app.get("/api/images")
async def list_images(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Image).order_by(desc(Image.created_at)).offset(offset).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return {"items": [_image_to_dto(row) for row in rows]}


@app.delete("/api/images/{uuid}")
async def delete_image(uuid: str, db: Session = Depends(get_db)):
    row = db.execute(select(Image).where(Image.uuid == uuid)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    _delete_image_files(row)
    db.delete(row)
    db.commit()
    return {"status": "ok"}


@app.get("/i/{uuid}/{variant}")
async def serve_image(uuid: str, variant: Literal["orig", "sm", "md", "lg"], db: Session = Depends(get_db)):
    row = db.execute(select(Image).where(Image.uuid == uuid)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    path = _path_for_variant(row, variant)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    media_type = row.content_type if variant == "orig" else "image/jpeg"
    return FileResponse(path.as_posix(), media_type=media_type)


def _image_to_dto(img: Image) -> dict:
    return {
        "id": img.id,
        "uuid": img.uuid,
        "original_filename": img.original_filename,
        "content_type": img.content_type,
        "width": img.width,
        "height": img.height,
        "size_bytes": img.size_bytes,
        "created_at": img.created_at.isoformat() + "Z",
        "urls": {
            "orig": f"/i/{img.uuid}/orig",
            "sm": f"/i/{img.uuid}/sm",
            "md": f"/i/{img.uuid}/md",
            "lg": f"/i/{img.uuid}/lg",
        },
    }


def _path_for_variant(img: Image, variant: str) -> Path:
    if variant == "orig":
        return UPLOADS_DIR / "original" / f"{img.uuid}.{img.original_ext}"
    return UPLOADS_DIR / variant / f"{img.uuid}.{img.thumb_ext}"


def _delete_image_files(img: Image) -> None:
    variants = ["orig", *THUMB_SIZES.keys()]
    for v in variants:
        p = _path_for_variant(img, "orig" if v == "orig" else v)
        try:
            os.remove(p)
        except FileNotFoundError:
            pass