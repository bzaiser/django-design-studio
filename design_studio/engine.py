from django.utils.translation import gettext_lazy as _

STATES = [
    {"index": 1, "n": _("1. OK / Ampel Grün"), "h": 142, "t": _("✓ Stabil"), "side": 1},
    {"index": 2, "n": _("2. Positiv / Info"), "h": 185, "t": _("ℹ Info"), "side": 1},
    {"index": 3, "n": _("3. Mittel / Achtung"), "h": 43, "t": _("⚠ Achtung"), "side": 2},
    {"index": 4, "n": _("4. Warnung"), "h": 26, "t": _("⚡ Warnung"), "side": 2},
    {"index": 5, "n": _("5. Schlecht / Negativ"), "h": 4, "t": _("✕ Fehler"), "side": 2},
    {"index": 6, "n": _("6. Gefahr / Kritisch"), "h": 338, "t": _("🛑 Gefahr"), "side": 2},
    {"index": 7, "n": _("7. Neutral / Inaktiv"), "h": None, "t": _("• Inaktiv"), "side": 0},
    {"index": 8, "n": _("8. Fokus / Highlight"), "h": 272, "t": _("★ Fokus"), "side": 1},
]

MOODS = {
    "modern":    {"s": 70, "l": 50, "bg": "#f4f6f9", "dark": False, "shift": 0.06, "surface": "tinted", "svg": "topography"},
    "dualtone":  {"s": 78, "l": 52, "bg": "#f4f6f9", "dark": False, "shift": 0.00, "dual": True, "surface": "tinted", "svg": "curves"},
    "serioes":   {"s": 42, "l": 45, "bg": "#f1f5f9", "dark": False, "shift": 0.10, "surface": "glass", "svg": "grid"},
    "dunkel":    {"s": 65, "l": 52, "bg": "#0f172a", "dark": True,  "shift": 0.08, "surface": "glass", "svg": "grid"},
    "brutalism": {"s": 92, "l": 56, "bg": "#050505", "dark": True,  "shift": 0.00, "brutal": True, "surface": "brutal", "svg": "brutal_grid"},
    "wellness":  {"s": 36, "l": 74, "bg": "#f6f7f4", "dark": False, "shift": 0.18, "surface": "tinted", "svg": "topography"},
    "ecofuture": {"s": 88, "l": 52, "bg": "#141d18", "dark": True,  "shift": 0.05, "eco": True, "surface": "tinted", "svg": "curves"},
    "moody":     {"s": 58, "l": 36, "bg": "#16131c", "dark": True,  "shift": 0.12, "surface": "tinted", "svg": "aura"},
    "fancy":     {"s": 65, "l": 68, "bg": "#f8f5fc", "dark": False, "shift": 0.12, "surface": "tinted", "svg": "aura"},
    "vintage":   {"s": 48, "l": 54, "bg": "#f5f0e6", "dark": False, "shift": 0.25, "warm": True, "surface": "tinted", "svg": "aura"},
    "knallbunt": {"s": 95, "l": 52, "bg": "#f4f6f9", "dark": False, "shift": 0.02, "surface": "solid", "svg": "curves"},
    "neon":      {"s": 100,"l": 55, "bg": "#090a0f", "dark": True,  "shift": 0.00, "glow": True, "surface": "tinted", "svg": "curves"},
    "duester":   {"s": 35, "l": 38, "bg": "#111317", "dark": True,  "shift": 0.15, "surface": "glass", "svg": "aura"},
    "earth":     {"s": 32, "l": 48, "bg": "#ede6dc", "dark": False, "shift": 0.15, "earth": True, "surface": "tinted", "svg": "topography"},
    "monochrom": {"s": 55, "l": 50, "bg": "#f4f6f9", "dark": False, "shift": 0.88, "surface": "glass", "svg": "grid"},
    "grayscale": {"s": 0,  "l": 50, "bg": "#efefef", "dark": False, "shift": 0.00, "surface": "glass", "svg": "grid"},
}

CARD_SURFACES = ("auto", "solid", "glass", "tinted", "brutal")
BG_SVG_MODES = ("auto", "topography", "grid", "curves", "aura", "brutal_grid", "none")
MENU_LAYOUTS = ("top", "sidebar")
MENU_STYLES = ("auto", "glass", "gradient")

