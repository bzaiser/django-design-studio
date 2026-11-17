from django.conf import settings as django_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

MENU_ICON_CHOICES = [
    ("bi-speedometer2", _("Dashboard / Tacho")),
    ("bi-collection", _("Sammlung / Katalog")),
    ("bi-box-seam", _("Objekte / Pakete")),
    ("bi-grid", _("Übersicht / Grid")),
    ("bi-arrow-down-up", _("Transaktionen / Pfeile")),
    ("bi-bank", _("Bank / Finanzen")),
    ("bi-houses", _("Immobilien / Häuser")),
    ("bi-pie-chart", _("Statistik / Torte")),
    ("bi-tags", _("Kategorien / Tags")),
    ("bi-magic", _("Zauberstab / Design")),
    ("bi-search", _("Suche / Lupe")),
    ("bi-folder2-open", _("Dokumente / Ordner")),
    ("bi-gear", _("Einstellungen / Zahnrad")),
    ("bi-palette", _("Design Studio")),
    ("bi-shield-lock", _("Admin / Schild")),
    ("bi-moon-stars", _("Tag / Nacht")),
    ("bi-plus-circle", _("Hinzufügen / Plus")),
    ("bi-star", _("Favorit / Stern")),
    ("bi-question-circle", _("Hilfe")),
    ("bi-info-circle", _("Info")),
]

FALLBACK_MENU_ITEMS = [
    {
        "id": "design_studio",
        "url_name": "design_studio:studio",
        "match_urls": ["studio"],
        "default_label": _("Design Studio"),
        "icon": "bi-palette",
        "zone": "utility",
        "display": "icon_only",
        "visible": True,
        "order": 1,
        "locked": True,
        "staff_only": False,
    },
    {
        "id": "night_mode",
        "url_name": "design_studio:toggle_night",
        "match_urls": [],
        "default_label": _("Tag / Nacht"),
        "icon": "bi-moon-stars",
        "zone": "utility",
        "display": "icon_only",
        "visible": True,
        "order": 2,
        "locked": False,
        "staff_only": False,
    },
]


def get_base_menu_items():
    configured = getattr(django_settings, "DESIGN_STUDIO_MENU_ITEMS", None)
    if isinstance(configured, (list, tuple)) and len(configured) > 0:
        return list(configured)
    return list(FALLBACK_MENU_ITEMS)


def resolve_user_menu(user, saved_menu_config=None):
    base_items = get_base_menu_items()
    saved_list = saved_menu_config if isinstance(saved_menu_config, list) else []
    saved_map = {
        entry.get("id"): entry
        for entry in saved_list
        if isinstance(entry, dict) and entry.get("id")
    }
    is_staff = bool(getattr(user, "is_staff", False))

    resolved = []
    for idx, item in enumerate(base_items):
        if item.get("staff_only") and not is_staff:
            continue
        item_id = item.get("id")
        if not item_id:
            continue
        ov = saved_map.get(item_id, {})
        custom_label = (ov.get("label") or "").strip()
        icon = (ov.get("icon") or "").strip()
        if not icon.startswith("bi-"):
            icon = item.get("icon", "bi-circle")
        default_zone = item.get("zone", "main")
        zone = ov.get("zone") if ov.get("zone") in ("main", "utility") else default_zone
        default_display = item.get("display", "icon_text" if zone == "main" else "icon_only")
        display = ov.get("display") if ov.get("display") in ("icon_text", "icon_only", "text_only") else default_display
        locked = bool(item.get("locked", False))
        visible = True if locked else bool(ov.get("visible", item.get("visible", True)))
        try:
            order = int(ov.get("order", item.get("order", idx + 1)))
        except (TypeError, ValueError):
            order = idx + 1

        url = item.get("url", "#")
        if item.get("url_name"):
            try:
                url = reverse(item["url_name"])
            except Exception:
                url = item.get("url", "#")

        resolved.append({
            "id": item_id,
            "url": url,
            "match_urls": list(item.get("match_urls") or []),
            "default_label": str(item.get("default_label", item_id)),
            "custom_label": custom_label,
            "label": custom_label or str(item.get("default_label", item_id)),
            "icon": icon,
            "zone": zone,
            "display": display,
            "visible": visible,
            "order": order,
            "locked": locked,
        })

    resolved.sort(key=lambda x: (0 if x["zone"] == "main" else 1, x["order"]))
    return {
        "all_items": resolved,
        "main_items": [x for x in resolved if x["visible"] and x["zone"] == "main"],
        "utility_items": [x for x in resolved if x["visible"] and x["zone"] == "utility"],
        "icon_choices": [(ic, str(lbl)) for ic, lbl in MENU_ICON_CHOICES],
    }
