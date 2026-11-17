from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserThemePreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="design_studio_preference",
    )
    config = models.JSONField(_("Design Studio Config"), default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Design Studio Preference")
        verbose_name_plural = _("Design Studio Preferences")

    def __str__(self):
        return f"DesignStudio({self.user})"
