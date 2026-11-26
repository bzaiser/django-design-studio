import json

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .engine import (
    APP_PRESETS,
    DEFAULT_SETTINGS,
    MOODS,
    compute_theme_palette,
    hex_to_hsl,
    normalize_settings,
    parse_import_payload,
    serialize_export_payload,
)
from .menu import is_valid_bi_icon
from .storage import get_storage_adapter


@login_required
def studio_view(request):
    from .context_processors import _resolve_site_admin_theme

    adapter = get_storage_adapter()
    if request.method == "POST":
        return save_studio_view(request)
    default_norm = normalize_settings(DEFAULT_SETTINGS)
    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    _su, site_ts = _resolve_site_admin_theme(adapter, default_norm)
    if not is_admin and not site_ts.get("allow_user_design", False):
        return HttpResponse("Kein Zugriff.", status=403)
    ts = adapter.get_settings(request.user)
    if not is_admin and not ts.get("user_custom_design", False):
        ts = dict(site_ts)
    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
        table_header_color=ts.get("table_header_color", ""),
    )
    from django.utils.http import url_has_allowed_host_and_scheme

    referer = request.META.get("HTTP_REFERER", "")
    next_param = request.GET.get("next", "").strip()
    if next_param and not url_has_allowed_host_and_scheme(
        next_param, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_param = ""
    if referer and not url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        referer = ""
    if next_param:
        request.session["ds_return_url"] = next_param
    elif referer and "/design-studio" not in referer:
        request.session["ds_return_url"] = referer
    sess_ret = request.session.get("ds_return_url") or ""
    if sess_ret and not url_has_allowed_host_and_scheme(
        sess_ret, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        sess_ret = ""
    back_url = next_param or sess_ret or "/"
    return render(request, "design_studio/studio_page.html", {
        "theme_studio": ts,
        "theme_palette": palette,
        "theme_state_overrides_json": json.dumps(ts.get("state_overrides", {})),
        "design_studio_presets": [{"key": k, **v} for k, v in APP_PRESETS.items()],
        "back_url": back_url,
    })


@login_required
@require_POST
def save_studio_view(request):
    from .context_processors import _resolve_site_admin_theme

    adapter = get_storage_adapter()
    default_norm = normalize_settings(DEFAULT_SETTINGS)
    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    _su, site_ts = _resolve_site_admin_theme(adapter, default_norm)
    if not is_admin and not site_ts.get("allow_user_design", False):
        return HttpResponse("Kein Zugriff.", status=403)

    prev = adapter.get_settings(request.user)
    if not is_admin and not prev.get("user_custom_design", False):
        prev = dict(site_ts)

    preset_key = request.POST.get("app_preset", "").strip()
    if not is_admin:
        if preset_key in APP_PRESETS:
            p = APP_PRESETS[preset_key]
            merged = {
                **prev,
                "c1": p["c1"],
                "c2": p["c2"],
                "mood": p["mood"],
                "bg_mode": p["bg_mode"],
                "day_bg_mode": p["bg_mode"] if p["bg_mode"] != "dark" else prev.get("day_bg_mode", "light"),
                "card_surface": p["card_surface"],
                "bg_svg_mode": p["bg_svg_mode"],
                "user_custom_design": True,
            }
        else:
            merged = {
                **prev,
                "default_genre": request.POST.get("theme_default_genre", prev.get("default_genre", "")),
                "genre_photos_enabled": request.POST.get("theme_genre_photos_enabled") == "1",
                "user_custom_design": True,
            }
    elif preset_key in APP_PRESETS:
        p = APP_PRESETS[preset_key]
        merged = {
            **prev,
            "c1": p["c1"],
            "c2": p["c2"],
            "mood": p["mood"],
            "bg_mode": p["bg_mode"],
            "day_bg_mode": p["bg_mode"] if p["bg_mode"] != "dark" else prev.get("day_bg_mode", "light"),
            "card_surface": p["card_surface"],
            "bg_svg_mode": p["bg_svg_mode"],
            "font_scale": p.get("font_scale", prev.get("font_scale", "normal")),
            "ui_zoom": p.get("ui_zoom", prev.get("ui_zoom", 100)),
            "glass_alpha": p.get("glass_alpha", prev.get("glass_alpha", 32)),
            "glass_blur": p.get("glass_blur", prev.get("glass_blur", 14)),
            "bg_strength": p.get("bg_strength", prev.get("bg_strength", 65)),
            "sync_cards_and_charts": True,
        }
    else:
        bg_mode = request.POST.get("theme_bg_mode", prev.get("bg_mode", "auto"))
        raw_ov = request.POST.get("theme_state_overrides", "").strip()
        state_overrides = prev.get("state_overrides", {})
        if raw_ov:
            try:
                parsed = json.loads(raw_ov)
                if isinstance(parsed, dict):
                    state_overrides = parsed
            except Exception:
                pass
        has_kpi = "kpi_ext_present" in request.POST
        merged = {
            **prev,
            "c1": request.POST.get("gradient_start") or prev.get("c1", "#6610f2"),
            "c2": request.POST.get("gradient_end") or prev.get("c2", "#0d6efd"),
            "mood": request.POST.get("theme_mood", prev.get("mood", "modern")),
            "bg_mode": bg_mode,
            "day_bg_mode": bg_mode if bg_mode != "dark" else prev.get("day_bg_mode", "light"),
            "bg_custom": request.POST.get("theme_bg_custom") or prev.get("bg_custom", "#ffffff"),
            "sync_cards_and_charts": request.POST.get("theme_sync_cards") == "on" if "theme_sync_cards" in request.POST or has_kpi else prev.get("sync_cards_and_charts", True),
            "state_overrides": state_overrides,
            "card_surface": request.POST.get("theme_card_surface", prev.get("card_surface", "auto")),
            "bg_svg_mode": request.POST.get("theme_bg_svg_mode", prev.get("bg_svg_mode", "auto")),
            "kpi_sparklines": (request.POST.get("kpi_sparklines") == "on") if has_kpi else prev.get("kpi_sparklines", True),
            "kpi_progress_bars": (request.POST.get("kpi_progress_bars") == "on") if has_kpi else prev.get("kpi_progress_bars", True),
            "kpi_watermarks": (request.POST.get("kpi_watermarks") == "on") if has_kpi else prev.get("kpi_watermarks", True),
            "kpi_spotlight": (request.POST.get("kpi_spotlight") == "on") if has_kpi else prev.get("kpi_spotlight", True),
            "kpi_click_navigation": (request.POST.get("kpi_click_navigation") == "on") if has_kpi else prev.get("kpi_click_navigation", True),
            "menu_layout": request.POST.get("theme_menu_layout", prev.get("menu_layout", "top")),
            "menu_style": request.POST.get("theme_menu_style", prev.get("menu_style", "auto")),
            "font_family": request.POST.get("theme_font_family", prev.get("font_family", "auto")),
            "font_scale": request.POST.get("theme_font_scale", prev.get("font_scale", "normal")),
            "ui_zoom": request.POST.get("theme_ui_zoom", prev.get("ui_zoom", 100)),
            "glass_alpha": request.POST.get("theme_glass_alpha", prev.get("glass_alpha", 32)),
            "glass_blur": request.POST.get("theme_glass_blur", prev.get("glass_blur", 14)),
            "bg_strength": request.POST.get("theme_bg_strength", prev.get("bg_strength", 65)),
            "menu_config": prev.get("menu_config", []),
            "menu_overflow_mode": request.POST.get("theme_menu_overflow_mode", prev.get("menu_overflow_mode", "wrap")),
            "brand_title": request.POST.get("brand_title", prev.get("brand_title", "")),
            "brand_icon": request.POST.get("brand_icon", prev.get("brand_icon", "")),
            "default_genre": request.POST.get("theme_default_genre", prev.get("default_genre", "")),
            "genre_photos_enabled": request.POST.get("theme_genre_photos_enabled") == "1",
            "table_header_color": request.POST.get("theme_table_header_color", prev.get("table_header_color", "")),
            "allow_user_design": (request.POST.get("theme_allow_user_design") == "1") if has_kpi else prev.get("allow_user_design", False),
        }
        if "menu_config_json" in request.POST:
            raw_menu = request.POST.get("menu_config_json", "").strip()
            if raw_menu == "RESET":
                merged["menu_config"] = []
                merged["brand_title"] = ""
                merged["brand_icon"] = ""
            elif raw_menu:
                try:
                    parsed_menu = json.loads(raw_menu)
                    if isinstance(parsed_menu, list):
                        clean_menu = []
                        for idx, m_item in enumerate(parsed_menu):
                            if not isinstance(m_item, dict) or not m_item.get("id"):
                                continue
                            mid = str(m_item["id"]).strip()
                            ic = str(m_item.get("icon") or "").strip()
                            if not is_valid_bi_icon(ic):
                                ic = ""
                            disp = m_item.get("display") if m_item.get("display") in ("icon_text", "icon_only", "text_only") else "icon_text"
                            zn = m_item.get("zone") if m_item.get("zone") in ("main", "utility", "system") else "main"
                            from .genres import is_valid_genre
                            gr = str(m_item.get("genre") or "").strip()
                            if not is_valid_genre(gr):
                                gr = ""
                            parent_id = str(m_item.get("parent_id") or "").strip()[:40]
                            if parent_id == mid:
                                parent_id = ""
                            clean_menu.append({
                                "id": mid,
                                "label": str(m_item.get("label") or "").strip()[:40],
                                "icon": ic,
                                "display": disp,
                                "zone": zn,
                                "visible": bool(m_item.get("visible", True)),
                                "order": int(m_item.get("order", idx + 1)),
                                "genre": gr,
                                "parent_id": parent_id,
                            })
                        merged["menu_config"] = clean_menu
                except Exception:
                    pass
        if "web_menu_config_json" in request.POST:
            raw_wm = (request.POST.get("web_menu_config_json") or "").strip()
            if raw_wm:
                try:
                    from django.apps import apps
                    if apps.is_installed("site_kit"):
                        from site_kit.views import save_web_menu_config
                        save_web_menu_config(json.loads(raw_wm))
                except Exception:
                    pass

    norm = normalize_settings(merged)
    palette = compute_theme_palette(
        c1=norm["c1"],
        c2=norm["c2"],
        mood_key=norm["mood"],
        bg_mode=norm["bg_mode"],
        bg_custom=norm["bg_custom"],
        state_overrides=norm.get("state_overrides"),
        table_header_color=norm.get("table_header_color", ""),
    )
    manual_precision = request.POST.get("theme_manual_precision") == "1"
    adapter.save_settings(request.user, norm, palette=palette, manual_precision=manual_precision)
    messages.success(request, _("Design Studio Einstellungen gespeichert."))
    return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "design_studio:studio")


@login_required
def toggle_night_mode_view(request):
    from .context_processors import _resolve_site_admin_theme

    adapter = get_storage_adapter()
    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    ts = adapter.get_settings(request.user)
    if not is_admin and not ts.get("user_custom_design", False):
        _su, site_ts = _resolve_site_admin_theme(adapter, normalize_settings(DEFAULT_SETTINGS))
        ts = {**site_ts, **{k: ts[k] for k in ("user_menu_layout", "user_night_bg") if k in ts}}
        if ts.get("user_night_bg") in ("auto", "light", "dark", "custom"):
            ts["bg_mode"] = ts["user_night_bg"]
    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
        table_header_color=ts.get("table_header_color", ""),
    )
    mood_key = ts.get("mood", "modern")
    if mood_key not in MOODS:
        mood_key = "modern"

    if palette.get("is_dark"):
        day_mode = ts.get("day_bg_mode", "light")
        if day_mode not in ("auto", "light", "custom"):
            day_mode = "light"
        if day_mode == "auto" and MOODS[mood_key].get("dark"):
            day_mode = "light"
        if day_mode == "custom" and hex_to_hsl(ts.get("bg_custom", "#ffffff"))["l"] < 50:
            day_mode = "light"
        ts["bg_mode"] = day_mode
    else:
        cur_bg = ts.get("bg_mode", "auto")
        ts["day_bg_mode"] = cur_bg if cur_bg in ("auto", "light", "custom") else "light"
        ts["bg_mode"] = "dark"
    ts["user_night_bg"] = ts["bg_mode"]

    new_palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
        table_header_color=ts.get("table_header_color", ""),
    )
    adapter.save_settings(request.user, ts, palette=new_palette, manual_precision=False)
    next_url = (request.GET.get("next") or request.POST.get("next") or "").strip()
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(request.META.get("HTTP_REFERER") or "/")


