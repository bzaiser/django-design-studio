import re

from django.conf import settings as django_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .genres import GENRE_CHOICES, is_valid_genre

BI_ICON_RE = re.compile(r"^bi-[a-z0-9-]+$")


def is_valid_bi_icon(value: str) -> bool:
    return bool(isinstance(value, str) and BI_ICON_RE.match(value.strip()))


MENU_ICON_CHOICES = [
    # Dashboard & Navigation
    ("bi-speedometer2", _("Dashboard / Tacho")),
    ("bi-house", _("Startseite / Haus")),
    ("bi-house-door", _("Home / Tür")),
    ("bi-grid", _("Übersicht / Grid")),
    ("bi-grid-1x2", _("Layout / Kacheln")),
    ("bi-grid-3x3-gap", _("Apps / Kachel-Menü")),
    ("bi-columns-gap", _("Bento / Spalten")),
    ("bi-compass", _("Navigation / Kompass")),
    ("bi-map", _("Karte / Übersicht")),
    ("bi-signpost-split", _("Wegweiser")),
    ("bi-menu-button-wide", _("Menü / Liste")),
    ("bi-list-ul", _("Liste")),
    ("bi-list-check", _("Checkliste")),
    ("bi-kanban", _("Kanban / Board")),
    ("bi-window", _("Fenster / App")),
    ("bi-app-indicator", _("App-Badge")),
    # Finanzen & Business
    ("bi-bank", _("Bank / Finanzen")),
    ("bi-cash-stack", _("Bargeld / Umsatz")),
    ("bi-cash-coin", _("Zahlung / Münze")),
    ("bi-currency-euro", _("Euro")),
    ("bi-currency-dollar", _("Dollar")),
    ("bi-credit-card", _("Kreditkarte")),
    ("bi-wallet2", _("Portemonnaie / Konto")),
    ("bi-piggy-bank", _("Sparen / Rücklagen")),
    ("bi-receipt", _("Beleg / Rechnung")),
    ("bi-receipt-cutoff", _("Quittung / Buchung")),
    ("bi-calculator", _("Rechner / Kalkulation")),
    ("bi-percent", _("Prozent / Steuern")),
    ("bi-briefcase", _("Business / Projekt")),
    ("bi-building", _("Firma / Gebäude")),
    ("bi-shop", _("Shop / Laden")),
    ("bi-cart3", _("Warenkorb / Einkauf")),
    ("bi-bag", _("Bestellung / Tasche")),
    ("bi-award", _("Auszeichnung / Ziel")),
    # Statistik & Charts
    ("bi-pie-chart", _("Kreisdiagramm")),
    ("bi-bar-chart", _("Balkendiagramm")),
    ("bi-bar-chart-line", _("Balken & Linie")),
    ("bi-graph-up", _("Wachstum / Trend")),
    ("bi-graph-up-arrow", _("Steigung / Kurs")),
    ("bi-graph-down", _("Abnahme / Trend")),
    ("bi-activity", _("Aktivität / Puls")),
    ("bi-clipboard-data", _("Bericht / Daten")),
    ("bi-file-earmark-bar-graph", _("Auswertung / Report")),
    # Objekte, Inventar & Immobilien
    ("bi-collection", _("Sammlung / Katalog")),
    ("bi-box-seam", _("Objekte / Pakete")),
    ("bi-boxes", _("Lager / Bestände")),
    ("bi-archive", _("Archiv")),
    ("bi-houses", _("Immobilien / Häuser")),
    ("bi-key", _("Schlüssel / Zugang")),
    ("bi-truck", _("Lieferung / Transport")),
    ("bi-car-front", _("Fahrzeug / Fuhrpark")),
    ("bi-tools", _("Werkzeug / Wartung")),
    ("bi-wrench-adjustable", _("Reparatur / Service")),
    ("bi-hammer", _("Bau / Handwerk")),
    ("bi-lightbulb", _("Energie / Idee")),
    ("bi-lightning-charge", _("Strom / Schnell")),
    ("bi-thermometer-half", _("Temperatur / Sensor")),
    ("bi-droplet", _("Wasser / Verbrauch")),
    # Dokumente, Dateien & Medien
    ("bi-folder2-open", _("Dokumente / Ordner")),
    ("bi-folder", _("Ordner")),
    ("bi-file-earmark-text", _("Textdokument")),
    ("bi-file-earmark-pdf", _("PDF-Datei")),
    ("bi-file-earmark-spreadsheet", _("Tabelle / Excel")),
    ("bi-file-earmark-code", _("Code-Datei")),
    ("bi-file-earmark-zip", _("ZIP / Backup")),
    ("bi-journal-text", _("Journal / Notizen")),
    ("bi-book", _("Handbuch / Wissen")),
    ("bi-bookmark", _("Lesezeichen")),
    ("bi-paperclip", _("Anhang")),
    ("bi-images", _("Bilder / Galerie")),
    ("bi-camera", _("Kamera / Foto")),
    ("bi-film", _("Video / Film")),
    ("bi-music-note-beamed", _("Musik / Audio")),
    ("bi-printer", _("Drucken")),
    # Technik, Server, NAS & Entwicklung
    ("bi-hdd-stack", _("NAS / Festplatten")),
    ("bi-hdd-network", _("Netzwerk-Speicher")),
    ("bi-server", _("Server")),
    ("bi-cpu", _("Prozessor / System")),
    ("bi-memory", _("RAM / Speicher")),
    ("bi-database", _("Datenbank")),
    ("bi-cloud", _("Cloud")),
    ("bi-cloud-arrow-up", _("Upload / Sync")),
    ("bi-cloud-arrow-down", _("Download")),
    ("bi-cloud-check", _("Cloud OK / Backup")),
    ("bi-router", _("Router / Netzwerk")),
    ("bi-wifi", _("WLAN")),
    ("bi-ethernet", _("LAN / Kabel")),
    ("bi-globe", _("Web / Internet")),
    ("bi-terminal", _("Terminal / CLI")),
    ("bi-code-slash", _("Code / API")),
    ("bi-braces", _("JSON / Config")),
    ("bi-git", _("Git / Versionierung")),
    ("bi-bug", _("Debug / Fehler")),
    ("bi-plug", _("Integration / Plugin")),
    ("bi-usb-drive", _("USB / Laufwerk")),
    # Zeit, Kalender & Aufgaben
    ("bi-calendar3", _("Kalender")),
    ("bi-calendar-check", _("Termin / Erledigt")),
    ("bi-calendar-event", _("Event / Frist")),
    ("bi-clock", _("Uhr / Zeit")),
    ("bi-stopwatch", _("Stoppuhr / Laufzeit")),
    ("bi-hourglass-split", _("Wartezeit / Verlauf")),
    ("bi-alarm", _("Wecker / Erinnerung")),
    ("bi-check2-square", _("Aufgabe / Todo")),
    ("bi-check-circle", _("Erledigt / OK")),
    # Nutzer, Teams & Sicherheit
    ("bi-person", _("Benutzer / Profil")),
    ("bi-person-circle", _("Konto / Avatar")),
    ("bi-people", _("Team / Gruppen")),
    ("bi-person-badge", _("Ausweis / Rolle")),
    ("bi-person-gear", _("Benutzer-Einstellung")),
    ("bi-shield-lock", _("Admin / Sicherheit")),
    ("bi-shield-check", _("Geschützt / Geprüft")),
    ("bi-lock", _("Gesperrt / Privat")),
    ("bi-unlock", _("Freigegeben")),
    ("bi-fingerprint", _("Biometrie / Auth")),
    ("bi-eye", _("Ansicht / Vorschau")),
    ("bi-incognito", _("Privat / Inkognito")),
    # Kommunikation & Benachrichtigungen
    ("bi-envelope", _("E-Mail / Postfach")),
    ("bi-send", _("Senden")),
    ("bi-chat-dots", _("Chat / Kommentare")),
    ("bi-bell", _("Benachrichtigungen")),
    ("bi-megaphone", _("Ankündigung")),
    ("bi-rss", _("Feed / Updates")),
    ("bi-share", _("Teilen")),
    # Design, Theme & Kategorien
    ("bi-palette", _("Design Studio")),
    ("bi-brush", _("Pinsel / Stil")),
    ("bi-magic", _("Zauberstab / Design")),
    ("bi-stars", _("KI / Highlights")),
    ("bi-sparkles", _("Effekte / Neu")),
    ("bi-moon-stars", _("Tag / Nacht")),
    ("bi-sun", _("Tagmodus / Sonne")),
    ("bi-droplet-half", _("Kontrast / Farbe")),
    ("bi-sliders", _("Regler / Filter")),
    ("bi-toggles", _("Schalter / Optionen")),
    ("bi-tags", _("Kategorien / Tags")),
    ("bi-tag", _("Etikett / Label")),
    # Aktionen, Status & Sonstiges
    ("bi-search", _("Suche / Lupe")),
    ("bi-funnel", _("Filter")),
    ("bi-arrow-down-up", _("Transaktionen / Sortieren")),
    ("bi-arrow-repeat", _("Aktualisieren / Sync")),
    ("bi-plus-circle", _("Hinzufügen / Plus")),
    ("bi-dash-circle", _("Entfernen / Minus")),
    ("bi-pencil-square", _("Bearbeiten")),
    ("bi-trash3", _("Papierkorb / Löschen")),
    ("bi-gear", _("Einstellungen / Zahnrad")),
    ("bi-star", _("Favorit / Stern")),
    ("bi-heart", _("Gemocht / Gesundheit")),
    ("bi-bookmark-star", _("Wichtig")),
    ("bi-flag", _("Markierung / Flagge")),
    ("bi-pin-angle", _("Angeheftet")),
    ("bi-rocket-takeoff", _("Start / Schnellstart")),
    ("bi-trophy", _("Erfolg / Rangliste")),
    ("bi-exclamation-triangle", _("Warnung")),
    ("bi-question-circle", _("Hilfe")),
    ("bi-info-circle", _("Info")),
    ("bi-box-arrow-right", _("Abmelden / Export")),
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


SYSTEM_HUB_ITEM_IDS = set()


def compute_system_hub_state(request, system_items):
    """Mark active item in system_items and return (items_with_active, is_any_active, entry_url)."""
    req_path = (getattr(request, "path", "") or "").rstrip("/") or "/"
    resolver_match = getattr(request, "resolver_match", None)
    req_url_name = getattr(resolver_match, "url_name", "") or ""
    req_view_name = getattr(resolver_match, "view_name", "") or ""

    enriched = []
    any_active = False
    for item in system_items:
        item_url = (item.get("url") or "").rstrip("/") or "/"
        match_urls = item.get("match_urls") or []
        is_active = (
            (item_url != "#" and req_path == item_url)
            or (req_url_name and req_url_name in match_urls)
            or (req_view_name and req_view_name in match_urls)
        )
        if is_active:
            any_active = True
        enriched.append({**item, "is_active": bool(is_active)})

    entry_url = enriched[0]["url"] if enriched else ""
    return enriched, any_active, entry_url


def resolve_user_menu(user, saved_menu_config=None):
    base_items = get_base_menu_items()
    saved_list = saved_menu_config if isinstance(saved_menu_config, list) else []
    saved_map = {
        entry.get("id"): entry
        for entry in saved_list
        if isinstance(entry, dict) and entry.get("id")
    }
    is_staff = bool(getattr(user, "is_staff", False))
    has_profile_hub = any(
        isinstance(it, dict) and it.get("id") in ("profile", "settings")
        for it in base_items
    )

    domain_settings = None
    notify_badge = {"count": 0, "level": "danger", "latest_title": ""}
    ops_has_updates = False
    is_auth = bool(user and getattr(user, "is_authenticated", False))
    try:
        from django.apps import apps
    except Exception:
        apps = None

    if apps is not None:
        try:
            if apps.is_installed("domain_kit"):
                _dms_model = apps.get_model("domain_kit", "DomainModuleSettings")
                if _dms_model and hasattr(_dms_model, "get_solo"):
                    domain_settings = _dms_model.get_solo()
        except Exception:
            domain_settings = None

        try:
            if apps.is_installed("notify_kit"):
                has_notify_item = any(
                    isinstance(it, dict) and (it.get("id") == "notifications" or str(it.get("url_name") or "").startswith("notify_kit:"))
                    for it in base_items
                )
                if not has_notify_item:
                    base_items.append({
                        "id": "notifications",
                        "url_name": "notify_kit:inbox",
                        "match_urls": ["inbox"],
                        "default_label": _("Meldungen"),
                        "icon": "bi-bell",
                        "zone": "utility",
                        "display": "icon_only",
                        "visible": True,
                        "order": 1,
                    })
                if is_auth:
                    _notif_model = apps.get_model("notify_kit", "Notification")
                    if _notif_model:
                        unread_rows = list(
                            _notif_model.objects.filter(user=user, is_read=False)
                            .order_by("-created_at")
                            .values_list("title", "level")[:15]
                        )
                        if unread_rows:
                            notify_badge["count"] = (
                                len(unread_rows)
                                if len(unread_rows) < 15
                                else _notif_model.objects.filter(user=user, is_read=False).count()
                            )
                            notify_badge["latest_title"] = str(unread_rows[0][0] or "").strip()
                            levels = {str(r[1] or "").lower() for r in unread_rows}
                            if "danger" in levels or "error" in levels:
                                notify_badge["level"] = "danger"
                            elif "warning" in levels:
                                notify_badge["level"] = "warning"
                            else:
                                notify_badge["level"] = "primary"
        except Exception:
            pass

        try:
            if is_auth and is_staff and apps.is_installed("ops_kit"):
                _upd_model = apps.get_model("ops_kit", "UpdateSettings")
                if _upd_model and hasattr(_upd_model, "get_solo"):
                    ucfg = _upd_model.get_solo()
                    res_json = getattr(ucfg, "last_result_json", None) or {}
                    if isinstance(res_json, dict) and res_json.get("has_updates"):
                        ops_has_updates = True
        except Exception:
            pass

    if domain_settings is not None:
        existing_domain_urls = {
            item.get("url_name") for item in base_items if isinstance(item, dict) and item.get("url_name")
        }
        canonical_domain_items = [
            {
                "id": "master_data",
                "url_name": "domain_kit:settings",
                "match_urls": ["settings"],
                "default_label": _("Stammdaten"),
                "icon": "bi-tags",
                "zone": "main",
                "display": "icon_text",
                "visible": True,
                "order": 20,
                "module_key": "master_data",
            },
            {
                "id": "persons",
                "url_name": "domain_kit:persons",
                "match_urls": ["persons"],
                "default_label": _("Personen"),
                "icon": "bi-people",
                "zone": "main",
                "display": "icon_text",
                "visible": True,
                "order": 21,
                "module_key": "persons",
            },
            {
                "id": "assets",
                "url_name": "domain_kit:assets",
                "match_urls": ["assets"],
                "default_label": _("Assets"),
                "icon": "bi-boxes",
                "zone": "main",
                "display": "icon_text",
                "visible": True,
                "order": 22,
                "module_key": "assets",
            },
            {
                "id": "documents",
                "url_name": "domain_kit:documents",
                "match_urls": ["documents"],
                "default_label": _("Dokumente"),
                "icon": "bi-folder2-open",
                "zone": "main",
                "display": "icon_text",
                "visible": True,
                "order": 23,
                "module_key": "documents",
            },
            {
                "id": "search",
                "url_name": "domain_kit:search",
                "match_urls": ["search"],
                "default_label": _("Suche"),
                "icon": "bi-search",
                "zone": "main",
                "display": "icon_text",
                "visible": True,
                "order": 24,
                "module_key": "global_search",
            },
        ]
        for c_item in canonical_domain_items:
            if c_item["url_name"] not in existing_domain_urls:
                if domain_settings.is_module_enabled(c_item["module_key"]):
                    base_items.append(c_item)

    if apps is not None:
        existing_ids = {
            item.get("id") for item in base_items if isinstance(item, dict) and item.get("id")
        }
        existing_urls = {
            item.get("url_name") for item in base_items if isinstance(item, dict) and item.get("url_name")
        }
        optional_kit_items = []
        try:
            if apps.is_installed("cal_kit"):
                cal_label = _("Kalender")
                try:
                    from cal_kit.services import get_cal_profile_labels
                    cal_label = get_cal_profile_labels().get("menu_label") or cal_label
                except Exception:
                    pass
                optional_kit_items.append({
                    "id": "calendar",
                    "url_name": "cal_kit:calendar",
                    "match_urls": ["calendar", "offering_list", "billing_overview", "event_billing"],
                    "default_label": cal_label,
                    "icon": "bi-calendar3",
                    "zone": "main",
                    "display": "icon_text",
                    "visible": True,
                    "order": 25,
                })
        except Exception:
            pass
        try:
            if apps.is_installed("list_kit"):
                optional_kit_items.extend([
                    {
                        "id": "lists",
                        "url_name": "list_kit:collection_list",
                        "match_urls": ["collection_list", "collection_detail"],
                        "default_label": _("Listen"),
                        "icon": "bi-list-check",
                        "zone": "main",
                        "display": "icon_text",
                        "visible": True,
                        "order": 26,
                    },
                    {
                        "id": "list_builder",
                        "url_name": "list_kit:builder_list",
                        "match_urls": ["builder_list", "builder_edit", "builder_create"],
                        "default_label": _("Listen-Builder"),
                        "icon": "bi-ui-checks-grid",
                        "zone": "main",
                        "display": "icon_text",
                        "visible": True,
                        "order": 27,
                        "staff_only": True,
                    },
                ])
        except Exception:
            pass
        try:
            if apps.is_installed("site_kit"):
                optional_kit_items.extend([
                    {
                        "id": "site_cockpit",
                        "url_name": "site_kit:cockpit",
                        "match_urls": ["cockpit"],
                        "default_label": _("Redaktion"),
                        "icon": "bi-pencil-square",
                        "zone": "main",
                        "display": "icon_text",
                        "visible": True,
                        "order": 27,
                        "editorial_or_staff": True,
                    },
                    {
                        "id": "site_manage",
                        "url_name": "site_kit:manage",
                        "match_urls": ["manage", "page_create", "page_edit"],
                        "default_label": _("Webseite"),
                        "icon": "bi-globe2",
                        "zone": "main",
                        "display": "icon_text",
                        "visible": True,
                        "order": 28,
                        "editorial_or_staff": True,
                    },
                ])
        except Exception:
            pass
        for opt_item in optional_kit_items:
            if opt_item["id"] not in existing_ids and opt_item["url_name"] not in existing_urls:
                base_items.append(opt_item)
                existing_ids.add(opt_item["id"])
                existing_urls.add(opt_item["url_name"])

    is_editorial = is_staff
    if not is_editorial and user and getattr(user, "is_authenticated", False):
        try:
            is_editorial = user.groups.filter(
                name__in=("Redakteur", "Redaktion", "Leitung / Vorstand", "Vorstand")
            ).exists()
        except Exception:
            is_editorial = False

    get_mod_access = None
    if domain_settings is not None and user and getattr(user, "is_authenticated", False):
        try:
            from domain_kit.services import get_module_access
            get_mod_access = get_module_access
        except Exception:
            get_mod_access = None

    resolved = []
    for idx, item in enumerate(base_items):
        if item.get("staff_only") and not is_staff:
            continue
        if item.get("editorial_or_staff") and not is_editorial:
            continue
        item_id = item.get("id")
        if not item_id:
            continue
        if item_id == "design_studio" and has_profile_hub:
            continue

        if domain_settings is not None:
            url_name = str(item.get("url_name") or "")
            if url_name.startswith("domain_kit:"):
                mod_part = url_name.split(":", 1)[1]
                target_mod = {
                    "persons": "persons",
                    "person_photo": "persons",
                    "assets": "assets",
                    "documents": "documents",
                    "document_view": "documents",
                    "document_preview": "documents",
                    "document_download": "documents",
                    "search": "global_search",
                    "settings": "master_data",
                }.get(mod_part)
                if target_mod and not domain_settings.is_module_enabled(target_mod):
                    continue
                if target_mod and get_mod_access is not None and get_mod_access(user, target_mod) == "none":
                    continue
        ov = saved_map.get(item_id, {})
        custom_label = (ov.get("label") or "").strip()
        icon = (ov.get("icon") or "").strip()
        if not is_valid_bi_icon(icon):
            icon = item.get("icon", "bi-circle")
        if item_id in SYSTEM_HUB_ITEM_IDS:
            zone = "main" if ov.get("zone") == "main" else "system"
        else:
            default_zone = item.get("zone", "main")
            zone = ov.get("zone") if ov.get("zone") in ("main", "utility", "system") else default_zone
        default_display = item.get("display", "icon_text" if zone == "main" else "icon_only")
        display = ov.get("display") if ov.get("display") in ("icon_text", "icon_only", "text_only") else default_display
        locked = bool(item.get("locked", False))
        visible = True if locked else bool(ov.get("visible", item.get("visible", True)))
        raw_genre = ov.get("genre") if is_valid_genre(ov.get("genre")) else item.get("genre", "")
        genre = raw_genre if is_valid_genre(raw_genre) else ""
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

        label_text = custom_label or str(item.get("default_label", item_id))
        badge_count = int(item.get("badge_count") or 0)
        badge_dot = bool(item.get("badge_dot", False))
        badge_level = str(item.get("badge_level") or "danger")
        badge_tooltip = ""

        url_name_str = str(item.get("url_name") or "")
        if item_id == "notifications" or url_name_str.startswith("notify_kit:"):
            if notify_badge["count"] > 0:
                badge_count = notify_badge["count"]
                badge_level = notify_badge["level"]
                if icon == "bi-bell":
                    icon = "bi-bell-fill"
                latest = notify_badge["latest_title"]
                badge_tooltip = (
                    f"{label_text} ({badge_count} ungelesen – {latest})"
                    if latest
                    else f"{label_text} ({badge_count} ungelesen)"
                )
        elif ops_has_updates and item_id in ("profile", "settings", "design_studio", "ops_updates"):
            badge_dot = True
            badge_level = "warning"
            badge_tooltip = f"{label_text} (Neue Updates verfügbar)"

        resolved.append({
            "id": item_id,
            "url": url,
            "match_urls": list(item.get("match_urls") or []),
            "default_label": str(item.get("default_label", item_id)),
            "custom_label": custom_label,
            "label": label_text,
            "icon": icon,
            "zone": zone,
            "display": display,
            "visible": visible,
            "order": order,
            "locked": locked,
            "genre": genre,
            "badge_count": badge_count,
            "badge_dot": badge_dot,
            "badge_level": badge_level,
            "badge_tooltip": badge_tooltip,
        })

    zone_rank = {"main": 0, "utility": 1, "system": 2}
    resolved.sort(key=lambda x: (zone_rank.get(x["zone"], 1), x["order"]))
    has_visible_notify = any(
        x["visible"] and (x["id"] == "notifications" or "inbox" in (x.get("match_urls") or []))
        for x in resolved
    )
    return {
        "all_items": resolved,
        "main_items": [x for x in resolved if x["visible"] and x["zone"] == "main"],
        "utility_items": [x for x in resolved if x["visible"] and x["zone"] == "utility"],
        "system_items": [x for x in resolved if x["visible"] and x["zone"] == "system"],
        "has_updates": ops_has_updates,
        "has_notify_item": has_visible_notify,
        "unread_notifications_count": notify_badge["count"],
        "icon_choices": [(ic, str(lbl)) for ic, lbl in MENU_ICON_CHOICES],
        "genre_choices": [(gk, str(gl)) for gk, gl in GENRE_CHOICES],
    }
