"""Persistent custom background image storage & strict validation for Design Studio genres.

Stores uploaded images under `<BASE_DIR>/data/design_studio_bg/` so they persist
across container restarts/rebuilds on NAS deployments without requiring host-app
MEDIA_URL setup or database migrations.
"""
from __future__ import annotations

from pathlib import Path
import re
import struct

from django.conf import settings as django_settings
from django.urls import reverse

from .genres import GENRE_DEFINITIONS

ALLOWED_EXT_BY_FORMAT: dict[str, str] = {
    "jpeg": "jpg",
    "png": "png",
    "webp": "webp",
}

CONTENT_TYPE_BY_EXT: dict[str, str] = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_WIDTH = 640
MIN_HEIGHT = 360
MAX_WIDTH = 6000
MAX_HEIGHT = 6000


def _parse_png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Ungültige PNG-Datei (IHDR-Header fehlt).")
    w, h = struct.unpack(">II", data[16:24])
    return int(w), int(h)


def _parse_webp_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("Ungültige WebP-Datei.")
    chunk = data[12:16]
    if chunk == b"VP8X":
        if len(data) < 30:
            raise ValueError("Beschädigter WebP-VP8X-Header.")
        w = 1 + int.from_bytes(data[24:27], "little")
        h = 1 + int.from_bytes(data[27:30], "little")
        return w, h
    if chunk == b"VP8 ":
        if len(data) < 30:
            raise ValueError("Beschädigter WebP-VP8-Header.")
        w, h = struct.unpack("<HH", data[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if chunk == b"VP8L":
        if len(data) < 25 or data[20] != 0x2F:
            raise ValueError("Beschädigter WebP-VP8L-Header.")
        bits = struct.unpack("<I", data[21:25])[0]
        w = (bits & 0x3FFF) + 1
        h = ((bits >> 14) & 0x3FFF) + 1
        return int(w), int(h)
    raise ValueError("Nicht unterstützter WebP-Untertyp.")


def _parse_jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("Ungültige JPEG-Datei.")
    i = 2
    n = len(data)
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3,
        0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB,
        0xCD, 0xCE, 0xCF,
    }
    while i < n:
        while i < n and data[i] != 0xFF:
            i += 1
        while i < n and data[i] == 0xFF:
            i += 1
        if i >= n:
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9, 0x01) or (0xD0 <= marker <= 0xD7):
            continue
        if i + 2 > n:
            break
        seg_len = struct.unpack(">H", data[i : i + 2])[0]
        if seg_len < 2 or i + seg_len > n:
            break
        if marker in sof_markers:
            if i + 7 > n:
                break
            h, w = struct.unpack(">HH", data[i + 3 : i + 7])
            return int(w), int(h)
        i += seg_len
    raise ValueError("JPEG-Bildmaße konnten nicht ausgelesen werden.")


def detect_image_info(data: bytes) -> tuple[str, int, int]:
    """Detect real image format via magic bytes and parse (format_key, width, height)."""
    if not data or len(data) < 12:
        raise ValueError("Die Datei ist leer oder beschädigt.")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = _parse_png_dimensions(data)
        return "png", w, h
    if data[:3] == b"\xff\xd8\xff":
        w, h = _parse_jpeg_dimensions(data)
        return "jpeg", w, h
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        w, h = _parse_webp_dimensions(data)
        return "webp", w, h
    raise ValueError("Nicht unterstütztes Bildformat. Erlaubt sind ausschließlich JPG, PNG und WebP.")


def validate_bg_image(uploaded_file) -> tuple[bytes, str, int, int]:
    """Validate uploaded Django file for size, magic-byte format, and pixel dimensions."""
    if uploaded_file is None:
        raise ValueError("Keine Bilddatei ausgewählt.")
    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_BYTES:
        mb = size / (1024 * 1024)
        raise ValueError(f"Datei zu groß ({mb:.2f} MB) — maximal {MAX_BYTES // (1024 * 1024)} MB erlaubt.")

    data = uploaded_file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"Datei zu groß — maximal {MAX_BYTES // (1024 * 1024)} MB erlaubt.")

    fmt, width, height = detect_image_info(data)
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValueError(
            f"Auflösung zu gering ({width} × {height} px) — mindestens {MIN_WIDTH} × {MIN_HEIGHT} px erforderlich."
        )
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValueError(
            f"Auflösung zu groß ({width} × {height} px) — maximal {MAX_WIDTH} × {MAX_HEIGHT} px erlaubt."
        )
    return data, ALLOWED_EXT_BY_FORMAT[fmt], width, height


