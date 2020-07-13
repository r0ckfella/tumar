from django.utils.translation import gettext_lazy as _


MALE = "ML"
FEMALE = "FM"

GENDER_CHOICES = [(MALE, _("Бычок")), (FEMALE, _("Телочка"))]

KAZ_LH = "KL"
GEREFORD = "GF"
ANGUS = "AG"
KALMYK = "KM"
AULIYEKOL = "AK"
SIMMENTAL = "SM"
MILK_BREED = "MB"
NO_BREED = "NB"
CROSS = "CR"
OTHER = "OT"

BREED_CHOICES = [
    (KAZ_LH, _("Казахская белоголовая")),
    (GEREFORD, _("Герефорд")),
    (ANGUS, _("Ангус")),
    (KALMYK, _("Калмыцкая")),
    (AULIYEKOL, _("Аулиекольская")),
    (SIMMENTAL, _("Симментал")),
    (MILK_BREED, _("Молочные породы")),
    (NO_BREED, _("Беспородная")),
    (CROSS, _("Кросс")),
    (OTHER, _("Другое")),
]
