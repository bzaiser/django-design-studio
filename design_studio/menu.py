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
    try:
        from django.apps import apps
        if apps.is_installed("domain_kit"):
            _dms_model = apps.get_model("domain_kit", "DomainModuleSettings")
            if _dms_model and hasattr(_dms_model, "get_solo"):
                domain_settings = _dms_model.get_solo()
    except Exception:
        domain_settings = None

    resolved = []
    for idx, item in enumerate(base_items):
        if item.get("staff_only") and not is_staff:
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
            "genre": genre,
        })

    zone_rank = {"main": 0, "utility": 1, "system": 2}
    resolved.sort(key=lambda x: (zone_rank.get(x["zone"], 1), x["order"]))
    return {
        "all_items": resolved,
        "main_items": [x for x in resolved if x["visible"] and x["zone"] == "main"],
        "utility_items": [x for x in resolved if x["visible"] and x["zone"] == "utility"],
        "system_items": [x for x in resolved if x["visible"] and x["zone"] == "system"],
        "icon_choices": [(ic, str(lbl)) for ic, lbl in MENU_ICON_CHOICES],
        "genre_choices": [(gk, str(gl)) for gk, gl in GENRE_CHOICES],
    }