@login_required
def toggle_menu_layout_view(request):
    from .context_processors import _resolve_site_admin_theme

    adapter = get_storage_adapter()
    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    ts = adapter.get_settings(request.user)
    if not is_admin and not ts.get("user_custom_design", False):
        _su, site_ts = _resolve_site_admin_theme(adapter, normalize_settings(DEFAULT_SETTINGS))
        ts = {**site_ts, **{k: ts[k] for k in ("user_menu_layout", "user_night_bg") if k in ts}}
        if ts.get("user_menu_layout") in ("top", "sidebar"):
            ts["menu_layout"] = ts["user_menu_layout"]
    ts["menu_layout"] = "top" if ts.get("menu_layout") == "sidebar" else "sidebar"
    ts["user_menu_layout"] = ts["menu_layout"]
    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
        table_header_color=ts.get("table_header_color", ""),
    )
    adapter.save_settings(request.user, ts, palette=palette, manual_precision=False)
    next_url = (request.GET.get("next") or request.POST.get("next") or "").strip()
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect(request.META.get("HTTP_REFERER") or "/")


@login_required
def export_theme_json_view(request):
    adapter = get_storage_adapter()
    ts = adapter.get_settings(request.user)
    payload = serialize_export_payload(ts)
    resp = HttpResponse(json.dumps(payload, indent=2), content_type="application/json")
    resp["Content-Disposition"] = 'attachment; filename="design-studio-theme.json"'
    return resp


