import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

REQUIRED_INCLUDES = (
    "design_studio/includes/head.html",
    "design_studio/includes/body_attrs.html",
    "design_studio/includes/bg_layer.html",
    "design_studio/includes/navbar.html",
    "design_studio/includes/scripts.html",
)


class Command(BaseCommand):
    help = (
        "Prüft die Design-Studio-Integration, erkennt überschattende lokale "
        "Templates/Static-Dateien und kann diese optional bereinigen."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean-overrides",
            action="store_true",
            help="Verschiebt lokale templates/design_studio und static/design_studio in .bak-Ordner.",
        )
        parser.add_argument(
            "--no-backup",
            action="store_true",
            help="Löscht lokale Overrides bei --clean-overrides direkt ohne Backup.",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Beendet mit Fehlercode, wenn Probleme gefunden wurden.",
        )

    def _backup_or_remove(self, path: Path, no_backup: bool):
        if no_backup:
            shutil.rmtree(path)
            self.stdout.write(self.style.SUCCESS(f"Gelöscht: {path}"))
            return
        backup = path.with_name(f"{path.name}.bak")
        idx = 1
        while backup.exists():
            backup = path.with_name(f"{path.name}.bak.{idx}")
            idx += 1
        path.rename(backup)
        self.stdout.write(self.style.SUCCESS(f"Gesichert & entfernt: {path} -> {backup.name}"))

    def _collect_search_dirs(self, base_dir: Path, kind: str) -> list[Path]:
        dirs: list[Path] = []
        default_dir = base_dir / kind
        if default_dir.exists():
            dirs.append(default_dir)
        if kind == "templates":
            for tpl in getattr(settings, "TEMPLATES", []):
                for d in tpl.get("DIRS", []):
                    p = Path(d)
                    if p not in dirs:
                        dirs.append(p)
        elif kind == "static":
            for d in getattr(settings, "STATICFILES_DIRS", []):
                p = Path(d[1] if isinstance(d, (tuple, list)) else d)
                if p not in dirs:
                    dirs.append(p)
        return dirs

    def handle(self, *args, **options):
        base_dir = Path(getattr(settings, "BASE_DIR", "."))
        clean = bool(options.get("clean_overrides"))
        no_backup = bool(options.get("no_backup"))
        strict = bool(options.get("strict"))
        issues: list[str] = []

        # 1. Settings check
        installed = list(getattr(settings, "INSTALLED_APPS", []))
        if "design_studio" not in installed:
            issues.append("INSTALLED_APPS enthält 'design_studio' nicht.")

        has_ctx = any(
            "design_studio.context_processors.theme_context" in tpl.get("OPTIONS", {}).get("context_processors", [])
            for tpl in getattr(settings, "TEMPLATES", [])
        )
        if not has_ctx:
            issues.append("TEMPLATES context_processors enthält 'design_studio.context_processors.theme_context' nicht.")

        # 2. Override check (Typ-A-Problem)
        pkg_root = Path(__file__).resolve().parents[3]
        for kind in ("templates", "static"):
            for parent in self._collect_search_dirs(base_dir, kind):
                candidate = parent / "design_studio"
                if not candidate.exists() or not candidate.is_dir():
                    continue
                if candidate.resolve() == pkg_root.resolve():
                    continue
                if clean:
                    self._backup_or_remove(candidate, no_backup=no_backup)
                else:
                    issues.append(f"Lokaler Override überschattet Paket-Updates: {candidate}")

        # 3. base.html check
        base_html = None
        for parent in self._collect_search_dirs(base_dir, "templates"):
            candidate = parent / "base.html"
            if candidate.exists():
                base_html = candidate
                break

        if base_html is not None:
            content = base_html.read_text(encoding="utf-8", errors="ignore")
            if "design_studio/layouts/base.html" in content:
                self.stdout.write(self.style.SUCCESS(f"base.html (Typ B): erbt von Paket-Layout ({base_html})"))
            else:
                missing = [inc for inc in REQUIRED_INCLUDES if inc not in content]
                if missing:
                    issues.append(f"base.html ({base_html}) fehlen Includes: {', '.join(missing)}")
                else:
                    self.stdout.write(self.style.SUCCESS(f"base.html (Typ A): alle 5 Includes vorhanden ({base_html})"))

        if issues:
            for msg in issues:
                self.stdout.write(self.style.WARNING(f"[WARN] {msg}"))
            if strict:
                raise CommandError(f"{len(issues)} Problem(e) gefunden.")
        else:
            self.stdout.write(self.style.SUCCESS("Design Studio Doctor: Alles OK."))