def _get_bg_dir(base_dir=None) -> Path:
    root = Path(base_dir) if base_dir is not None else Path(getattr(django_settings, "BASE_DIR", "."))
    return root / "data" / "design_studio_bg"


def _get_tenant_prefix() -> str:
    try:
        from core.router import get_active_tenant
        slug = get_active_tenant()
        if slug:
            clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(slug)).strip("_")
            if clean:
                return f"t_{clean}__"
    except Exception:
        pass
    return "default__"


STANDARD_BG_KEY = "standard"


def is_valid_bg_key(genre_key: str) -> bool:
    return genre_key == STANDARD_BG_KEY or genre_key in GENRE_DEFINITIONS


def _stem_for(user, genre_key: str) -> str:
    uid = getattr(user, "pk", None)
    if not uid or not is_valid_bg_key(genre_key):
        raise ValueError("Ungültiger Benutzer oder unbekanntes Genre.")
    return f"{_get_tenant_prefix()}u{int(uid)}__{genre_key}"


def get_user_genre_bg_path(user, genre_key: str, base_dir=None) -> Path | None:
    if not user or not getattr(user, "is_authenticated", False) or not is_valid_bg_key(genre_key):
        return None
    bg_dir = _get_bg_dir(base_dir)
    if not bg_dir.is_dir():
        return None
    stem = _stem_for(user, genre_key)
    for ext in ("webp", "jpg", "png"):
        cand = bg_dir / f"{stem}.{ext}"
        if cand.is_file():
            return cand
    return None


def get_user_genre_bg_url(user, genre_key: str, base_dir=None) -> str:
    path = get_user_genre_bg_path(user, genre_key, base_dir=base_dir)
    if not path:
        return ""
    try:
        base_url = reverse("design_studio:serve_genre_bg", kwargs={"genre_key": genre_key})
    except Exception:
        base_url = f"/design-studio/genre-bg/{genre_key}/"
    try:
        ver = path.stat().st_mtime_ns
    except OSError:
        ver = 1
    return f"{base_url}?v={ver}"


def get_user_genre_bg_map(user, base_dir=None) -> dict[str, str]:
    if not user or not getattr(user, "is_authenticated", False):
        return {}
    bg_dir = _get_bg_dir(base_dir)
    if not bg_dir.is_dir():
        return {}
    uid = getattr(user, "pk", None)
    if not uid:
        return {}
    prefix = f"{_get_tenant_prefix()}u{int(uid)}__"
    result: dict[str, str] = {}
    for gkey in (*GENRE_DEFINITIONS.keys(), STANDARD_BG_KEY):
        for ext in ("webp", "jpg", "png"):
            cand = bg_dir / f"{prefix}{gkey}.{ext}"
            if cand.is_file():
                try:
                    base_url = reverse("design_studio:serve_genre_bg", kwargs={"genre_key": gkey})
                except Exception:
                    base_url = f"/design-studio/genre-bg/{gkey}/"
                try:
                    ver = cand.stat().st_mtime_ns
                except OSError:
                    ver = 1
                result[gkey] = f"{base_url}?v={ver}"
                break
    return result


def save_user_genre_bg(user, genre_key: str, uploaded_file, base_dir=None) -> dict:
    if not is_valid_bg_key(genre_key):
        raise ValueError("Bitte zuerst ein gültiges Genre auswählen.")
    data, ext, width, height = validate_bg_image(uploaded_file)
    bg_dir = _get_bg_dir(base_dir)
    bg_dir.mkdir(parents=True, exist_ok=True)
    stem = _stem_for(user, genre_key)
    # Remove any previous file for this (tenant, user, genre)
    for old_ext in ("webp", "jpg", "png"):
        old_file = bg_dir / f"{stem}.{old_ext}"
        if old_file.is_file():
            try:
                old_file.unlink()
            except OSError:
                pass
    dest = bg_dir / f"{stem}.{ext}"
    dest.write_bytes(data)
    return {
        "url": get_user_genre_bg_url(user, genre_key, base_dir=base_dir),
        "ext": ext,
        "width": width,
        "height": height,
        "size_bytes": len(data),
    }


def delete_user_genre_bg(user, genre_key: str, base_dir=None) -> bool:
    if not is_valid_bg_key(genre_key):
        return False
    bg_dir = _get_bg_dir(base_dir)
    if not bg_dir.is_dir():
        return False
    stem = _stem_for(user, genre_key)
    removed = False
    for ext in ("webp", "jpg", "png"):
        cand = bg_dir / f"{stem}.{ext}"
        if cand.is_file():
            try:
                cand.unlink()
                removed = True
            except OSError:
                pass
    return removed
