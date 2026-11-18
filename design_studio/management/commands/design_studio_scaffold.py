from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

BASE_HTML_STARTER = """{% extends "design_studio/layouts/base.html" %}
{# Passe hier projektweite Blöcke an, z. B. {% block footer %}...{% endblock %} #}
"""

DASHBOARD_HTML_STARTER = """{% extends "design_studio/layouts/dashboard.html" %}

{% block page_title %}Dashboard{% endblock %}
{% block page_subtitle %}Übersicht{% endblock %}

{% block kpi_cards %}
    {# Optionale Parameter: target_url="/pfad/", target_tab="tab_id", hover_rows=meine_liste #}
    {% include "design_studio/components/kpi_card.html" with title="Beispiel-KPI" value="42" unit="Stk." icon="bi-speedometer2" size="sm" %}
{% endblock %}
"""


class Command(BaseCommand):
    help = "Erstellt optionale Starter-Templates (templates/base.html, templates/dashboard.html), ohne bestehende Dateien zu überschreiben."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Bestehende Dateien überschreiben.",
        )

    def handle(self, *args, **options):
        base_dir = Path(getattr(settings, "BASE_DIR", "."))
        tpl_dir = base_dir / "templates"
        tpl_dir.mkdir(parents=True, exist_ok=True)
        force = bool(options.get("force"))

        targets = {
            tpl_dir / "base.html": BASE_HTML_STARTER,
            tpl_dir / "dashboard.html": DASHBOARD_HTML_STARTER,
        }
        for path, content in targets.items():
            if path.exists() and not force:
                self.stdout.write(self.style.WARNING(f"Übersprungen (existiert bereits): {path}"))
                continue
            path.write_text(content, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Erstellt: {path}"))
