from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from typing import Optional
from app.services.cloudinary_service import cloudinary_service

router = APIRouter()


@router.post(
    "/image",
    summary="Upload image to Cloudinary CDN",
    description="Uploads an image file to Cloudinary and returns its permanent optimized CDN URL.",
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload (JPEG, PNG, WEBP)"),
    folder: str = Form("dgda/general", description="Target folder in Cloudinary"),
    public_id: Optional[str] = Form(None, description="Optional custom filename / public ID"),
):
    # Validate content type
    allowed_content_types = ["image/jpeg", "image/png", "image/webp", "image/gif", "image/jpg"]
    if file.content_type and file.content_type.lower() not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image format: {file.content_type}. Supported: JPEG, PNG, WEBP, GIF",
        )

    try:
        content = await file.read()
        res = cloudinary_service.upload_image(
            file_or_path=content,
            folder=folder,
            public_id=public_id,
            overwrite=True,
        )
        return {
            "success": True,
            "url": res["url"],
            "public_id": res["public_id"],
            "format": res["format"],
            "width": res.get("width"),
            "height": res.get("height"),
            "bytes": res.get("bytes"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cloudinary upload failed: {str(e)}",
        )
