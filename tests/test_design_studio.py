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
        self.user = User.objects.create_user(username="ds_user", password="pw")
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
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("--target", args)
            self.assertIn("/opt/ds-pkg", args)
            self.assertIn("git+https://example.com/repo.git@main", args)
            self.assertIn("collectstatic übersprungen", out.getvalue())

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


if __name__ == "__main__":
    from django.test.runner import DiscoverRunner
    call_command("migrate", verbosity=0)
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(["tests.test_design_studio"])
    sys.exit(bool(failures))