APP_PRESETS = {
    "finanz_serioes": {
        "label": _("Finanz-Seriös"),
        "c1": "#1E3A8A",
        "c2": "#0F766E",
        "mood": "serioes",
        "bg_mode": "light",
        "card_surface": "glass",
        "bg_svg_mode": "grid",
    },
    "modern_glass": {
        "label": _("Modern Glass"),
        "c1": "#3B82F6",
        "c2": "#10B981",
        "mood": "modern",
        "bg_mode": "auto",
        "card_surface": "tinted",
        "bg_svg_mode": "topography",
    },
    "neon_dark": {
        "label": _("Neon Dark"),
        "c1": "#06B6D4",
        "c2": "#EC4899",
        "mood": "neon",
        "bg_mode": "dark",
        "card_surface": "tinted",
        "bg_svg_mode": "curves",
    },
    "eco_future": {
        "label": _("Eco Future"),
        "c1": "#10B981",
        "c2": "#84CC16",
        "mood": "ecofuture",
        "bg_mode": "dark",
        "card_surface": "tinted",
        "bg_svg_mode": "curves",
    },
    "brutal_contrast": {
        "label": _("Polished Brutalism"),
        "c1": "#F59E0B",
        "c2": "#EF4444",
        "mood": "brutalism",
        "bg_mode": "dark",
        "card_surface": "brutal",
        "bg_svg_mode": "brutal_grid",
    },
}

DEFAULT_SETTINGS = {
    "c1": "#6610f2",
    "c2": "#0d6efd",
    "mood": "modern",
    "bg_mode": "auto",
    "day_bg_mode": "light",
    "bg_custom": "#ffffff",
    "sync_cards_and_charts": True,
    "state_overrides": {},
    "card_surface": "auto",
    "bg_svg_mode": "auto",
    "kpi_sparklines": True,
    "kpi_progress_bars": True,
    "kpi_watermarks": True,
    "kpi_spotlight": True,
    "kpi_click_navigation": True,
    "menu_layout": "top",
    "menu_style": "auto",
    "menu_config": [],
    "brand_title": "",
    "brand_icon": "",
}


def hex_to_hsl(hex_str):
    if not hex_str or not isinstance(hex_str, str):
        return {"h": 217, "s": 91, "l": 60}
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    if len(clean) != 6:
        return {"h": 217, "s": 91, "l": 60}
    try:
        r = int(clean[0:2], 16) / 255.0
        g = int(clean[2:4], 16) / 255.0
        b = int(clean[4:6], 16) / 255.0
    except ValueError:
        return {"h": 217, "s": 91, "l": 60}

    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2.0
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif mx == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h *= 60.0
    return {"h": round(h) % 360, "s": round(s * 100), "l": round(l * 100)}


def hsl_to_hex(h, s, l):
    h = h % 360
    s = max(0, min(100, s))
    l = max(0, min(100, l))
    l_norm = l / 100.0
    a = (s * min(l_norm, 1.0 - l_norm)) / 100.0

    def f(n):
        k = (n + h / 30.0) % 12.0
        color = l_norm - a * max(min(k - 3.0, 9.0 - k, 1.0), -1.0)
        return f"{round(255 * color):02x}"

    return f"#{f(0)}{f(8)}{f(4)}".upper()


def get_contrast_text(hex_str):
    if not hex_str or not isinstance(hex_str, str):
        return "#ffffff"
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    if len(clean) != 6:
        return "#ffffff"
    try:
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
    except ValueError:
        return "#ffffff"
    yiq = (r * 299 + g * 587 + b * 114) / 1000.0
    return "#1e293b" if yiq >= 175 else "#ffffff"


