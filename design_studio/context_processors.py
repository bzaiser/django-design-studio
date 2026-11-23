import json

from django.conf import settings as django_settings

from .bg_media import get_user_genre_bg_map
from .engine import APP_PRESETS, DEFAULT_SETTINGS, compute_theme_palette, normalize_settings
from .genres import GENRE_CHOICES, GENRE_DEFINITIONS, resolve_request_genre
from .menu import compute_system_hub_state, resolve_user_menu
from .storage import get_storage_adapter


def _resolve_site_admin_theme(adapter, default_norm):
    try:
        from django.contrib.auth import get_user_model

        staff_users = list(
            get_user_model()
            .objects.filter(is_staff=True, is_active=True)
            .order_by("-is_superuser", "-last_login", "id")[:10]
        )
        for su in staff_users:
            su_ts = adapter.get_settings(su)
            if su_ts != default_norm:
                return su, su_ts
        if staff_users:
            return staff_users[0], adapter.get_settings(staff_users[0])
    except Exception:
        pass
    return None, default_norm


def theme_context(request):
    user = getattr(request, "user", None)
    is_auth = bool(user and getattr(user, "is_authenticated", False))
    adapter = get_storage_adapter()
    default_norm = normalize_settings(DEFAULT_SETTINGS)
    if is_auth:
        ts = adapter.get_settings(user)
    else:
        ts = dict(default_norm)

    site_user = None
    site_ts = default_norm
    if not getattr(user, "is_staff", False):
        site_user, site_ts = _resolve_site_admin_theme(adapter, default_norm)
        if ts == default_norm:
            ts = dict(site_ts)
        else:
            ts = dict(ts)
            for shared_key in ("brand_title", "brand_icon", "default_genre", "menu_config"):
                if not ts.get(shared_key) and site_ts.get(shared_key):
                    ts[shared_key] = site_ts[shared_key]

    if not ts.get("brand_title"):
        try:
            from django.apps import apps
            if apps.is_installed("site_kit"):
                from site_kit.models import SiteConfig
                sname = (SiteConfig.get_solo().site_name or "").strip()
                if sname and sname != "Mein Verein":
                    ts = {**ts, "brand_title": sname}
        except Exception:
            pass

    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
        table_header_color=ts.get("table_header_color", ""),
    )
    user_menu = resolve_user_menu(user, saved_menu_config=ts.get("menu_config"))
    system_items, system_active, system_entry_url = compute_system_hub_state(request, user_menu["system_items"])
    active_genre = resolve_request_genre(request, user_menu["all_items"], default_genre=ts.get("default_genre", ""))
    custom_genre_bgs = get_user_genre_bg_map(user) if is_auth else {}
    if not custom_genre_bgs and site_user is not None:
        custom_genre_bgs = get_user_genre_bg_map(site_user)
    if active_genre and active_genre.get("key") in custom_genre_bgs:
        active_genre = {**active_genre, "custom_photo_url": custom_genre_bgs[active_genre["key"]]}

    return {
        "theme_studio": ts,
        "theme_palette": palette,
        "theme_state_overrides_json": json.dumps(ts.get("state_overrides", {})),
        "theme_palette_json": json.dumps({
            "mood": palette["mood"],
            "is_dark": palette["is_dark"],
            "brutal": palette["brutal"],
            "glow": palette["glow"],
            "sync_cards_and_charts": ts.get("sync_cards_and_charts", True),
            "states": palette["states"],
        }),
        "design_studio_presets": [
            {"key": k, **v} for k, v in APP_PRESETS.items()
        ],
        "nav_main_items": user_menu["main_items"] if is_auth else [],
        "nav_utility_items": user_menu["utility_items"] if is_auth else [],
        "nav_system_items": system_items if is_auth else [],
        "nav_system_active": system_active if is_auth else False,
        "nav_system_entry_url": system_entry_url if is_auth else "",
        "nav_system_has_updates": bool(user_menu.get("has_updates")) if is_auth else False,
        "nav_has_notify_item": bool(user_menu.get("has_notify_item")) if is_auth else False,
        "ds_unread_notifications_count": int(user_menu.get("unread_notifications_count") or 0) if is_auth else 0,
        "menu_studio_items": user_menu["all_items"],
        "menu_icon_choices": user_menu["icon_choices"],
        "genre_choices": [(gk, str(gl)) for gk, gl in GENRE_CHOICES],
        "active_genre": active_genre,
        "genre_preview_json": json.dumps({
            k: {
                "label": str(v["label"]),
                "primary": v["primary"],
                "secondary": v["secondary"],
                "bg_light": v["bg_light"],
                "svg": v["svg"],
                "photo_url": v["photo_url"],
                "custom_photo_url": custom_genre_bgs.get(k, ""),
            }
            for k, v in GENRE_DEFINITIONS.items()
        }),
        "design_studio_app_name": ts.get("brand_title") or getattr(django_settings, "DESIGN_STUDIO_APP_NAME", "App"),
        "design_studio_app_icon": ts.get("brand_icon") or getattr(django_settings, "DESIGN_STUDIO_APP_ICON", "bi-speedometer2"),
        "design_studio_pwa_enabled": bool(getattr(django_settings, "DESIGN_STUDIO_PWA_ENABLED", True)),
    }
