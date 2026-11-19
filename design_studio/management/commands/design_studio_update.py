import os
import signal
import subprocess
import sys

from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

DEFAULT_REPO = "https://github.com/bzaiser/django-design-studio/archive/refs/heads/main.zip"

KIT_REPOS = {
    "design_studio": DEFAULT_REPO,
    "domain_kit": "https://github.com/bzaiser/domain-django-kit/archive/refs/heads/main.zip",
    "auth_kit": "https://github.com/bzaiser/auth-django-kit/archive/refs/heads/main.zip",
    "notify_kit": "https://github.com/bzaiser/notify-django-kit/archive/refs/heads/main.zip",
    "cal_kit": "https://github.com/bzaiser/cal-django-kit/archive/refs/heads/main.zip",
    "grid_kit": "https://github.com/bzaiser/grid-django-kit/archive/refs/heads/main.zip",
    "seed_kit": "https://github.com/bzaiser/seed-django-kit/archive/refs/heads/main.zip",
    "ops_kit": "https://github.com/bzaiser/ops-django-kit/archive/refs/heads/main.zip",
}


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
            "--all-kits",
            action="store_true",
            help="Erkennt und aktualisiert automatisch alle in INSTALLED_APPS aktiven Baukasten-Pakete.",
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
        if not target:
            for p in os.environ.get("PYTHONPATH", "").split(os.pathsep):
                p = p.strip()
                if p and os.path.isdir(p) and os.access(p, os.W_OK):
                    target = p
                    break

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--force-reinstall",
            "--no-deps",
            "--no-cache-dir",
        ]
        if target:
            cmd.extend(["--target", target])
        if options.get("all_kits"):
            installed = set(getattr(settings, "INSTALLED_APPS", []))
            packages = [url for app, url in KIT_REPOS.items() if app in installed]
            if not packages:
                packages = [repo]
            cmd.extend(packages)
        else:
            cmd.append(repo)

        self.stdout.write(f"Starte Update: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"pip install fehlgeschlagen (Exit {exc.returncode}).") from exc

        manage_py = Path(getattr(settings, "BASE_DIR", ".")) / "manage.py"
        use_subproc = manage_py.exists()

        if not options.get("skip_migrate"):
            if use_subproc:
                mig_cmd = [sys.executable, str(manage_py), "migrate", "--noinput"]
                if not options.get("all_kits"):
                    mig_cmd.append("design_studio")
                subprocess.run(mig_cmd, check=True)
            elif options.get("all_kits"):
                call_command("migrate", interactive=False, stdout=self.stdout)
            else:
                call_command("migrate", "design_studio", interactive=False, stdout=self.stdout)

        if not options.get("skip_collectstatic"):
            if getattr(settings, "STATIC_ROOT", None):
                if use_subproc:
                    subprocess.run([sys.executable, str(manage_py), "collectstatic", "--clear", "--noinput"], check=True)
                else:
                    call_command("collectstatic", clear=True, interactive=False, stdout=self.stdout)
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
