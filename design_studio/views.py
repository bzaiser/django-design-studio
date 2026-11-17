import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .engine import (
    APP_PRESETS,
    MOODS,
    compute_theme_palette,
    hex_to_hsl,
    normalize_settings,
    parse_import_payload,
    serialize_export_payload,
)
from .storage import get_storage_adapter


@login_required
def studio_view(request):
    adapter = get_storage_adapter()
    ts = adapter.get_settings(request.user)
    if request.method == "POST":
        return save_studio_view(request)
    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
    )
    referer = request.META.get("HTTP_REFERER", "")
    next_param = request.GET.get("next", "").strip()
    if next_param:
        request.session["ds_return_url"] = next_param
    elif referer and "/design-studio" not in referer:
        request.session["ds_return_url"] = referer
    back_url = next_param or request.session.get("ds_return_url") or "/"
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
    adapter = get_storage_adapter()
    prev = adapter.get_settings(request.user)

    preset_key = request.POST.get("app_preset", "").strip()
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
        }

    norm = normalize_settings(merged)
    palette = compute_theme_palette(
        c1=norm["c1"],
        c2=norm["c2"],
        mood_key=norm["mood"],
        bg_mode=norm["bg_mode"],
        bg_custom=norm["bg_custom"],
        state_overrides=norm.get("state_overrides"),
    )
    manual_precision = request.POST.get("theme_manual_precision") == "1"
    adapter.save_settings(request.user, norm, palette=palette, manual_precision=manual_precision)
    messages.success(request, _("Design Studio Einstellungen gespeichert."))
    return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "design_studio:studio")


@login_required
def toggle_night_mode_view(request):
    adapter = get_storage_adapter()
    ts = adapter.get_settings(request.user)
    palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
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

    new_palette = compute_theme_palette(
        c1=ts["c1"],
        c2=ts["c2"],
        mood_key=ts["mood"],
        bg_mode=ts["bg_mode"],
        bg_custom=ts["bg_custom"],
        state_overrides=ts.get("state_overrides"),
    )
    adapter.save_settings(request.user, ts, palette=new_palette, manual_precision=False)
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
    adapter = get_storage_adapter()
    raw_text = ""
    if request.FILES.get("theme_file"):
        raw_text = request.FILES["theme_file"].read().decode("utf-8", errors="replace")
    elif request.POST.get("theme_json"):
        raw_text = request.POST.get("theme_json", "")
    elif request.body:
        raw_text = request.body.decode("utf-8", errors="replace")

    try:
        parsed = json.loads(raw_text)
        imported = parse_import_payload(parsed)
    except Exception as exc:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "message": str(exc)}, status=400)
        messages.error(request, _("Ungültige Theme-JSON-Datei."))
        return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "design_studio:studio")

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
    return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "design_studio:studio")
