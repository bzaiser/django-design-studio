import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape, linebreaks

from .engine import normalize_settings

DEFAULT_CHANNELS = {
    "pdf": {
        "show_logo": True,
        "show_letterhead": True,
        "use_brand_color": True,
        "show_footer": True,
        "show_bank": True,
    },
    "print": {
        "show_header": True,
        "use_brand_color": True,
        "show_footer": True,
    },
    "email": {
        "html_layout": True,
        "show_logo": True,
        "append_signature": True,
    },
    "press": {
        "show_contact": True,
        "show_about": True,
    },
    "web": {
        "sync_site_kit": True,
    },
}


def merge_channels_config(raw: dict | None) -> dict:
    raw = raw if isinstance(raw, dict) else {}
    merged = {}
    for ch, defaults in DEFAULT_CHANNELS.items():
        ch_raw = raw.get(ch) if isinstance(raw.get(ch), dict) else {}
        merged[ch] = {k: bool(ch_raw.get(k, v)) for k, v in defaults.items()}
    return merged


def _resolve_global_colors() -> tuple[str, str]:
    try:
        from django.contrib.auth import get_user_model
        from .models import UserThemePreference

        User = get_user_model()
        staff_pref = (
            UserThemePreference.objects.filter(user__is_staff=True)
            .order_by("-user__is_superuser", "user_id")
            .first()
        )
        if staff_pref and isinstance(staff_pref.config, dict):
            norm = normalize_settings(staff_pref.config)
            return norm.get("c1") or "#2563eb", norm.get("c2") or "#1e40af"
    except Exception:
        pass
    norm = normalize_settings({})
    return norm.get("c1") or "#2563eb", norm.get("c2") or "#1e40af"


def get_branding_context(channel: str = "pdf") -> dict:
    from .models import BrandingProfile

    try:
        bp = BrandingProfile.get_solo()
    except Exception:
        bp = None

    org_name = (getattr(bp, "org_name", "") or "").strip()
    tagline = (getattr(bp, "tagline", "") or "").strip()
    logo_url = ""
    logo_path = ""
    if bp and bp.logo:
        try:
            logo_url = bp.logo.url
            if hasattr(bp.logo, "path") and os.path.isfile(bp.logo.path):
                logo_path = bp.logo.path
        except Exception:
            pass

    if apps.is_installed("site_kit"):
        try:
            from site_kit.models import SiteConfig
            sc = SiteConfig.get_solo()
            if not org_name:
                org_name = (sc.site_name or "").strip()
            if not tagline:
                tagline = (sc.tagline or "").strip()
            if not logo_url and sc.logo:
                logo_url = sc.logo.url
                if hasattr(sc.logo, "path") and os.path.isfile(sc.logo.path):
                    logo_path = sc.logo.path
        except Exception:
            pass

    if not org_name:
        org_name = getattr(settings, "DESIGN_STUDIO_APP_NAME", "") or "Organisation"

    channels = merge_channels_config(getattr(bp, "channels_config_json", None))
    c1, c2 = _resolve_global_colors()
    ch_flags = channels.get(channel, channels["pdf"])

    press_text = (getattr(bp, "press_contact", "") or "").strip()
    press_ref = (getattr(bp, "press_person_ref", "") or "").strip()
    if press_ref.startswith("person:") and apps.is_installed("domain_kit"):
        try:
            pid = int(press_ref.split(":", 1)[1])
            Person = apps.get_model("domain_kit", "Person")
            p_obj = Person.objects.filter(pk=pid).first()
            if p_obj:
                parts = [p_obj.full_name]
                if p_obj.email:
                    parts.append(p_obj.email)
                tel = p_obj.phone or p_obj.mobile
                if tel:
                    parts.append(tel)
                person_line = " · ".join(parts)
                press_text = f"{person_line}\n{press_text}".strip() if press_text else person_line
        except Exception:
            pass

    return {
        "org_name": org_name,
        "tagline": tagline,
        "logo_url": logo_url,
        "logo_path": logo_path,
        "primary_color": c1,
        "secondary_color": c2,
        "address": (getattr(bp, "address", "") or "").strip(),
        "phone": (getattr(bp, "phone", "") or "").strip(),
        "email": (getattr(bp, "email", "") or "").strip(),
        "reply_to_email": (getattr(bp, "reply_to_email", "") or getattr(bp, "email", "") or "").strip(),
        "website": (getattr(bp, "website", "") or "").strip(),
        "tax_id": (getattr(bp, "tax_id", "") or "").strip(),
        "iban": (getattr(bp, "iban", "") or "").strip(),
        "bic": (getattr(bp, "bic", "") or "").strip(),
        "press_person_ref": press_ref,
        "press_contact": press_text,
        "about_short": (getattr(bp, "about_short", "") or "").strip(),
        "email_signature": (getattr(bp, "email_signature", "") or "").strip(),
        "footer_text": (getattr(bp, "footer_text", "") or "").strip(),
        "channels": channels,
        "channel": ch_flags,
    }


