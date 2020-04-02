from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnimalsConfig(AppConfig):
    name = "tumar.animals"
    verbose_name = _("Farms, Animals")
