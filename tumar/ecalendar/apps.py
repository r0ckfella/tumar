from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EcalendarConfig(AppConfig):
    name = 'tumar.ecalendar'
    verbose_name = _('Animals Calendar')

    def ready(self):
        from . import signals
