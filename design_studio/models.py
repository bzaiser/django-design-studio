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


class BrandingProfile(models.Model):
    """Singleton branding & channel configuration shared across all kits."""
    org_name = models.CharField(max_length=140, blank=True, default="")
    tagline = models.CharField(max_length=200, blank=True, default="")
    logo = models.FileField(upload_to="design_studio/branding/", blank=True, null=True)
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=60, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    reply_to_email = models.EmailField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    tax_id = models.CharField(max_length=80, blank=True, default="")
    iban = models.CharField(max_length=60, blank=True, default="")
    bic = models.CharField(max_length=30, blank=True, default="")
    press_contact = models.TextField(blank=True, default="")
    about_short = models.TextField(blank=True, default="")
    email_signature = models.TextField(blank=True, default="")
    footer_text = models.CharField(max_length=240, blank=True, default="")
    channels_config_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Branding & Kanäle")
        verbose_name_plural = _("Branding & Kanäle")

    @classmethod
    def get_solo(cls):
        obj = cls.objects.order_by("pk").first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    def __str__(self):
        return self.org_name or "BrandingProfile"
