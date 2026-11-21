# django-design-studio

Wiederverwendbares Design- & Menü-Studio-Add-in für Django + Bootstrap 5 (+ optional Chart.js & HTMX).

## Features
- **16 Design-Stimmungen** & **8-Zustände semantische Farbharmonie** (`--theme-state-1` .. `--theme-state-8`)
- **5 Karten-Oberflächen**: `liquid` (Liquid Glass), `tinted` (Farbharmonie-Milchglas), `glass` (Edles Milchglas), `solid` (Vollton), `brutal` (Kontrast-Kante)
- **5 Adaptive Seiten-SVG-Hintergründe** (`topography`, `grid`, `curves`, `aura`, `brutal_grid`, `none`) & **App-/Seiten-Genres** inkl. Upload eigener Hintergrundbilder pro Genre (Client- & Server-Prüfung: JPG/PNG/WebP, max. 5 MB, 640×360 bis 6000×6000 px, persistent unter `data/design_studio_bg/`)
- **KPI-Karten 2.0**: SVG-Sparklines, segmentierte Ziel-Fortschrittsbalken, Watermark-Icons, Maus-Spotlight, Bento-Grid (`sm`/`md`/`lg`)
- **Menü-Studio**: Top-Leiste oder einklappbares Seitenpanel (`sidebar`), Glass/Gradient-Stil, gleitende Hover-Pille, Drag & Drop-Sortierung, umbenennbare Menütexte, Icon-Auswahl, `Icon + Text` / `Nur Icon` / `Nur Text` pro Punkt
- **Globale Tabellen-, Card-, Modal- & Chart.js-Harmonisierung** (Hell & Dunkel)
- **Tag/Nacht-Umschalter** im Menü synchron mit dem Design Studio
- **JSON Theme Export / Import** & vorgefertigte App-Vorlagen

## Schnellstart (3 Schritte)

1. Installieren:
```bash
pip install --no-user --upgrade --no-cache-dir git+https://github.com/bzaiser/django-design-studio.git@main
```

2. `settings.py` & `urls.py`:
```python
INSTALLED_APPS = [..., "design_studio"]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "design_studio.context_processors.theme_context",
]

DESIGN_STUDIO_APP_NAME = "Meine App"
DESIGN_STUDIO_MENU_ITEMS = [
    {"id": "home", "url_name": "home", "match_urls": ["home"], "default_label": "Übersicht", "icon": "bi-speedometer2", "zone": "main", "display": "icon_text", "visible": True, "order": 1},
    {"id": "design_studio", "url_name": "design_studio:studio", "match_urls": ["studio"], "default_label": "Design Studio", "icon": "bi-palette", "zone": "utility", "display": "icon_only", "visible": True, "order": 1, "locked": True},
    {"id": "night_mode", "url_name": "design_studio:toggle_night", "match_urls": [], "default_label": "Tag / Nacht", "icon": "bi-moon-stars", "zone": "utility", "display": "icon_only", "visible": True, "order": 2},
]

# urls.py
path("design-studio/", include("design_studio.urls")),
```

3. `base.html` einbinden:
```django
<html lang="de" data-bs-theme="{% if theme_palette.is_dark %}dark{% else %}light{% endif %}">
<head>
    ...
    {% include "design_studio/includes/head.html" %}
</head>
<body {% include "design_studio/includes/body_attrs.html" %}>
    {% include "design_studio/includes/bg_layer.html" %}
    {% include "design_studio/includes/navbar.html" %}
    <main class="container py-4">{% block content %}{% endblock %}</main>
    {% include "design_studio/includes/scripts.html" %}
</body>
</html>
```

*(Hinweis: Keine lokalen Kopien unter `templates/design_studio/` anlegen, sonst werden Paket-Updates überschrieben.)*

## Starter-Layouts für neue Apps (kein Überschreibungsrisiko)

Neue Apps können direkt von den mitgelieferten Paket-Layouts erben (bestehende Apps mit eigener `base.html` bleiben unberührt):

- `design_studio/layouts/base.html` (Komplettes Grundgerüst mit Bootstrap 5, SVG-Layer, Navbar/Sidebar & Messages)
- `design_studio/layouts/dashboard.html` (Bento-KPI-Grid + Chart-/Tabellen-Blöcke)
- `design_studio/layouts/list_page.html` (Seitentitel, Action-Buttons, Filter & responsive Tabelle)
- `design_studio/components/kpi_card.html` (KPI-2.0-Karte mit Sparkline, Fortschrittsbalken, Watermark & Spotlight)

```django
{% extends "design_studio/layouts/dashboard.html" %}
{% block kpi_cards %}
    {% include "design_studio/components/kpi_card.html" with title="Umsatz" value="12.450" unit="€" icon="bi-cash-stack" size="md" %}
{% endblock %}
```

Optionales Erzeugen lokaler Starter-Dateien (überspringt bestehende Dateien automatisch):
```bash
python manage.py design_studio_scaffold
```

## Updates bestehender Apps & Container ohne Rebuild

### 1. Einmalig prüfen (Typ A: nachträglich eingebaut vs. Typ B: mit Studio gebaut)
Lokale Kopien unter `templates/design_studio/` oder `static/design_studio/` überschatten Paket-Updates und müssen entfernt werden:
```bash
docker compose exec web python manage.py design_studio_doctor
docker compose exec web python manage.py design_studio_doctor --clean-overrides   # sichert lokale Overrides als .bak
```

### 2. Persistentes Update über `/opt/ds-pkg` (Standard für alle Baukasten-Apps)
Alle Baukasten-Kits werden **persistent** im Named Volume `ds_pkg:/opt/ds-pkg` installiert (niemals flüchtig nach `site-packages` im laufenden Container):
```yaml
services:
  web:
    environment:
      - PYTHONPATH=/opt/ds-pkg
      - DESIGN_STUDIO_TARGET=/opt/ds-pkg
    volumes:
      - .:/app
      - ./data:/app/data
      - ds_pkg:/opt/ds-pkg

volumes:
  ds_pkg:
```
Im Container oder über das einheitliche `./docker/update-fast.sh` (empfohlen):
```bash
./docker/update-fast.sh             # prüft Commits & synct nur geänderte Kits nach /opt/ds-pkg
./docker/update-fast.sh --force-kits # erzwingt Neuinstallation aller aktiven Kits nach /opt/ds-pkg
```
Direkt per Management-Command (erkennt `migrate_all` in Multi-Tenant-Apps automatisch):
```bash
python manage.py design_studio_update --all-kits --target /opt/ds-pkg
```

