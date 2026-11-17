# django-design-studio

Wiederverwendbares Design-Studio-Add-in für Django + Bootstrap 5 (+ optional Chart.js & HTMX).

## Features
- **16 Design-Stimmungen** (`modern`, `dualtone`, `serioes`, `dunkel`, `brutalism`, `wellness`, `ecofuture`, `moody`, `fancy`, `vintage`, `knallbunt`, `neon`, `duester`, `earth`, `monochrom`, `grayscale`)
- **8-Zustände semantische Farbharmonie** (`--theme-state-1` .. `--theme-state-8`) mit Per-State-Override
- **4 Karten-Oberflächen**: `tinted` (Farbharmonie-Milchglas), `glass` (Edles Milchglas), `solid` (Vollton), `brutal` (Kontrast-Kante)
- **5 Adaptive Seiten-SVG-Hintergründe**: `topography`, `grid`, `curves`, `aura`, `brutal_grid`, `none`
- **KPI-Karten 2.0**: SVG-Sparklines, segmentierte Ziel-Fortschrittsbalken, Watermark-Icons, Maus-Spotlight, Bento-Grid (`sm`/`md`/`lg`)
- **Globale Tabellen-, Card- & Chart.js-Harmonisierung** (Hell & Dunkel)
- **Tag/Nacht-Umschalter** im Menü synchron mit dem Design Studio
- **JSON Theme Export / Import** & vorgefertigte App-Vorlagen

## Schnellstart (3 Schritte)

1. Installieren:
```bash
pip install git+https://github.com/bzaiser/django-design-studio.git@main
```

2. `settings.py` & `urls.py`:
```python
INSTALLED_APPS = [..., "design_studio"]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "design_studio.context_processors.theme_context",
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
    <nav>...{% include "design_studio/includes/night_toggle.html" %}</nav>
    ...
    {% include "design_studio/includes/scripts.html" %}
</body>
</html>
```

## Optional: Eigener Storage-Adapter
Für bestehende Apps mit eigenem `UserProfile`:
```python
DESIGN_STUDIO_PROFILE_ADAPTER = "core.theme_adapter.FinanzplanThemeAdapter"
```