@login_required
@require_POST
def import_theme_json_view(request):
    from django.utils.http import url_has_allowed_host_and_scheme

    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    if not is_admin:
        return HttpResponseForbidden(_("Nur Administratoren dürfen Themes importieren."))
    adapter = get_storage_adapter()
    raw_text = ""
    if request.FILES.get("theme_file"):
        raw_text = request.FILES["theme_file"].read().decode("utf-8", errors="replace")
    elif request.POST.get("theme_json"):
        raw_text = request.POST.get("theme_json", "")
    elif request.body:
        raw_text = request.body.decode("utf-8", errors="replace")

    next_target = (request.POST.get("next") or request.META.get("HTTP_REFERER") or "").strip()
    if not next_target or not url_has_allowed_host_and_scheme(
        next_target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_target = "design_studio:studio"

    try:
        parsed = json.loads(raw_text)
        imported = parse_import_payload(parsed)
    except Exception as exc:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "message": str(exc)}, status=400)
        messages.error(request, _("Ungültige Theme-JSON-Datei."))
        return redirect(next_target)

    palette = compute_theme_palette(
        c1=imported["c1"],
        c2=imported["c2"],
        mood_key=imported["mood"],
        bg_mode=imported["bg_mode"],
        bg_custom=imported["bg_custom"],
        state_overrides=imported.get("state_overrides"),
    )
    adapter.save_settings(request.user, imported, palette=palette, manual_precision=False)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "theme_studio": imported})
    messages.success(request, _("Theme-Vorlage erfolgreich importiert."))
    return redirect(next_target)