def normalize_settings(raw):
    data = dict(DEFAULT_SETTINGS)
    if isinstance(raw, dict):
        for k in data:
            if k in raw and raw[k] is not None:
                data[k] = raw[k]

    if data["mood"] not in MOODS:
        data["mood"] = "modern"
    if data["bg_mode"] not in ("auto", "light", "dark", "custom"):
        data["bg_mode"] = "auto"
    if data["day_bg_mode"] not in ("auto", "light", "custom"):
        data["day_bg_mode"] = "light"
    if data["card_surface"] not in CARD_SURFACES:
        data["card_surface"] = "auto"
    if data["bg_svg_mode"] not in BG_SVG_MODES:
        data["bg_svg_mode"] = "auto"
    if data["menu_layout"] not in MENU_LAYOUTS:
        data["menu_layout"] = "top"
    if data["menu_style"] not in MENU_STYLES:
        data["menu_style"] = "auto"
    if not isinstance(data["menu_config"], list):
        data["menu_config"] = []
    data["brand_title"] = str(data.get("brand_title") or "").strip()[:60]
    raw_brand_icon = str(data.get("brand_icon") or "").strip()
    if raw_brand_icon == "none":
        data["brand_icon"] = "none"
    elif raw_brand_icon.startswith("bi-"):
        data["brand_icon"] = raw_brand_icon[:60]
    else:
        data["brand_icon"] = ""
    if not isinstance(data["state_overrides"], dict):
        data["state_overrides"] = {}

    m = MOODS[data["mood"]]
    data["resolved_card_surface"] = m.get("surface", "tinted") if data["card_surface"] == "auto" else data["card_surface"]
    data["resolved_bg_svg"] = m.get("svg", "topography") if data["bg_svg_mode"] == "auto" else data["bg_svg_mode"]
    data["resolved_menu_style"] = (
        ("brutal" if data["resolved_card_surface"] == "brutal" else "gradient")
        if data["menu_style"] == "auto"
        else data["menu_style"]
    )
    for bkey in ("sync_cards_and_charts", "kpi_sparklines", "kpi_progress_bars", "kpi_watermarks", "kpi_spotlight", "kpi_click_navigation"):
        data[bkey] = bool(data[bkey])
    return data


def _compute_single_state(st_h, st_side, idx, base1, base2, mood_key, m, is_dark):
    hue = base1["h"] if st_h is None else round(st_h + (base1["h"] - st_h) * m["shift"])
    s = (0 if m["s"] == 0 else 12) if st_h is None else m["s"]
    l = m["l"]

    if m.get("dual"):
        if st_side == 1:
            hue = base1["h"]
            l = 46 if idx == 0 else (56 if idx == 1 else 38)
        elif st_side == 2:
            hue = base2["h"]
            l = min(68, 38 + (max(0, idx - 2) * 7))
        else:
            hue = round((base1["h"] + base2["h"]) / 2)
            s = 14
            l = 50

    if m.get("warm") and st_h is not None:
        hue = round(hue * 0.85 + 35 * 0.15)
    if m.get("earth"):
        hue = 32 if st_h is None else round(hue * 0.35 + 28 * 0.65)
        l = min(68, 35 + ((idx % 8) * 4))
    if m.get("eco") and st_h is not None:
        if st_h in (142, 185):
            s = 48
            l = 44
        else:
            s = 98
            l = 56
    if mood_key in ("monochrom", "grayscale"):
        l = min(76, 24 + ((idx % 8) * 7))
    elif not m.get("dual") and st_h is not None and 35 <= st_h <= 55 and not is_dark and mood_key != "wellness":
        l = max(48, l)

    hex_val = hsl_to_hex(hue, s, l)
    alpha = 0.24 if is_dark else 0.15
    bg = f"hsla({hue % 360}, {s}%, {l}%, {alpha})"
    txt = hsl_to_hex(hue, s, min(86, l + 24)) if is_dark else hsl_to_hex(hue, s, max(22, l - 26))
    card_text = get_contrast_text(hex_val)
    return {
        "hue": hue % 360,
        "s": s,
        "l": l,
        "hex": hex_val,
        "bg": bg,
        "txt": txt,
        "card_text": card_text,
    }


