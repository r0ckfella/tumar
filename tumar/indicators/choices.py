from django.utils.translation import gettext_lazy as _


PENDING = "PE"
WAITING = "WA"
PROCESSING = "PR"
FINISHED = "FI"
FAILED = "FA"
FREE_EXPIRED = "FE"

STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (WAITING, _("Waiting for new imagery")),
    (PROCESSING, _("Processing")),
    (FINISHED, _("Finished")),
    (FAILED, _("Failed")),
    (FREE_EXPIRED, _("Free requests expired")),
]