def _pwa_theme_context(request):
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        ts = get_storage_adapter().get_settings(user)
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
    app_name = ts.get("brand_title") or getattr(django_settings, "DESIGN_STUDIO_APP_NAME", "App")
    return ts, palette, str(app_name)


def pwa_manifest_view(request):
    _, palette, app_name = _pwa_theme_context(request)
    icons = getattr(django_settings, "DESIGN_STUDIO_PWA_ICONS", None) or [
        {
            "src": reverse("design_studio:pwa_icon_svg"),
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable",
        }
    ]
    payload = {
        "name": app_name,
        "short_name": app_name[:12],
        "start_url": getattr(django_settings, "DESIGN_STUDIO_PWA_START_URL", "/"),
        "scope": "/",
        "display": "standalone",
        "theme_color": palette.get("primary_color", "#0d6efd"),
        "background_color": palette.get("background_color", "#ffffff"),
        "icons": icons,
    }
    return HttpResponse(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/manifest+json; charset=utf-8",
    )


def pwa_icon_svg_view(request):
    _, palette, app_name = _pwa_theme_context(request)
    c1 = escape(palette.get("c1", "#6610f2"))
    c2 = escape(palette.get("c2", "#0d6efd"))
    letter = escape((getattr(django_settings, "DESIGN_STUDIO_PWA_ICON_TEXT", "") or app_name[:1] or "A").upper())
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/>'
        '</linearGradient></defs>'
        '<rect width="512" height="512" rx="112" fill="url(#g)"/>'
        f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" '
        'font-family="system-ui,-apple-system,sans-serif" font-weight="700" font-size="260" fill="#ffffff">'
        f"{letter}</text></svg>"
    )
    return HttpResponse(svg, content_type="image/svg+xml; charset=utf-8")


