from django.db import models
from django.utils.translation import gettext_lazy as _

from ..users.utils import compress

# Create your models here.


SALE = "SL"
PURCHASE = "PR"
RENT = "RT"

CATEGORY_CHOICES = [
    (SALE, _("Продажа")),
    (PURCHASE, _("Приобретение")),
    (RENT, _("Аренда")),
]


class City(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("Name of the City"))

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def __str__(self):
        return self.name


class CompanyDirection(models.Model):
    title = models.CharField(max_length=80, verbose_name=_("Title of the Direction"))

    class Meta:
        verbose_name = _("Direction of the Company")
        verbose_name_plural = _("Directions of the Company")

    def __str__(self):
        return self.title


class Company(models.Model):
    directions = models.ManyToManyField(
        CompanyDirection,
        related_name="companies",
        verbose_name=_("Directions of the Company"),
    )
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default=SALE,
        verbose_name=_("Category of the Company"),
    )
    cities = models.ManyToManyField(
        City, related_name="companies", verbose_name=_("Cities of the Company"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Title of the Company"))
    product_description = models.TextField(
        blank=True, verbose_name=_("Product Description")
    )
    company_description = models.TextField(
        blank=True, verbose_name=_("Short Company Description")
    )
    phone_numbers = models.CharField(
        max_length=100, blank=True, verbose_name=_("Phone Numbers")
    )
    emails = models.CharField(max_length=100, blank=True, verbose_name=_("Emails"))
    web_sites = models.CharField(max_length=100, blank=True, verbose_name=_("Websites"))
    instagram_url = models.CharField(
        max_length=100, blank=True, verbose_name=_("Instagram")
    )
    facebook_url = models.CharField(
        max_length=100, blank=True, verbose_name=_("Facebook")
    )
    image = models.ImageField(
        upload_to="companyimages",
        max_length=150,
        null=True,
        blank=True,
        verbose_name=_("Company Logo"),
    )

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image:
            # call the compress function
            new_image = compress(self.image)

            # set self.image to new_image
            self.image = new_image

        super().save(*args, **kwargs)
