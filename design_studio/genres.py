from django.utils.translation import gettext_lazy as _

GENRE_DEFINITIONS = {
    "poesie": {
        "label": "Poesiealbum (Buch-Look)",
        "badge": "Buch-Optik · Schreiblinien · Spitzen-SVG",
        "primary": "#9D5C63",
        "secondary": "#C49A6C",
        "bg_light": "#F5EFE6",
        "font_head": "'Playfair Display', Georgia, 'Palatino', serif",
        "font_body": "'Georgia', serif",
        "photo_url": "design_studio/img/genres/poesie.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="dsGenreLace" width="80" height="80" patternUnits="userSpaceOnUse">'
            '<circle cx="40" cy="40" r="28" fill="none" stroke="#9D5C63" stroke-width="1" stroke-dasharray="3,4" opacity="0.35"/>'
            '<circle cx="40" cy="40" r="14" fill="none" stroke="#C49A6C" stroke-width="1" opacity="0.35"/>'
            '<path d="M40 5 L40 15 M40 65 L40 75 M5 40 L15 40 M65 40 L75 40" stroke="#9D5C63" stroke-width="1.2" opacity="0.3"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#dsGenreLace)"/></svg>'
        ),
    },
    "natur": {
        "label": "Natur & Waldruhe",
        "badge": "Organisch · Topografie-SVG",
        "primary": "#3D7A5A",
        "secondary": "#8C9A6E",
        "bg_light": "#E8EFEA",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/natur.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#3D7A5A" stroke-width="1.5" opacity="0.28">'
            '<path d="M-50,180 C200,80 400,340 850,210" />'
            '<path d="M-50,240 C220,140 420,400 850,270" />'
            '<path d="M-50,580 C180,480 500,700 850,550" />'
            '</g></svg>'
        ),
    },
    "sport": {
        "label": "Sport & Performance",
        "badge": "Dynamisch · Tempo-Linien",
        "primary": "#E05A2B",
        "secondary": "#2B6CB0",
        "bg_light": "#ECEFF3",
        "font_head": "system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/sport.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g stroke="#E05A2B" stroke-width="2" opacity="0.24">'
            '<line x1="-100" y1="700" x2="500" y2="-100" />'
            '<line x1="50" y1="850" x2="650" y2="50" />'
            '<line x1="200" y1="950" x2="800" y2="150" />'
            '</g></svg>'
        ),
    },
    "tiere": {
        "label": "Tiere & Safari",
        "badge": "Warm · Pfoten & Naturpfad",
        "primary": "#B86B35",
        "secondary": "#6E7F52",
        "bg_light": "#F2ECE4",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/tiere.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="dsGenrePaws" width="120" height="120" patternUnits="userSpaceOnUse">'
            '<circle cx="40" cy="45" r="8" fill="#B86B35" opacity="0.22"/>'
            '<circle cx="30" cy="32" r="4" fill="#B86B35" opacity="0.22"/>'
            '<circle cx="40" cy="28" r="4" fill="#B86B35" opacity="0.22"/>'
            '<circle cx="50" cy="32" r="4" fill="#B86B35" opacity="0.22"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#dsGenrePaws)"/></svg>'
        ),
    },
    "technik": {
        "label": "Technik & Engineering",
        "badge": "Präzise · Platinen-Raster",
        "primary": "#2563EB",
        "secondary": "#0D9488",
        "bg_light": "#E6ECF2",
        "font_head": "'JetBrains Mono', ui-monospace, 'SF Mono', monospace",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/technik.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="dsGenreTech" width="60" height="60" patternUnits="userSpaceOnUse">'
            '<path d="M 60 0 L 0 0 0 60" fill="none" stroke="#2563EB" stroke-width="0.8" opacity="0.22"/>'
            '<circle cx="0" cy="0" r="2.5" fill="#0D9488" opacity="0.4"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#dsGenreTech)"/></svg>'
        ),
    },
    "comic": {
        "label": "Comic & Pop-Art",
        "badge": "Kontrast · Halbton-Punkte",
        "primary": "#E11D48",
        "secondary": "#2563EB",
        "bg_light": "#FEFCE8",
        "font_head": "'Comic Neue', 'Comic Sans MS', 'Chalkboard SE', sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/comic.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="dsGenreHalftone" width="24" height="24" patternUnits="userSpaceOnUse">'
            '<circle cx="12" cy="12" r="3" fill="#E11D48" opacity="0.22"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#dsGenreHalftone)"/></svg>'
        ),
    },
    "esoterik": {
        "label": "Esoterik & Mondphasen",
        "badge": "Mystisch · Heilige Geometrie",
        "primary": "#7C3AED",
        "secondary": "#D97706",
        "bg_light": "#EFEBF7",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/esoterik.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#7C3AED" stroke-width="1.2" opacity="0.25">'
            '<circle cx="400" cy="350" r="180"/><circle cx="400" cy="350" r="120"/>'
            '<polygon points="400,170 555,440 245,440"/><polygon points="400,530 555,260 245,260"/>'
            '</g></svg>'
        ),
    },
    "musik": {
        "label": "Musik & Akustik",
        "badge": "Harmonisch · Notenlinien & Schallwellen",
        "primary": "#6D28D9",
        "secondary": "#DB2777",
        "bg_light": "#EFEBF5",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/musik.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#6D28D9" stroke-width="1.2" opacity="0.24">'
            '<path d="M0,200 Q200,140 400,200 T800,200"/><path d="M0,215 Q200,155 400,215 T800,215"/>'
            '<path d="M0,230 Q200,170 400,230 T800,230"/><path d="M0,245 Q200,185 400,245 T800,245"/>'
            '</g></svg>'
        ),
    },
    "kinder": {
        "label": "Kinder & Spielwelt",
        "badge": "Fröhlich · Konfetti & Bauklötze",
        "primary": "#F59E0B",
        "secondary": "#10B981",
        "bg_light": "#FFFBEB",
        "font_head": "'Comic Neue', 'Comic Sans MS', 'Chalkboard SE', sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/kinder.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<circle cx="150" cy="180" r="24" fill="#F59E0B" opacity="0.25"/>'
            '<polygon points="620,160 650,210 590,210" fill="#10B981" opacity="0.25"/>'
            '<rect x="200" y="520" width="36" height="36" rx="8" fill="#3B82F6" opacity="0.22" transform="rotate(15 218 538)"/>'
            '</svg>'
        ),
    },
    "malbuch": {
        "label": "Malbuch & Skizzenheft",
        "badge": "Kreativ · Gestrichelte Konturen",
        "primary": "#EC4899",
        "secondary": "#8B5CF6",
        "bg_light": "#FAF8F5",
        "font_head": "'Comic Neue', 'Comic Sans MS', 'Chalkboard SE', sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/malbuch.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#EC4899" stroke-width="1.8" stroke-dasharray="6,6" opacity="0.28">'
            '<circle cx="200" cy="250" r="110"/><rect x="480" y="420" width="180" height="180" rx="24"/>'
            '</g></svg>'
        ),
    },
    "game": {
        "label": "Game & Arcade",
        "badge": "Pixel & Quest · XP-Balken",
        "primary": "#10B981",
        "secondary": "#8B5CF6",
        "bg_light": "#E8F0EC",
        "font_head": "'JetBrains Mono', ui-monospace, 'SF Mono', monospace",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/game.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="dsGenrePixels" width="40" height="40" patternUnits="userSpaceOnUse">'
            '<rect x="4" y="4" width="12" height="12" fill="#10B981" opacity="0.18"/>'
            '<rect x="24" y="24" width="12" height="12" fill="#8B5CF6" opacity="0.18"/>'
            '</pattern></defs><rect width="100%" height="100%" fill="url(#dsGenrePixels)"/></svg>'
        ),
    },
    "scifi": {
        "label": "Science Fiction & Orbit",
        "badge": "Futuristisch · HUD-Konsolen",
        "primary": "#06B6D4",
        "secondary": "#6366F1",
        "bg_light": "#E6F0F5",
        "font_head": "'JetBrains Mono', ui-monospace, 'SF Mono', monospace",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/scifi.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#06B6D4" stroke-width="1.2" opacity="0.28">'
            '<ellipse cx="400" cy="400" rx="340" ry="120" transform="rotate(-18 400 400)"/>'
            '<ellipse cx="400" cy="400" rx="260" ry="90" transform="rotate(-18 400 400)"/>'
            '</g></svg>'
        ),
    },
    "welt": {
        "label": "Länder und Welt",
        "badge": "Global · Längen- & Breitengrade",
        "primary": "#2563EB",
        "secondary": "#D97706",
        "bg_light": "#EAEFF5",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/welt.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#2563EB" stroke-width="1" opacity="0.24">'
            '<circle cx="400" cy="420" r="260"/><ellipse cx="400" cy="420" rx="140" ry="260"/>'
            '<line x1="140" y1="420" x2="660" y2="420"/><line x1="170" y1="310" x2="630" y2="310"/>'
            '</g></svg>'
        ),
    },
    "urlaub": {
        "label": "Urlaub und Reisen",
        "badge": "Fernweh · Flugrouten & Kompass",
        "primary": "#EA580C",
        "secondary": "#0284C7",
        "bg_light": "#F5EFEA",
        "font_head": "system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/urlaub.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M80,680 Q320,240 720,180" fill="none" stroke="#EA580C" stroke-width="2" stroke-dasharray="8,8" opacity="0.32"/>'
            '<circle cx="720" cy="180" r="6" fill="#EA580C" opacity="0.4"/>'
            '</svg>'
        ),
    },
    "meer": {
        "label": "Meer & Küste",
        "badge": "Maritim · Sanfte Wellenlinien",
        "primary": "#0284C7",
        "secondary": "#0D9488",
        "bg_light": "#E6F1F5",
        "font_head": "'Playfair Display', Georgia, serif",
        "font_body": "'Inter', system-ui, sans-serif",
        "photo_url": "design_studio/img/genres/meer.jpg",
        "svg": (
            '<svg viewBox="0 0 800 900" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="none" stroke="#0284C7" stroke-width="1.8" opacity="0.26">'
            '<path d="M0,260 Q100,230 200,260 T400,260 T600,260 T800,260"/>'
            '<path d="M0,300 Q100,270 200,300 T400,300 T600,300 T800,300"/>'
            '<path d="M0,580 Q100,550 200,580 T400,580 T600,580 T800,580"/>'
            '</g></svg>'
        ),
    },
}


