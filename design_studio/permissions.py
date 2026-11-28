from __future__ import annotations

from django.apps import apps
from django.conf import settings as django_settings


DEFAULT_ROLE_GROUPS = {
    "management": ("Leitung / Vorstand", "Vorstand", "Geschäftsführung", "Administration"),
    "editorial": ("Redakteur", "Redaktion", "Pressewart", "Leitung / Vorstand", "Vorstand", "Geschäftsführung"),
    "finance": ("Buchhaltung / Kassierer", "Buchhaltung", "Finanzen", "Leitung / Vorstand", "Vorstand", "Geschäftsführung"),
    "hr": ("Personalverantwortlicher", "Personal", "Leitung / Vorstand", "Vorstand", "Geschäftsführung"),
    "calendar_write": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
        "Schriftführer",
        "Dozenten",
    ),
    "calendar_shared": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
        "Schriftführer",
    ),
    "calendar_offerings": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
        "Dozenten",
    ),
    "calendar_billing": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
        "Buchhaltung / Kassierer",
        "Finanzen",
        "Dozenten",
    ),
    "list_manage": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
        "Schriftführer",
        "Redakteur",
        "Pressewart",
        "Mitarbeiter",
    ),
    "form_inbox_manage": (
        "Leitung / Vorstand",
        "Vorstand",
        "Geschäftsführung",
    ),
}

NPO_PROFILES = frozenset({"verein", "club", "association", "npo", "nonprofit", "kunstverein"})


def get_business_profile() -> str:
    """Return normalized business profile from settings or DomainModuleSettings (fallback: 'general')."""
    profile = (
        getattr(django_settings, "APP_BUSINESS_PROFILE", "")
        or getattr(django_settings, "DOMAIN_KIT_BUSINESS_PROFILE", "")
        or getattr(django_settings, "CAL_KIT_BUSINESS_PROFILE", "")
        or ""
    ).strip().lower()
    if not profile and apps.is_installed("domain_kit"):
        try:
            from domain_kit.models import DomainModuleSettings
            profile = (getattr(DomainModuleSettings.get_solo(), "business_profile", "") or "").strip().lower()
        except Exception:
            profile = ""
    return profile or "general"


def is_npo_profile(profile: str | None = None) -> bool:
    """Return True when the active business profile is an association / NPO."""
    p = (profile if profile is not None else get_business_profile()).strip().lower()
    return p in NPO_PROFILES


def get_role_group_names(role_key: str) -> tuple[str, ...]:
    """Return configured group names for a semantic role key, falling back to DEFAULT_ROLE_GROUPS."""
    custom = getattr(django_settings, "APP_ROLE_GROUPS", None)
    if isinstance(custom, dict) and role_key in custom:
        vals = custom[role_key]
        if isinstance(vals, (list, tuple, set)):
            return tuple(str(v) for v in vals)
    return DEFAULT_ROLE_GROUPS.get(role_key, ())


def user_has_role(user, role_key: str, *, allow_when_no_groups: bool = False) -> bool:
    """Central semantic role check across all Baukasten kits."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    if allow_when_no_groups:
        from django.contrib.auth.models import Group
        if not Group.objects.exists():
            return True
    names = get_role_group_names(role_key)
    if not names:
        return False
    return user.groups.filter(name__in=names).exists()
