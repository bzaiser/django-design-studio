from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


class DesignStudioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "design_studio"
    verbose_name = "Design Studio"

    def ready(self):
        pkg_tpl_dir = Path(__file__).resolve().parent / "templates"
        for tpl_cfg in getattr(settings, "TEMPLATES", []):
            dirs = tpl_cfg.get("DIRS")
            if isinstance(dirs, list):
                resolved = [Path(d).resolve() for d in dirs]
                if pkg_tpl_dir.resolve() not in resolved:
                    dirs.append(pkg_tpl_dir)
