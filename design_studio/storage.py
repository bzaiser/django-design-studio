from django.conf import settings as django_settings
from django.utils.module_loading import import_string

from .engine import DEFAULT_SETTINGS, compute_theme_palette, normalize_settings
from .models import UserThemePreference


class DefaultThemeStorageAdapter:
    """
    Default storage backend using design_studio.models.UserThemePreference.
    Zero coupling to any host app's UserProfile model.
    """

    def get_settings(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return normalize_settings(DEFAULT_SETTINGS)
        pref, _ = UserThemePreference.objects.get_or_create(user=user)
        return normalize_settings(pref.config)

    def save_settings(self, user, settings_dict, palette=None, manual_precision=False):
        norm = normalize_settings(settings_dict)
        if palette is None:
            palette = compute_theme_palette(
                c1=norm["c1"],
                c2=norm["c2"],
                mood_key=norm["mood"],
                bg_mode=norm["bg_mode"],
                bg_custom=norm["bg_custom"],
                state_overrides=norm.get("state_overrides"),
                table_header_color=norm.get("table_header_color", ""),
            )
        pref, _ = UserThemePreference.objects.get_or_create(user=user)
        pref.config = {
            **norm,
            "primary_color": palette["primary_color"],
            "background_color": palette["background_color"],
            "text_color": palette["text_color"],
            "sidebar_bg_color": palette["sidebar_bg_color"],
            "table_header_bg_color": palette["table_header_bg_color"],
            "table_header_text_color": palette["table_header_text_color"],
            "table_body_bg_color": palette["table_body_bg_color"],
            "table_body_text_color": palette["table_body_text_color"],
            "table_border_color": palette["table_border_color"],
        }
        pref.save()
        return palette


def get_storage_adapter():
    adapter_path = getattr(django_settings, "DESIGN_STUDIO_PROFILE_ADAPTER", None)
    if adapter_path:
        cls = import_string(adapter_path)
        return cls()
    return DefaultThemeStorageAdapter()