def pdf_link_callback(uri: str, rel: str = "") -> str:
    """Resolve /media/ and /static/ URIs to local filesystem paths for xhtml2pdf."""
    if not uri:
        return uri
    if os.path.isfile(uri):
        return uri
    media_url = getattr(settings, "MEDIA_URL", "/media/") or "/media/"
    media_root = getattr(settings, "MEDIA_ROOT", "")
    if media_root and uri.startswith(media_url):
        rel_path = uri[len(media_url):].lstrip("/\\")
        cand = os.path.join(str(media_root), rel_path)
        if os.path.isfile(cand):
            return cand
    static_url = getattr(settings, "STATIC_URL", "/static/") or "/static/"
    static_root = getattr(settings, "STATIC_ROOT", "")
    if uri.startswith(static_url):
        rel_path = uri[len(static_url):].lstrip("/\\")
        if static_root:
            cand = os.path.join(str(static_root), rel_path)
            if os.path.isfile(cand):
                return cand
        found = finders.find(rel_path)
        if found:
            return found[0] if isinstance(found, (list, tuple)) else found
    return uri


def send_branded_email(
    subject: str,
    body: str,
    to: list[str] | None = None,
    bcc: list[str] | None = None,
    reply_to: list[str] | None = None,
    channel: str = "email",
) -> None:
    ctx = get_branding_context(channel)
    flags = ctx["channel"]
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.org")
    if ctx["org_name"] and "<" not in from_email:
        from_email = f"{ctx['org_name']} <{from_email}>"
    rt = reply_to or ([ctx["reply_to_email"]] if ctx["reply_to_email"] else None)

    plain_body = (body or "").strip()
    if flags.get("append_signature") and ctx["email_signature"]:
        plain_body = f"{plain_body}\n\n--\n{ctx['email_signature']}"

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_body,
        from_email=from_email,
        to=to or [getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.org")],
        bcc=bcc or None,
        reply_to=rt,
    )

    if flags.get("html_layout"):
        accent = ctx["primary_color"]
        body_html = linebreaks(escape(body or ""))
        sig_html = (
            f'<div style="margin-top:20px;padding-top:12px;border-top:1px solid #e2e8f0;color:#64748b;font-size:12px;">'
            f"{linebreaks(escape(ctx['email_signature']))}</div>"
            if (flags.get("append_signature") and ctx["email_signature"])
            else ""
        )
        header_html = (
            f'<div style="background:{accent};color:#ffffff;padding:14px 20px;font-weight:bold;font-size:16px;">'
            f"{escape(ctx['org_name'])}"
            f"{(' · ' + escape(ctx['tagline'])) if ctx['tagline'] else ''}"
            f"</div>"
        )
        html_content = (
            '<div style="font-family:Helvetica,Arial,sans-serif;background:#f8fafc;padding:20px;">'
            '<div style="max-width:620px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">'
            f"{header_html}"
            f'<div style="padding:20px;color:#1e293b;font-size:14px;line-height:1.5;">{body_html}{sig_html}</div>'
            "</div></div>"
        )
        msg.attach_alternative(html_content, "text/html")

    msg.send(fail_silently=False)