def pwa_sw_view(request):
    static_url = getattr(django_settings, "STATIC_URL", "/static/").rstrip("/") + "/"
    sw_js = f"""const CACHE_NAME = 'ds-pwa-v1.5.0';
const STATIC_PREFIX = '{static_url}design_studio/';

self.addEventListener('install', (event) => {{
    self.skipWaiting();
}});

self.addEventListener('activate', (event) => {{
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
}});

self.addEventListener('fetch', (event) => {{
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return;

    if (url.pathname.startsWith(STATIC_PREFIX)) {{
        event.respondWith(
            fetch(req).then((res) => {{
                if (res && res.status === 200) {{
                    const copy = res.clone();
                    caches.open(CACHE_NAME).then((c) => c.put(req, copy));
                }}
                return res;
            }}).catch(() => caches.match(req))
        );
        return;
    }}

    if (req.mode === 'navigate') {{
        event.respondWith(
            fetch(req).catch(() => caches.match(req))
        );
    }}
}});
"""
    resp = HttpResponse(sw_js, content_type="application/javascript; charset=utf-8")
    resp["Service-Worker-Allowed"] = "/"
    return resp


def admin_theme_css_view(request):
    ts, palette, _ = _pwa_theme_context(request)
    c1 = palette.get("c1", "#6610f2")
    c2 = palette.get("c2", "#0d6efd")
    primary = palette.get("primary_color", "#0d6efd")
    bg = palette.get("background_color", "#ffffff")
    fg = palette.get("text_color", "#212529")
    sidebar_bg = palette.get("sidebar_bg_color", "#f8f9fa")
    tbl_head_bg = palette.get("table_header_bg_color", primary)
    tbl_head_fg = palette.get("table_header_text_color", "#ffffff")
    border = palette.get("table_border_color", "rgba(128,128,128,0.22)")
    is_dark = bool(palette.get("is_dark"))
    brutal = bool(palette.get("brutal")) or ts.get("resolved_card_surface") == "brutal"
    radius = "0px" if brutal else "14px"
    btn_radius = "0px" if brutal else "999px"
    quiet = "#94a3b8" if is_dark else "#64748b"

    css = f"""/* Design Studio dynamic CSS variables for Django Admin */
:root,
html[data-theme="light"],
html[data-theme="dark"] {{
    --app-primary: {primary};
    --app-gradient: linear-gradient(135deg, {c1} 0%, {c2} 100%);
    --primary: {primary};
    --secondary: {c1};
    --accent: #ffffff;
    --primary-fg: #ffffff;
    --body-fg: {fg};
    --body-bg: {bg};
    --body-quiet-color: {quiet};
    --body-loud-color: {fg};
    --header-color: #ffffff;
    --header-branding-color: #ffffff;
    --header-bg: {c1};
    --header-link-color: rgba(255, 255, 255, 0.92);
    --breadcrumbs-fg: #ffffff;
    --breadcrumbs-link-fg: rgba(255, 255, 255, 0.9);
    --breadcrumbs-bg: color-mix(in srgb, {c1} 82%, #000000);
    --link-fg: {primary};
    --link-hover-color: {c1};
    --link-selected-fg: {c2};
    --hairline-color: {border};
    --border-color: {border};
    --darkened-bg: {sidebar_bg};
    --selected-bg: color-mix(in srgb, {primary} 14%, {bg});
    --selected-row: color-mix(in srgb, {primary} 12%, {bg});
    --button-fg: #ffffff;
    --button-bg: {primary};
    --button-hover-bg: {c1};
    --default-button-bg: {c1};
    --default-button-hover-bg: {c2};
}}

#header {{
    background: var(--app-gradient) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
    padding: 10px 24px !important;
}}

.ds-admin-branding {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}}

.ds-admin-back-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: {btn_radius};
    background: rgba(255, 255, 255, 0.22) !important;
    color: #ffffff !important;
    font-weight: 700;
    font-size: 0.88rem;
    text-decoration: none !important;
    border: 1px solid rgba(255, 255, 255, 0.34);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.14);
    transition: transform 0.15s ease, background 0.15s ease;
}}
.ds-admin-back-pill:hover {{
    background: rgba(255, 255, 255, 0.34) !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}}

#site-name a {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-weight: 700;
    color: #ffffff !important;
    text-decoration: none !important;
}}

div.breadcrumbs {{
    background: color-mix(in srgb, {primary} 14%, {sidebar_bg}) !important;
    color: {fg} !important;
    border-bottom: 1px solid {border};
}}
div.breadcrumbs a {{
    color: {primary} !important;
    font-weight: 600;
}}

.module,
#content-related,
#changelist-filter,
.inline-group {{
    border-radius: {radius} !important;
    overflow: hidden;
    border: 1px solid {border} !important;
    background: color-mix(in srgb, {primary} 4%, {bg}) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}}

.module h2,
.module caption,
.inline-group h2,
#changelist-filter h2 {{
    background: var(--app-gradient) !important;
    color: {tbl_head_fg} !important;
    font-weight: 700;
}}

#result_list thead th {{
    background: {tbl_head_bg} !important;
    color: {tbl_head_fg} !important;
}}
#result_list thead th a {{
    color: {tbl_head_fg} !important;
}}

.button,
input[type=submit],
input[type=button],
.submit-row input,
a.button,
.object-tools a:link,
.object-tools a:visited {{
    background: var(--app-gradient) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: {btn_radius} !important;
    font-weight: 600;
    padding: 7px 16px;
}}
"""
    return HttpResponse(css, content_type="text/css; charset=utf-8")


