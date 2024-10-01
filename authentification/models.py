from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon



class CustomUser(AbstractUser):
    code = models.IntegerField(default=0)
    profession = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self):
        return self.username
    
class BuildingsPolygons(models.Model):
    """
    Modèle représentant les polygones de bâtiments avec des données associées d'OpenStreetMap.
    """

    geom = models.MultiPolygonField(srid=4326)
    osm_id = models.CharField(max_length=80, blank=True, null=True, db_index=True)
    osm_way_id = models.CharField(max_length=80, blank=True, null=True, db_index=True)
    building = models.CharField(max_length=80, blank=True, null=True)
    name = models.CharField(max_length=147, blank=True, null=True)
    amenity = models.CharField(max_length=80, blank=True, null=True)
    office = models.CharField(max_length=80, blank=True, null=True)
    shop = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        db_table = 'CM_2018-09-19_WGS84_buildings_polygons_buildings'
        ordering = ['name']

class Yaounde(models.Model):
    """
    Modèle représentant la géométrie de Yaoundé avec des informations de division.
    """
    id = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(srid=4326)
    division = models.CharField(max_length=41, blank=True, null=True)

    class Meta:
        db_table = 'Yaounde'
        ordering = ['division']

class ElectricityLines(models.Model):
    """
    Modèle représentant les lignes électriques avec des données associées d'OpenStreetMap.
    """
 
    geom = models.MultiLineStringField(srid=4326)
    osm_id = models.CharField(max_length=80, blank=True, null=True, db_index=True)
    power = models.CharField(max_length=80, blank=True, null=True)
    cables = models.CharField(max_length=80, blank=True, null=True)
    circuits = models.CharField(max_length=80, blank=True, null=True)
    voltage = models.CharField(max_length=80, blank=True, null=True)
    wires = models.CharField(max_length=80, blank=True, null=True)
    location = models.CharField(max_length=80, blank=True, null=True)
    division = models.CharField(max_length=41, blank=True, null=True)

    class Meta:
        db_table = 'yde_CM_2018-09-19_WGS84_energy_electricity_lines_electricity-di'
        ordering = ['location']
