# import datetime
# import os

# from django.contrib.postgres.fields import JSONField
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _

# from tumar.animals.models import Cadastre

# # Create your models here.


# class DividedContinuousCeleryResponseQuerySet(models.QuerySet):
#     def delete(self, *args, **kwargs):
#         for obj in self:
#             if obj.is_layer_created:
#                 try:
#                     layer_delete_tiff(self)
#                 except Exception as e:
#                     print(str(e))
#         super(DividedContinuousCeleryResponseQuerySet, self).delete(*args, **kwargs)

# class ImageryRequest(models.Model):
#     cadastre = models.ForeignKey(Cadastre, on_delete=models.CASCADE,
#                                  related_name="imagery_requests", verbose_name=_('Cadastre'))
#     ndvi = JSONField()
#     gndvi = JSONField()
#     clgreen = JSONField()
#     ndmi = JSONField()
#     ndsi = JSONField()
#     actual_date = models.DateTimeField()
#     results_dir = models.TextField()
#     is_layer_created = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = _('Imagery Request')
#         verbose_name_plural = _('Imagery Requests')
#         unique_together = (("actual_date", "divided_cadastre_user"),)

#     objects = DividedContinuousCeleryResponseQuerySet.as_manager()



# class ImageryPNGs(models.Model):
#     imagery_request = models.OneToOneField(ImageryRequest, on_delete=models.CASCADE,
#                                          related_name="imagery_pngs", verbose_name=_('Imagery Request'))
#     clgreen = models.ImageField(upload_to='clgreen', max_length = 300, null = True)
#     ndvi = models.ImageField(upload_to='ndvi', max_length = 300, null = True)
#     gndvi = models.ImageField(upload_to='gndvi', max_length = 300, null = True)
#     ndmi = models.ImageField(upload_to='ndmi', max_length = 300, null = True)
#     rgb = models.ImageField(upload_to='rgb', max_length = 300, null = True)

#     class Meta:
#         verbose_name = _('Imagery Request')
#         verbose_name_plural = _('Imagery Requests')


# from geoserver.catalog import Catalog
# def layer_delete_tiff(request, name_part='_continuous_'):
#     geo_url = 'http://geoserver:8080/geoserver/rest/' if os.getenv(
#         'DEFAULT_DB_HOST') else 'https://geo.egistic.kz/geoserver/rest/'
#     cat = Catalog(geo_url, 'admin', 'UxeiJ5ree2riVoi')
#     ndmi = cat.get_layer("ndmi{}{}".format(name_part, str(request.id)))
#     ndvi =  cat.get_layer("ndvi{}{}".format(name_part, str(request.id)))
#     gndvi =  cat.get_layer("gndvi{}{}".format(name_part, str(request.id)))
#     clgreen =  cat.get_layer("clgreen{}{}".format(name_part, str(request.id)))
#     rgb =  cat.get_layer("rgb{}{}".format(name_part, str(request.id)))
#     cat.delete(ndmi)
#     cat.delete(ndvi)
#     cat.delete(gndvi)
#     cat.delete(clgreen)
#     cat.delete(rgb)
#     cat = Catalog(geo_url, 'admin', 'UxeiJ5ree2riVoi')
#     ndmi = cat.get_store("ndmi{}{}".format(name_part, str(request.id)))
#     ndvi =  cat.get_store("ndvi{}{}".format(name_part, str(request.id)))
#     gndvi =  cat.get_store("gndvi{}{}".format(name_part, str(request.id)))
#     clgreen =  cat.get_store("clgreen{}{}".format(name_part, str(request.id)))
#     rgb =  cat.get_store("rgb{}{}".format(name_part, str(request.id)))
#     cat.delete(ndmi)
#     cat.delete(ndvi)
#     cat.delete(gndvi)
#     cat.delete(clgreen)
#     cat.delete(rgb)