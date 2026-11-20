import json

from django.conf import settings as django_settings

from .engine import APP_PRESETS, DEFAULT_SETTINGS, compute_theme_palette, normalize_settings
from .genres import GENRE_CHOICES, GENRE_DEFINITIONS, resolve_request_genre
from .menu import compute_system_hub_state, resolve_user_menu
from .storage import get_storage_adapter


def theme_context(request):
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        adapter = get_storage_adapter()
        ts = adapter.get_settings(user)
    else:
        ts = normalize_settings(DEFAULT_SETTINGS)

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
        "nav_main_items": user_menu["main_items"],
        "nav_utility_items": user_menu["utility_items"],
        "nav_system_items": system_items,
        "nav_system_active": system_active,
        "nav_system_entry_url": system_entry_url,
        "menu_studio_items": user_menu["all_items"],
        "menu_icon_choices": user_menu["icon_choices"],
        "genre_choices": [(gk, str(gl)) for gk, gl in GENRE_CHOICES],
        "active_genre": active_genre,
        "genre_preview_json": json.dumps({
            k: {
                "primary": v["primary"],
                "secondary": v["secondary"],
                "bg_light": v["bg_light"],
                "svg": v["svg"],
                "photo_url": v["photo_url"],
            }
            for k, v in GENRE_DEFINITIONS.items()
        }),
        "design_studio_app_name": ts.get("brand_title") or getattr(django_settings, "DESIGN_STUDIO_APP_NAME", "App"),
        "design_studio_app_icon": ts.get("brand_icon") or getattr(django_settings, "DESIGN_STUDIO_APP_ICON", "bi-speedometer2"),
        "design_studio_pwa_enabled": bool(getattr(django_settings, "DESIGN_STUDIO_PWA_ENABLED", True)),
    }
