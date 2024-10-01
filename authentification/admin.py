from django.contrib import admin
from . import models

admin.site.register(models.CustomUser)
admin.site.register(models.BuildingsPolygons)
admin.site.register(models.ElectricityLines)
admin.site.register(models.Yaounde)