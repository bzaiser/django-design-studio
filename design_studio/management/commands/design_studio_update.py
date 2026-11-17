import os
import signal
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

DEFAULT_REPO = "git+https://github.com/bzaiser/django-design-studio.git@main"


class Command(BaseCommand):
    help = (
        "Aktualisiert django-design-studio aus Git, führt Migrationen sowie "
        "collectstatic aus und kann Gunicorn per SIGHUP neu laden."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--repo",
            default=getattr(settings, "DESIGN_STUDIO_REPO_URL", DEFAULT_REPO),
            help="Git- oder Paket-Quelle für pip install.",
        )
        parser.add_argument(
            "--target",
            default=os.environ.get("DESIGN_STUDIO_TARGET", ""),
            help="Optionales Zielverzeichnis (z. B. /opt/ds-pkg bei Volume-Mount).",
        )
        parser.add_argument(
            "--skip-migrate",
            action="store_true",
            help="Überspringt migrate design_studio.",
        )
        parser.add_argument(
            "--skip-collectstatic",
            action="store_true",
            help="Überspringt collectstatic.",
        )
        parser.add_argument(
            "--reload-gunicorn",
            action="store_true",
            help="Sendet SIGHUP an Gunicorn (POSIX), um Code & Templates ohne Container-Rebuild neu zu laden.",
        )
        parser.add_argument(
            "--gunicorn-pid",
            type=int,
            default=1,
            help="PID des Gunicorn-Master-Prozesses (Standard: 1).",
        )

    def handle(self, *args, **options):
        repo = options["repo"]
        target = (options.get("target") or "").strip()

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            "--no-cache-dir",
        ]
        if target:
            cmd.extend(["--target", target])
        cmd.append(repo)

        self.stdout.write(f"Starte Update: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"pip install fehlgeschlagen (Exit {exc.returncode}).") from exc

        if not options.get("skip_migrate"):
            call_command("migrate", "design_studio", interactive=False, stdout=self.stdout)

        if not options.get("skip_collectstatic"):
            if getattr(settings, "STATIC_ROOT", None):
                call_command("collectstatic", interactive=False, stdout=self.stdout)
            else:
                self.stdout.write(self.style.WARNING("collectstatic übersprungen: STATIC_ROOT ist nicht gesetzt."))

        if options.get("reload_gunicorn"):
            if hasattr(signal, "SIGHUP"):
                pid = int(options.get("gunicorn_pid") or 1)
                os.kill(pid, signal.SIGHUP)
                self.stdout.write(self.style.SUCCESS(f"SIGHUP an Gunicorn PID {pid} gesendet."))
            else:
                self.stdout.write(self.style.WARNING("SIGHUP auf diesem Betriebssystem nicht verfügbar."))

        self.stdout.write(self.style.SUCCESS("Design Studio Update abgeschlossen."))