GENRE_CHOICES = [("", _("Standard (App-Theme)"))] + [
    (key, data["label"]) for key, data in GENRE_DEFINITIONS.items()
]


def is_valid_genre(value) -> bool:
    return isinstance(value, str) and (value == "" or value in GENRE_DEFINITIONS)


def get_genre_definition(key: str, user=None):
    if not key or key not in GENRE_DEFINITIONS:
        return None
    data = {"key": key, **GENRE_DEFINITIONS[key]}
    photo = data.get("photo_url") or ""
    if photo and not photo.startswith(("http://", "https://", "/")):
        from django.templatetags.static import static
        data["photo_url"] = static(photo)
    if user and getattr(user, "is_authenticated", False):
        try:
            from .bg_media import get_user_genre_bg_url
            custom_url = get_user_genre_bg_url(user, key)
            if custom_url:
                data["custom_photo_url"] = custom_url
        except Exception:
            pass
    return data


def resolve_request_genre(request, menu_items, default_genre: str = ""):
    """Resolve the active genre for the current request based on menu_items or default_genre."""
    if request is not None:
        req_path = (getattr(request, "path", "") or "").rstrip("/") or "/"
        resolver_match = getattr(request, "resolver_match", None)
        req_url_name = getattr(resolver_match, "url_name", "") or ""
        req_view_name = getattr(resolver_match, "view_name", "") or ""

        for item in menu_items or ():
            if not isinstance(item, dict):
                continue
            item_url = (item.get("url") or "").rstrip("/") or "/"
            match_urls = item.get("match_urls") or []
            matched = (
                (item_url not in ("", "#") and req_path == item_url)
                or (req_url_name and req_url_name in match_urls)
                or (req_view_name and req_view_name in match_urls)
            )
            if matched and item.get("genre"):
                return get_genre_definition(item["genre"])

    return get_genre_definition(default_genre)
