"""Pillow pipeline: validate, orient, strip metadata, resize and re-encode."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_ICC_BYTES = 1_000_000


class ImageValidationError(Exception):
    status_code = 422
    code = "invalid_image"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnsupportedImageError(ImageValidationError):
    status_code = 415
    code = "unsupported_media"


@dataclass(frozen=True)
class ProcessedImage:
    width: int
    height: int
    mime: str
    extension: str
    bytes: int


def _open_and_check(source: Path, *, min_edge: int, max_pixels: int) -> tuple[Image.Image, str, bool, bytes | None]:
    try:
        image = Image.open(source)
    except UnidentifiedImageError as exc:
        raise UnsupportedImageError("Choose a JPEG, PNG or WebP photograph.") from exc
    except Image.DecompressionBombError as exc:
        raise ImageValidationError("This photograph has too many pixels.") from exc
    except OSError as exc:
        raise ImageValidationError("This file could not be read as an image.") from exc

    try:
        detected = (image.format or "").upper()
        if detected not in ALLOWED_FORMATS:
            raise UnsupportedImageError("Choose a JPEG, PNG or WebP photograph.")
        if getattr(image, "is_animated", False) or getattr(image, "n_frames", 1) > 1:
            raise UnsupportedImageError("Animated images are not supported.")
        if image.width < min_edge or image.height < min_edge:
            raise ImageValidationError(f"Photographs must be at least {min_edge} pixels on each edge.")
        if image.width * image.height > max_pixels:
            raise ImageValidationError("This photograph has too many pixels.")
        has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
        icc = image.info.get("icc_profile")
        if icc is not None and len(icc) > MAX_ICC_BYTES:
            icc = None
        return image, detected, has_alpha, icc
    except Exception:
        image.close()
        raise


def process_image(
    source: Path,
    destination: Path,
    *,
    max_edge: int,
    min_edge: int = 64,
    max_pixels: int = 40_000_000,
    jpeg_quality: int = 85,
    force_jpeg: bool = False,
) -> ProcessedImage:
    """Write a metadata-free copy and return its stored properties.

    A fresh image is created for the output so EXIF, XMP, GPS, comments and
    other ancillary chunks cannot survive the re-encode. Only pixels and, when
    small enough, the ICC colour profile are carried over.
    """
    source = Path(source)
    destination = Path(destination)
    image, detected, has_alpha, icc = _open_and_check(source, min_edge=min_edge, max_pixels=max_pixels)

    try:
        working = ImageOps.exif_transpose(image)
        # ``thumbnail`` shrinks in place and never enlarges a small source.
        working.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)

        out_format = "JPEG" if (force_jpeg or detected != "PNG" or not has_alpha) else "PNG"
        if out_format == "PNG":
            clean = Image.new("RGBA", working.size, (0, 0, 0, 0))
            clean.paste(working.convert("RGBA"))
            extension, mime = ".png", "image/png"
            save_options: dict[str, object] = {"optimize": True}
        else:
            clean = Image.new("RGB", working.size, (255, 255, 255))
            foreground = working.convert("RGBA")
            clean.paste(foreground, mask=foreground.getchannel("A"))
            extension, mime = ".jpg", "image/jpeg"
            save_options = {"quality": jpeg_quality, "optimize": True, "progressive": True}

        if icc:
            save_options["icc_profile"] = icc
        destination.parent.mkdir(parents=True, exist_ok=True)
        clean.save(destination, out_format, **save_options)
        width, height = clean.size
    except UnidentifiedImageError as exc:
        raise UnsupportedImageError("Choose a JPEG, PNG or WebP photograph.") from exc
    except Image.DecompressionBombError as exc:
        raise ImageValidationError("This photograph has too many pixels.") from exc
    except OSError as exc:
        raise ImageValidationError("The photograph could not be processed.") from exc
    finally:
        image.close()

    try:
        size = destination.stat().st_size
    except OSError as exc:
        raise ImageValidationError("The photograph could not be stored.") from exc
    if size <= 0:
        raise ImageValidationError("The photograph could not be stored.")
    return ProcessedImage(width=width, height=height, mime=mime, extension=extension, bytes=size)