@login_required
@require_POST
def upload_genre_bg_view(request):
    from .bg_media import save_user_genre_bg
    from .context_processors import _resolve_site_admin_theme

    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    if not is_admin:
        site_ts, _site_user = _resolve_site_admin_theme(request.user, normalize_settings(DEFAULT_SETTINGS))
        if not bool(site_ts.get("allow_user_design", False)):
            return JsonResponse({"ok": False, "error": "Design-Änderung ist nur für Administratoren freigegeben."}, status=403)

    genre_key = (request.POST.get("genre_key") or "").strip()
    uploaded = request.FILES.get("image")
    try:
        info = save_user_genre_bg(request.user, genre_key, uploaded)
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": f"Upload fehlgeschlagen: {exc}"}, status=500)

    return JsonResponse({
        "ok": True,
        "genre_key": genre_key,
        "url": info["url"],
        "ext": info["ext"],
        "width": info["width"],
        "height": info["height"],
        "size_kb": round(info["size_bytes"] / 1024, 1),
    })


@login_required
@require_POST
def delete_genre_bg_view(request):
    from .bg_media import delete_user_genre_bg
    from .context_processors import _resolve_site_admin_theme

    is_admin = bool(getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False))
    if not is_admin:
        site_ts, _site_user = _resolve_site_admin_theme(request.user, normalize_settings(DEFAULT_SETTINGS))
        if not bool(site_ts.get("allow_user_design", False)):
            return JsonResponse({"ok": False, "error": "Design-Änderung ist nur für Administratoren freigegeben."}, status=403)

    genre_key = (request.POST.get("genre_key") or "").strip()
    removed = delete_user_genre_bg(request.user, genre_key)
    return JsonResponse({"ok": True, "removed": removed, "genre_key": genre_key})


