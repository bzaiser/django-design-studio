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


if __name__ == "__main__":
    from django.test.runner import DiscoverRunner
    call_command("migrate", verbosity=0)
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(["tests.test_design_studio"])
    sys.exit(bool(failures))