def compute_theme_palette(c1="#6610f2", c2="#0d6efd", mood_key="modern", bg_mode="auto", bg_custom="#e2e8f0", state_overrides=None):
    if mood_key not in MOODS:
        mood_key = "modern"
    m = MOODS[mood_key]
    overrides = state_overrides if isinstance(state_overrides, dict) else {}

    page_bg = m["bg"]
    is_dark = bool(m["dark"])
    if bg_mode == "light":
        page_bg = "#f4f6f9"
        is_dark = False
    elif bg_mode == "dark":
        page_bg = "#0f172a"
        is_dark = True
    elif bg_mode == "custom" and bg_custom:
        page_bg = bg_custom
        is_dark = hex_to_hsl(page_bg)["l"] < 50

    base1 = hex_to_hsl(c1)
    base2 = hex_to_hsl(c2)

    computed_states = []
    states_by_index = {}
    for idx, st in enumerate(STATES):
        ov_raw = overrides.get(str(st["index"])) or overrides.get(st["index"])
        ov_bg = None
        ov_txt = None
        if isinstance(ov_raw, str):
            ov_bg = ov_raw
        elif isinstance(ov_raw, dict):
            ov_bg = ov_raw.get("bg")
            ov_txt = ov_raw.get("text")

        if isinstance(ov_bg, str) and ov_bg.strip().startswith("#") and len(ov_bg.strip()) in (4, 7):
            clean_ov = ov_bg.strip().upper()
            ov_hsl = hex_to_hsl(clean_ov)
            alpha = 0.24 if is_dark else 0.15
            res = {
                "hue": ov_hsl["h"],
                "s": ov_hsl["s"],
                "l": ov_hsl["l"],
                "hex": clean_ov,
                "bg": f"hsla({ov_hsl['h']}, {ov_hsl['s']}%, {ov_hsl['l']}%, {alpha})",
                "txt": hsl_to_hex(ov_hsl["h"], ov_hsl["s"], min(86, ov_hsl["l"] + 24)) if is_dark else hsl_to_hex(ov_hsl["h"], ov_hsl["s"], max(22, ov_hsl["l"] - 26)),
                "card_text": get_contrast_text(clean_ov),
            }
        else:
            res = _compute_single_state(st["h"], st["side"], idx, base1, base2, mood_key, m, is_dark)

        if isinstance(ov_txt, str) and ov_txt.strip().startswith("#") and len(ov_txt.strip()) in (4, 7):
            res["card_text"] = ov_txt.strip().upper()

        entry = {
            "index": st["index"],
            "name": str(st["n"]),
            "tag": str(st["t"]),
            **res,
        }
        computed_states.append(entry)
        states_by_index[st["index"]] = entry

    primary_hex = "#555555" if mood_key == "grayscale" else c1
    grad_start = "#333333" if mood_key == "grayscale" else c1
    grad_end = "#888888" if mood_key == "grayscale" else c2

    text_color = "#f8fafc" if is_dark else "#1e293b"
    sidebar_bg = hsl_to_hex(base1["h"], min(25, m["s"]), 12 if is_dark else 96)
    th_hue = base1["h"]
    if m.get("warm"):
        th_hue = round(th_hue * 0.85 + 35 * 0.15)
    if m.get("earth"):
        th_hue = round(th_hue * 0.35 + 28 * 0.65)
    th_lightness = 30 if mood_key == "grayscale" else (28 if is_dark else max(32, min(52, m["l"])))
    table_header_bg = hsl_to_hex(th_hue, m["s"], th_lightness)
    table_header_text = get_contrast_text(table_header_bg)
    table_body_bg = hsl_to_hex(base1["h"], min(18, m["s"]), 11 if is_dark else 99) if bg_mode != "custom" else page_bg
    table_body_text = text_color
    table_border = "#334155" if is_dark else "#dee2e6"

    return {
        "c1": grad_start,
        "c2": grad_end,
        "mood": mood_key,
        "bg_mode": bg_mode,
        "bg_custom": bg_custom,
        "is_dark": is_dark,
        "brutal": bool(m.get("brutal", False)),
        "glow": bool(m.get("glow", False) or m.get("eco", False)),
        "primary_color": primary_hex,
        "background_color": page_bg,
        "text_color": text_color,
        "sidebar_bg_color": sidebar_bg,
        "table_header_bg_color": table_header_bg,
        "table_header_text_color": table_header_text,
        "table_body_bg_color": table_body_bg,
        "table_body_text_color": table_body_text,
        "table_border_color": table_border,
        "states": computed_states,
        "states_by_index": states_by_index,
    }


def serialize_export_payload(settings_dict):
    norm = normalize_settings(settings_dict)
    return {
        "version": 1,
        "c1": norm["c1"],
        "c2": norm["c2"],
        "mood": norm["mood"],
        "bg_mode": norm["bg_mode"],
        "day_bg_mode": norm["day_bg_mode"],
        "bg_custom": norm["bg_custom"],
        "sync_cards_and_charts": norm["sync_cards_and_charts"],
        "state_overrides": norm["state_overrides"],
        "card_surface": norm["card_surface"],
        "bg_svg_mode": norm["bg_svg_mode"],
        "kpi_sparklines": norm["kpi_sparklines"],
        "kpi_progress_bars": norm["kpi_progress_bars"],
        "kpi_watermarks": norm["kpi_watermarks"],
        "kpi_spotlight": norm["kpi_spotlight"],
        "kpi_click_navigation": norm["kpi_click_navigation"],
    }


def parse_import_payload(raw_dict):
    if not isinstance(raw_dict, dict):
        raise ValueError("Invalid theme JSON object.")
    return serialize_export_payload(raw_dict)