def serve_genre_bg_view(request, genre_key: str):
    from django.http import Http404
    from .bg_media import CONTENT_TYPE_BY_EXT, get_user_genre_bg_path
    from .context_processors import _resolve_site_admin_theme

    clean_key = (genre_key or "").strip()
    path = None
    if getattr(request.user, "is_authenticated", False):
        path = get_user_genre_bg_path(request.user, clean_key)
    if not path or not path.is_file():
        _site_ts, site_user = _resolve_site_admin_theme(getattr(request, "user", None), normalize_settings(DEFAULT_SETTINGS))
        if site_user is not None:
            path = get_user_genre_bg_path(site_user, clean_key)
    if not path or not path.is_file():
        raise Http404("Kein eigenes Hintergrundbild vorhanden.")
    ext = path.suffix.lstrip(".").lower()
    content_type = CONTENT_TYPE_BY_EXT.get(ext, "application/octet-stream")
    resp = HttpResponse(path.read_bytes(), content_type=content_type)
    resp["Cache-Control"] = "private, max-age=86400"
    resp["X-Content-Type-Options"] = "nosniff"
    return resp


@login_required
def branding_view(request):
    from django.contrib import messages
    from .branding import DEFAULT_CHANNELS, get_branding_context, merge_channels_config
    from .models import BrandingProfile

    if not (getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False)):
        return HttpResponse("Kein Zugriff.", status=403)

    bp = BrandingProfile.get_solo()
    if request.method == "POST":
        bp.org_name = (request.POST.get("org_name") or "").strip()[:140]
        bp.tagline = (request.POST.get("tagline") or "").strip()[:200]
        bp.address = (request.POST.get("address") or "").strip()
        bp.phone = (request.POST.get("phone") or "").strip()[:60]
        bp.email = (request.POST.get("email") or "").strip()[:140]
        bp.reply_to_email = (request.POST.get("reply_to_email") or "").strip()[:140]
        bp.website = (request.POST.get("website") or "").strip()[:200]
        bp.tax_id = (request.POST.get("tax_id") or "").strip()[:80]
        bp.iban = (request.POST.get("iban") or "").strip()[:60]
        bp.bic = (request.POST.get("bic") or "").strip()[:30]
        bp.press_person_ref = (request.POST.get("press_person_ref") or "").strip()[:64]
        bp.press_contact = (request.POST.get("press_contact") or "").strip()
        bp.about_short = (request.POST.get("about_short") or "").strip()
        bp.email_signature = (request.POST.get("email_signature") or "").strip()
        bp.footer_text = (request.POST.get("footer_text") or "").strip()[:240]
        if request.FILES.get("logo"):
            bp.logo = request.FILES["logo"]
        elif request.POST.get("remove_logo") == "1":
            bp.logo = None

        ch_cfg = {}
        for ch, opts in DEFAULT_CHANNELS.items():
            ch_cfg[ch] = {k: bool(request.POST.get(f"ch_{ch}_{k}")) for k in opts}
        bp.channels_config_json = ch_cfg
        bp.save()
        messages.success(request, "Branding & Kanal-Einstellungen gespeichert.")
        return redirect("design_studio:branding")

    person_options = []
    try:
        from django.apps import apps
        if apps.is_installed("domain_kit"):
            Person = apps.get_model("domain_kit", "Person")
            for p in Person.objects.prefetch_related("roles").order_by("last_name", "first_name"):
                role_names = ", ".join(r.name for r in p.roles.all())
                person_options.append({
                    "ref": f"person:{p.id}",
                    "label": f"{p.full_name} ({role_names})" if role_names else p.full_name,
                })
    except Exception:
        pass

    channels = merge_channels_config(bp.channels_config_json)
    return render(request, "design_studio/branding.html", {
        "bp": bp,
        "channels": channels,
        "person_options": person_options,
        "branding_preview": get_branding_context("pdf"),
    })
