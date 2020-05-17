from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IndicatorsConfig(AppConfig):
    name = "tumar.indicators"
    verbose_name = _("Imagery Requests")
