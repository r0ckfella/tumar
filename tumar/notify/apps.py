from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotifyConfig(AppConfig):
    name = "tumar.notify"
    verbose_name = _("Notifications")
