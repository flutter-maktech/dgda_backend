import logging
from typing import Optional, Dict, Any, Union
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Enterprise Cloudinary CDN service for storing and optimizing media assets."""

    def __init__(self):
        self._configured = False
        self._ensure_configured()

    def _ensure_configured(self) -> bool:
        if self._configured:
            return True
        try:
            if settings.CLOUDINARY_URL:
                cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
            elif settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True,
                )
            self._configured = True
            return True
        except Exception as e:
            logger.error(f"Failed to configure Cloudinary: {e}")
            return False

    def upload_image(
        self,
        file_or_path: Any,
        folder: str = "dgda/general",
        public_id: Optional[str] = None,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        """Upload an image file or byte stream to Cloudinary and return details with secure HTTPS URL."""
        self._ensure_configured()
        options = {
            "folder": folder,
            "resource_type": "image",
            "overwrite": overwrite,
        }
        if public_id:
            options["public_id"] = public_id

        try:
            res = cloudinary.uploader.upload(file_or_path, **options)
            return {
                "url": res.get("secure_url") or res.get("url"),
                "public_id": res.get("public_id"),
                "format": res.get("format"),
                "width": res.get("width"),
                "height": res.get("height"),
                "bytes": res.get("bytes"),
            }
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise e

    def delete_image(self, public_id: str) -> bool:
        """Delete an asset from Cloudinary by its public ID."""
        self._ensure_configured()
        try:
            res = cloudinary.uploader.destroy(public_id)
            return res.get("result") == "ok"
        except Exception as e:
            logger.error(f"Cloudinary deletion failed: {e}")
            return False


cloudinary_service = CloudinaryService()
