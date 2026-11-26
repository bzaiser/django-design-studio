import json
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "design_studio",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        ROOT_URLCONF="tests.test_design_studio",
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "design_studio.context_processors.theme_context",
                ],
            },
        }],
        STATIC_URL="/static/",
    )
    django.setup()

from django.contrib.auth import get_user_model
from django.urls import include, path

urlpatterns = [
    path("design-studio/", include("design_studio.urls")),
]


class DesignStudioPackageTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="ds_user", password="pw", is_staff=True)
        self.client = Client()
        self.client.force_login(self.user)

    def test_studio_page_save_toggle_export_import(self):
        resp = self.client.get("/design-studio/")
        self.assertEqual(resp.status_code, 200)

        # Save via Studio form
        resp = self.client.post("/design-studio/save/", {
            "kpi_ext_present": "1",
            "gradient_start": "#1e3a8a",
            "gradient_end": "#0f766e",
            "theme_mood": "serioes",
            "theme_bg_mode": "light",
            "theme_card_surface": "glass",
            "theme_bg_svg_mode": "grid",
            "theme_sync_cards": "on",
            "kpi_sparklines": "on",
            "theme_menu_layout": "sidebar",
            "theme_menu_style": "glass",
            "menu_config_json": json.dumps([
                {"id": "design_studio", "label": "Studio", "icon": "bi-palette", "display": "icon_text", "zone": "utility", "visible": True, "order": 1}
            ]),
            "next": "/",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/")

        studio_html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn("Abbrechen", studio_html)
        self.assertIn("dsMenuTableBody", studio_html)

    def test_starter_layouts_render_and_scaffold_protects_existing_files(self):
        import tempfile
        from pathlib import Path
        from django.template.loader import render_to_string
        from django.test import RequestFactory, override_settings

        rf = RequestFactory()
        req = rf.get("/")
        req.user = self.user
        for tpl in (
            "design_studio/layouts/base.html",
            "design_studio/layouts/dashboard.html",
            "design_studio/layouts/list_page.html",
            "design_studio/components/kpi_card.html",
        ):
            html = render_to_string(tpl, {"title": "Test KPI", "value": "99", "unit": "€", "icon": "bi-star"}, request=req)
            self.assertTrue(len(html) > 20)

        with tempfile.TemporaryDirectory() as tmp:
            tpl_dir = Path(tmp) / "templates"
            tpl_dir.mkdir(parents=True, exist_ok=True)
            existing = tpl_dir / "base.html"
            existing.write_text("CUSTOM_KEEP", encoding="utf-8")
            with override_settings(BASE_DIR=tmp):
                call_command("design_studio_scaffold")
            self.assertEqual(existing.read_text(encoding="utf-8"), "CUSTOM_KEEP")
            self.assertTrue((tpl_dir / "dashboard.html").exists())

        # Save preset
        resp = self.client.post("/design-studio/save/", {"app_preset": "neon_dark"})
        self.assertEqual(resp.status_code, 302)

        # Export JSON
        exp = self.client.get("/design-studio/export/")
        self.assertEqual(exp.status_code, 200)
        data = json.loads(exp.content.decode("utf-8"))
        self.assertEqual(data["mood"], "neon")
        self.assertEqual(data["bg_mode"], "dark")

        # Toggle Night -> Day -> Night
        self.client.get("/design-studio/toggle-night/")
        exp_day = json.loads(self.client.get("/design-studio/export/").content.decode("utf-8"))
        self.assertEqual(exp_day["bg_mode"], "light")

        # Import modified JSON
        data["mood"] = "serioes"
        data["card_surface"] = "glass"
        imp = self.client.post(
            "/design-studio/import/",
            {"theme_json": json.dumps(data)},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(imp.status_code, 200)
        self.assertEqual(imp.json()["theme_studio"]["mood"], "serioes")

    def test_doctor_detects_and_cleans_overrides_and_checks_base_html(self):
        import io
        import tempfile
        from pathlib import Path
        from django.core.management.base import CommandError

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            override_dir = tmp_path / "templates" / "design_studio" / "includes"
            override_dir.mkdir(parents=True)
            (override_dir / "navbar.html").write_text("OLD", encoding="utf-8")

            base_html = tmp_path / "templates" / "base.html"
            base_html.write_text('{% extends "design_studio/layouts/base.html" %}', encoding="utf-8")

            with self.settings(BASE_DIR=tmp_path):
                out = io.StringIO()
                with self.assertRaises(CommandError):
                    call_command("design_studio_doctor", strict=True, stdout=out)
                self.assertIn("Lokaler Override", out.getvalue())

                out_clean = io.StringIO()
                call_command("design_studio_doctor", clean_overrides=True, strict=True, stdout=out_clean)
                self.assertFalse((tmp_path / "templates" / "design_studio").exists())
                self.assertTrue((tmp_path / "templates" / "design_studio.bak").exists())
                self.assertIn("Alles OK", out_clean.getvalue())

    def test_update_command_runs_pip_with_target_and_skips_missing_static_root(self):
        import io
        from unittest.mock import patch

        with patch("design_studio.management.commands.design_studio_update.subprocess.run") as mock_run:
            out = io.StringIO()
            call_command(
                "design_studio_update",
                target="/opt/ds-pkg",
                repo="git+https://example.com/repo.git@main",
                stdout=out,
            )
            self.assertGreaterEqual(mock_run.call_count, 1)
            args = mock_run.call_args_list[0][0][0]
            self.assertIn("--upgrade", args)
            self.assertIn("--target", args)
            self.assertIn("/opt/ds-pkg", args)
            self.assertIn("git+https://example.com/repo.git@main", args)
            self.assertIn("collectstatic übersprungen", out.getvalue())

            mock_run.reset_mock()
            with patch.object(settings, "INSTALLED_APPS", ["design_studio", "django.contrib.auth"]):
                call_command("design_studio_update", all_kits=True, skip_migrate=True, target="/opt/ds-pkg", stdout=io.StringIO())
                args_all = mock_run.call_args[0][0]
                self.assertTrue(any("django-design-studio" in a for a in args_all))
                self.assertFalse(any("domain-django-kit" in a for a in args_all))

    def test_offline_vendor_assets_and_cdn_free_templates(self):
        from pathlib import Path
        pkg_dir = Path(__file__).resolve().parent.parent / "design_studio"
        vendor = pkg_dir / "static" / "design_studio" / "vendor"
        for rel in (
            "bootstrap/bootstrap.min.css",
            "bootstrap/bootstrap.bundle.min.js",
            "bootstrap-icons/bootstrap-icons.min.css",
            "bootstrap-icons/fonts/bootstrap-icons.woff2",
            "sortable/Sortable.min.js",
        ):
            self.assertTrue((vendor / rel).exists(), f"Missing vendor asset: {rel}")

        for tpl in (
            pkg_dir / "templates" / "design_studio" / "layouts" / "base.html",
            pkg_dir / "templates" / "design_studio" / "studio_page.html",
        ):
            content = tpl.read_text(encoding="utf-8")
            self.assertNotIn("cdn.jsdelivr.net", content)

    def test_expanded_icons_manual_icon_and_brand_title_config(self):
        from design_studio.menu import MENU_ICON_CHOICES

        self.assertGreater(len(MENU_ICON_CHOICES), 100)
        resp = self.client.post(
            "/design-studio/save/",
            {
                "brand_title": "Mein NAS Studio",
                "brand_icon": "bi-hdd-network",
                "menu_config_json": json.dumps([
                    {
                        "id": "design_studio",
                        "icon": "bi-rocket-takeoff",
                        "label": "Start",
                        "display": "icon_text",
                        "zone": "utility",
                        "visible": True,
                        "order": 1,
                    }
                ]),
            },
        )
        self.assertEqual(resp.status_code, 302)
        studio_page = self.client.get("/design-studio/")
        html = studio_page.content.decode("utf-8")
        self.assertIn("Mein NAS Studio", html)
        self.assertIn("bi-hdd-network", html)
        self.assertIn("bi-rocket-takeoff", html)

    def test_toggle_menu_layout_switches_between_top_and_sidebar(self):
        from design_studio.storage import get_storage_adapter

        resp1 = self.client.get("/design-studio/toggle-menu-layout/")
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(get_storage_adapter().get_settings(self.user)["menu_layout"], "sidebar")
        self.assertIn('data-menu-layout="sidebar"', self.client.get("/design-studio/").content.decode("utf-8"))

        resp2 = self.client.get("/design-studio/toggle-menu-layout/")
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(get_storage_adapter().get_settings(self.user)["menu_layout"], "top")
        self.assertIn('data-menu-layout="top"', self.client.get("/design-studio/").content.decode("utf-8"))

    def test_pwa_manifest_icon_and_service_worker(self):
        manifest = self.client.get("/design-studio/manifest.webmanifest")
        self.assertEqual(manifest.status_code, 200)
        self.assertIn("application/manifest+json", manifest["Content-Type"])
        data = json.loads(manifest.content.decode("utf-8"))
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["icons"][0]["src"], "/design-studio/pwa-icon.svg")

        icon = self.client.get("/design-studio/pwa-icon.svg")
        self.assertEqual(icon.status_code, 200)
        self.assertIn("image/svg+xml", icon["Content-Type"])
        self.assertIn("<svg", icon.content.decode("utf-8"))

        sw = self.client.get("/design-studio/sw.js")
        self.assertEqual(sw.status_code, 200)
        self.assertEqual(sw["Service-Worker-Allowed"], "/")
        self.assertIn("CACHE_NAME", sw.content.decode("utf-8"))

        page_html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn('rel="manifest"', page_html)
        self.assertIn("serviceWorker.register", page_html)

    def test_admin_theme_css_maps_palette_variables(self):
        self.client.post("/design-studio/save/", {"app_preset": "neon_dark"})
        css_resp = self.client.get("/design-studio/admin.css")
        self.assertEqual(css_resp.status_code, 200)
        self.assertIn("text/css", css_resp["Content-Type"])
        css_text = css_resp.content.decode("utf-8")
        self.assertIn("--app-gradient:", css_text)
        self.assertIn("--header-bg:", css_text)
        self.assertIn("#header", css_text)

    def test_studio_page_renders_8_state_harmony_grid_and_saves_overrides(self):
        html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn('id="studioStateOverrides"', html)
        self.assertIn('id="studioSwatchGrid"', html)
        resp = self.client.post(
            "/design-studio/save/",
            {"theme_state_overrides": json.dumps({"1": "#26D96B", "8": "#7126D9"})},
        )
        self.assertEqual(resp.status_code, 302)
        exp = json.loads(self.client.get("/design-studio/export/").content.decode("utf-8"))
        self.assertEqual(exp["state_overrides"]["1"], "#26D96B")
        self.assertEqual(exp["state_overrides"]["8"], "#7126D9")

    def test_liquid_glass_density_and_zoom_settings(self):
        resp = self.client.post(
            "/design-studio/save/",
            {
                "theme_card_surface": "liquid",
                "theme_font_scale": "compact",
                "theme_ui_zoom": "75",
                "theme_glass_alpha": "40",
                "theme_glass_blur": "18",
                "theme_bg_strength": "80",
            },
        )
        self.assertEqual(resp.status_code, 302)
        html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn('data-card-surface="liquid"', html)
        self.assertIn('data-font-scale="compact"', html)
        self.assertIn('data-ui-zoom="75"', html)
        self.assertIn("--app-ui-zoom: 75;", html)
        self.assertIn("--glass-alpha: 0.40;", html)
        self.assertIn("--glass-blur: 18px;", html)
        self.assertIn("--bg-strength: 0.80;", html)

    def test_new_liquid_and_density_presets(self):
        resp = self.client.post("/design-studio/save/", {"app_preset": "cockpit_kompakt"})
        self.assertEqual(resp.status_code, 302)
        html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn('data-card-surface="liquid"', html)
        self.assertIn('data-font-scale="compact"', html)
        self.assertIn('data-ui-zoom="95"', html)

    def test_design_studio_css_includes_ds_tabs_and_panel_styles(self):
        from pathlib import Path
        css_path = Path(__file__).resolve().parent.parent / "design_studio" / "static" / "design_studio" / "css" / "design-studio.css"
        css = css_path.read_text(encoding="utf-8")
        self.assertIn(".nav-tabs.ds-tabs", css)
        self.assertIn(".ds-tab-panel", css)

    def test_per_page_genre_saves_and_renders_with_photo_toggle(self):
        resp = self.client.post(
            "/design-studio/save/",
            {
                "theme_genre_photos_enabled": "1",
                "menu_config_json": json.dumps([
                    {"id": "design_studio", "icon": "bi-palette", "label": "Studio", "display": "icon_only", "zone": "utility", "visible": True, "order": 1, "genre": "scifi"},
                ]),
            },
        )
        self.assertEqual(resp.status_code, 302)
        html = self.client.get("/design-studio/").content.decode("utf-8")
        self.assertIn('data-genre="scifi"', html)
        self.assertIn('id="ds-genre-svg-layer"', html)
        self.assertIn('id="ds-genre-photo-layer"', html)
        self.assertIn('ds-menu-genre', html)

    def test_domain_kit_modular_subsections_menu_filtering(self):
        from unittest.mock import MagicMock, patch
        from design_studio.menu import resolve_user_menu

        mock_settings = MagicMock()
        mock_settings.is_module_enabled.side_effect = lambda mod: mod in ("persons", "documents")

        custom_items = [
            {"id": "persons", "url_name": "domain_kit:persons", "default_label": "Personen", "zone": "main", "visible": True},
            {"id": "assets", "url_name": "domain_kit:assets", "default_label": "Assets", "zone": "main", "visible": True},
            {"id": "documents", "url_name": "domain_kit:documents", "default_label": "Dokumente", "zone": "main", "visible": True},
            {"id": "search", "url_name": "domain_kit:search", "default_label": "Suche", "zone": "main", "visible": True},
        ]

        with self.settings(DESIGN_STUDIO_MENU_ITEMS=custom_items):
            with patch("django.apps.apps.is_installed", return_value=True), \
                 patch("django.apps.apps.get_model") as mock_get_model:
                mock_model = MagicMock()
                mock_model.get_solo.return_value = mock_settings
                mock_get_model.return_value = mock_model

                res = resolve_user_menu(user=None)
                all_ids = [it["id"] for it in res["all_items"]]
                self.assertIn("persons", all_ids)
                self.assertIn("documents", all_ids)
                self.assertNotIn("assets", all_ids)
                self.assertNotIn("search", all_ids)

        # Test auto-discovery of enabled domain items when not in DESIGN_STUDIO_MENU_ITEMS at all
        mock_settings.is_module_enabled.side_effect = lambda mod: mod == "master_data"
        with self.settings(DESIGN_STUDIO_MENU_ITEMS=[]):
            with patch("django.apps.apps.is_installed", return_value=True), \
                 patch("django.apps.apps.get_model") as mock_get_model:
                mock_model = MagicMock()
                mock_model.get_solo.return_value = mock_settings
                mock_get_model.return_value = mock_model

                res = resolve_user_menu(user=None)
                all_ids = [it["id"] for it in res["all_items"]]
                self.assertIn("master_data", all_ids)
                self.assertNotIn("persons", all_ids)


    def test_custom_genre_background_upload_validation_serve_and_delete(self):
        import struct
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from design_studio.bg_media import MAX_BYTES, detect_image_info

        def make_png(w, h):
            ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
            return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr + b"\x00\x00\x00\x00"

        def make_jpeg(w, h):
            # Minimal SOI + SOF0 segment with height & width
            sof_body = struct.pack(">BHHB", 8, h, w, 3) + b"\x01\x11\x00\x02\x11\x00\x03\x11\x00"
            return b"\xff\xd8\xff\xc0" + struct.pack(">H", len(sof_body) + 2) + sof_body + b"\xff\xd9"

        def make_webp_vp8x(w, h):
            body = b"\x00\x00\x00\x00" + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")
            return b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WEBP" + b"VP8X" + struct.pack("<I", len(body)) + body

        # Pure-Python header parsing works for PNG, JPEG, WebP
        self.assertEqual(detect_image_info(make_png(1920, 1080)), ("png", 1920, 1080))
        self.assertEqual(detect_image_info(make_jpeg(1280, 720)), ("jpeg", 1280, 720))
        self.assertEqual(detect_image_info(make_webp_vp8x(2560, 1440)), ("webp", 2560, 1440))

        self.client.force_login(self.user)
        with tempfile.TemporaryDirectory() as tmp:
            with self.settings(BASE_DIR=tmp):
                # 1. Reject SVG / non-image format
                r_svg = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "natur", "image": SimpleUploadedFile("bad.svg", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", content_type="image/svg+xml")},
                )
                self.assertEqual(r_svg.status_code, 400)
                self.assertFalse(r_svg.json()["ok"])

                # 2. Reject too small resolution (< 640x360)
                r_small = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "natur", "image": SimpleUploadedFile("tiny.png", make_png(320, 200), content_type="image/png")},
                )
                self.assertEqual(r_small.status_code, 400)
                self.assertIn("640", r_small.json()["error"])

                # 3. Reject too large resolution (> 6000x6000)
                r_huge = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "natur", "image": SimpleUploadedFile("huge.png", make_png(7000, 4000), content_type="image/png")},
                )
                self.assertEqual(r_huge.status_code, 400)
                self.assertIn("6000", r_huge.json()["error"])

                # 4. Reject > 5 MB file
                r_big = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "natur", "image": SimpleUploadedFile("big.png", make_png(1920, 1080) + (b"\x00" * (MAX_BYTES + 10)), content_type="image/png")},
                )
                self.assertEqual(r_big.status_code, 400)
                self.assertIn("5 MB", r_big.json()["error"])

                # 5. Reject unknown genre
                r_bad_genre = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "invalid_genre", "image": SimpleUploadedFile("ok.png", make_png(1280, 720), content_type="image/png")},
                )
                self.assertEqual(r_bad_genre.status_code, 400)

                # 6. Valid PNG upload succeeds and is served with image/png
                r_ok = self.client.post(
                    "/design-studio/genre-bg/upload/",
                    {"genre_key": "natur", "image": SimpleUploadedFile("forest.png", make_png(1920, 1080), content_type="image/png")},
                )
                self.assertEqual(r_ok.status_code, 200)
                data = r_ok.json()
                self.assertTrue(data["ok"])
                self.assertEqual(data["width"], 1920)
                self.assertEqual(data["height"], 1080)
                self.assertIn("/design-studio/genre-bg/natur/", data["url"])

                serve_resp = self.client.get("/design-studio/genre-bg/natur/")
                self.assertEqual(serve_resp.status_code, 200)
                self.assertEqual(serve_resp["Content-Type"], "image/png")

                # 7. Select genre 'natur' WITHOUT internet photos -> custom image STILL renders in bg_layer!
                self.client.post("/design-studio/save/", {"theme_default_genre": "natur"})
                page_html = self.client.get("/design-studio/").content.decode("utf-8")
                self.assertIn("dsGenreBgModal", page_html)
                self.assertIn("/design-studio/genre-bg/natur/", page_html)
                self.assertIn('id="ds-genre-photo-layer"', page_html)

                # 8. Delete custom image -> serve returns 404
                r_del = self.client.post("/design-studio/genre-bg/delete/", {"genre_key": "natur"})
                self.assertEqual(r_del.status_code, 200)
                self.assertTrue(r_del.json()["removed"])
                self.assertEqual(self.client.get("/design-studio/genre-bg/natur/").status_code, 404)

    def test_notify_kit_unread_badge_and_ops_kit_update_dot(self):
        from unittest.mock import MagicMock, patch
        from django.template.loader import render_to_string
        from django.test import RequestFactory
        from design_studio.menu import resolve_user_menu

        self.user.is_staff = True
        self.user.save()

        mock_notif_qs = MagicMock()
        mock_notif_qs.order_by.return_value.values_list.return_value = [
            ("Backup fehlgeschlagen", "danger")
        ] + [(f"Info {i}", "info") for i in range(11)]

        mock_notif_model = MagicMock()
        mock_notif_model.objects.filter.return_value = mock_notif_qs

        mock_update_settings = MagicMock()
        mock_update_settings.last_result_json = {"has_updates": True}
        mock_update_model = MagicMock()
        mock_update_model.get_solo.return_value = mock_update_settings

        def fake_is_installed(app_name):
            return app_name in ("domain_kit", "notify_kit", "ops_kit")

        def fake_get_model(app_label, model_name):
            if app_label == "domain_kit":
                raise RuntimeError("domain_kit DB error should not block notify_kit")
            if app_label == "notify_kit" and model_name == "Notification":
                return mock_notif_model
            if app_label == "ops_kit" and model_name == "UpdateSettings":
                return mock_update_model
            raise LookupError(f"{app_label}.{model_name}")

        with patch("django.apps.apps.is_installed", side_effect=fake_is_installed), \
             patch("django.apps.apps.get_model", side_effect=fake_get_model):
            res = resolve_user_menu(user=self.user)
            self.assertTrue(res["has_updates"])
            self.assertTrue(res["has_notify_item"])
            notif_items = [it for it in res["all_items"] if it["id"] == "notifications"]
            self.assertEqual(len(notif_items), 1)
            notif_item = notif_items[0]
            self.assertEqual(notif_item["badge_count"], 12)
            self.assertEqual(notif_item["badge_level"], "danger")
            self.assertEqual(notif_item["icon"], "bi-bell-fill")
            self.assertIn("12 ungelesen", notif_item["badge_tooltip"])
            self.assertIn("Backup fehlgeschlagen", notif_item["badge_tooltip"])

            studio_items = [it for it in res["all_items"] if it["id"] == "design_studio"]
            self.assertTrue(studio_items[0]["badge_dot"])

            rf = RequestFactory()
            req = rf.get("/design-studio/")
            req.user = self.user
            html = render_to_string("design_studio/layouts/base.html", {}, request=req)
            self.assertIn("app-navbar-header", html)
            self.assertIn("app-navbar-toggles", html)
            self.assertIn("menu-layout-toggle-btn", html)
            self.assertIn("sidebarCollapseBtn", html)
            self.assertIn("ds-nav-badge", html)
            self.assertIn("9+", html)
            self.assertIn("bi-bell-fill", html)
            self.assertIn("ds-nav-dot", html)
            self.assertIn("Neue Updates verfügbar", html)

    def test_anonymous_user_hides_navbar_and_menus(self):
        from django.contrib.auth.models import AnonymousUser
        from django.template.loader import render_to_string
        from django.test import RequestFactory
        from design_studio.context_processors import theme_context

        rf = RequestFactory()
        req = rf.get("/accounts/login/")
        req.user = AnonymousUser()

        ctx = theme_context(req)
        self.assertEqual(ctx["nav_main_items"], [])
        self.assertEqual(ctx["nav_utility_items"], [])
        self.assertEqual(ctx["nav_system_items"], [])
        self.assertFalse(ctx["nav_system_active"])
        self.assertFalse(ctx["nav_has_notify_item"])
        self.assertEqual(ctx["ds_unread_notifications_count"], 0)

        base_html = render_to_string("design_studio/layouts/base.html", {}, request=req)
        self.assertNotIn("<nav class=\"navbar", base_html)
        self.assertNotIn("navMainList", base_html)
        self.assertNotIn("navUtilityList", base_html)

        nav_html = render_to_string("design_studio/includes/navbar.html", {}, request=req)
        self.assertEqual(nav_html.strip(), "")

    def test_optional_kits_auto_discovered_in_menu_with_staff_filter(self):
        from unittest.mock import patch
        from design_studio.menu import resolve_user_menu

        def fake_is_installed(app_name):
            return app_name in ("cal_kit", "list_kit", "site_kit")

        with self.settings(DESIGN_STUDIO_MENU_ITEMS=[]):
            with patch("django.apps.apps.is_installed", side_effect=fake_is_installed):
                # Regular user sees calendar + lists, not staff-only builder / site_manage
                self.user.is_staff = False
                self.user.save()
                res_user = resolve_user_menu(user=self.user)
                user_ids = [it["id"] for it in res_user["all_items"]]
                self.assertIn("calendar", user_ids)
                self.assertIn("lists", user_ids)
                self.assertNotIn("list_builder", user_ids)
                self.assertNotIn("site_manage", user_ids)

                # Staff user sees all auto-discovered kit menu items
                self.user.is_staff = True
                self.user.save()
                res_staff = resolve_user_menu(user=self.user)
                staff_ids = [it["id"] for it in res_staff["all_items"]]
                self.assertIn("calendar", staff_ids)
                self.assertIn("lists", staff_ids)
                self.assertIn("list_builder", staff_ids)
                self.assertIn("site_manage", staff_ids)

    def test_no_missing_migrations(self):
        call_command("makemigrations", "design_studio", "--check", "--dry-run", verbosity=0)

    def test_menu_designer_persists_system_hub_zone_and_moves_back_to_main(self):
        import json
        from django.contrib.auth import get_user_model
        from design_studio.menu import resolve_user_menu
        from design_studio.storage import get_storage_adapter

        staff = get_user_model().objects.create_user(username="menu_adm", password="pw", is_staff=True)
        self.client.force_login(staff)

        payload = json.dumps([
            {"id": "home", "label": "Start", "icon": "bi-house", "display": "icon_text", "zone": "main", "visible": True, "order": 1},
            {"id": "design_studio", "label": "Studio", "icon": "bi-palette", "display": "icon_text", "zone": "system", "visible": True, "order": 2},
        ])
        r = self.client.post("/design-studio/save/", {"menu_config_json": payload})
        self.assertEqual(r.status_code, 302)

        menu = resolve_user_menu(staff, saved_menu_config=get_storage_adapter().get_settings(staff).get("menu_config"))
        sys_ids = [x["id"] for x in menu["system_items"]]
        main_ids = [x["id"] for x in menu["main_items"]]
        self.assertIn("design_studio", sys_ids)
        self.assertNotIn("design_studio", main_ids)

        # Move back to main
        payload2 = json.dumps([
            {"id": "home", "label": "Start", "icon": "bi-house", "display": "icon_text", "zone": "main", "visible": True, "order": 1},
            {"id": "design_studio", "label": "Studio", "icon": "bi-palette", "display": "icon_text", "zone": "main", "visible": True, "order": 2},
        ])
        self.client.post("/design-studio/save/", {"menu_config_json": payload2})
        menu2 = resolve_user_menu(staff, saved_menu_config=get_storage_adapter().get_settings(staff).get("menu_config"))
        self.assertIn("design_studio", [x["id"] for x in menu2["main_items"]])
        self.assertNotIn("design_studio", [x["id"] for x in menu2["system_items"]])

    def test_existing_non_staff_inherits_admin_theme_and_allow_user_design_toggle(self):
        from django.test import RequestFactory
        from design_studio.context_processors import theme_context
        from design_studio.storage import get_storage_adapter

        User = get_user_model()
        admin = User.objects.create_user(username="site_admin_theme", password="pw", is_staff=True, is_superuser=True)
        demo = User.objects.create_user(username="demo_presse_existing", password="pw", is_staff=False)
        adapter = get_storage_adapter()

        # Admin sets custom color + allow_user_design=False
        self.client.force_login(admin)
        self.client.post("/design-studio/save/", {
            "kpi_ext_present": "1",
            "gradient_start": "#123456",
            "gradient_end": "#654321",
        })
        # Simulate demo_presse already having an old blue UserThemePreference row
        old_blue = adapter.get_settings(demo)
        old_blue["c1"] = "#6610f2"
        old_blue["menu_layout"] = "sidebar"
        adapter.save_settings(demo, old_blue)

        # When allow_user_design=False, demo_presse MUST still inherit #123456 from admin
        req = RequestFactory().get("/")
        req.user = demo
        ctx = theme_context(req)
        self.assertEqual(ctx["theme_studio"]["c1"], "#123456")

        # Non-staff cannot open or save /design-studio/ while allow_user_design=False
        self.client.force_login(demo)
        self.assertEqual(self.client.get("/design-studio/").status_code, 403)
        self.assertEqual(self.client.post("/design-studio/save/", {"app_preset": "finanz_serioes"}).status_code, 403)

        # Admin enables allow_user_design=True
        self.client.force_login(admin)
        self.client.post("/design-studio/save/", {
            "kpi_ext_present": "1",
            "gradient_start": "#123456",
            "gradient_end": "#654321",
            "theme_allow_user_design": "1",
        })
        self.client.force_login(demo)
        r_page = self.client.get("/design-studio/")
        self.assertEqual(r_page.status_code, 200)
        html = r_page.content.decode("utf-8")
        self.assertIn("App-Vorlage (1-Klick-Start)", html)
        self.assertNotIn("Menü-Studio", html)

        # Demo user applies finanz_serioes preset + genre
        self.client.post("/design-studio/save/", {"app_preset": "finanz_serioes"})
        self.client.post("/design-studio/save/", {"theme_default_genre": "technik", "theme_genre_photos_enabled": "1"})
        ctx2 = theme_context(req)
        self.assertEqual(ctx2["theme_studio"]["default_genre"], "technik")
        self.assertTrue(ctx2["theme_studio"]["genre_photos_enabled"])
        self.assertNotEqual(ctx2["theme_studio"]["c1"], "#123456")


if __name__ == "__main__":
    from django.test.runner import DiscoverRunner
    call_command("migrate", verbosity=0)
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(["tests.test_design_studio"])
    sys.exit(bool(failures))
