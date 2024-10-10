from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from osgeo import gdal
import random
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def send_email_with_html_body(subjet:str, receivers:list, template:str, context:dict):
    ''' Envoyer un email personnaliser à un utilisateur spécifique. '''

    try:
        message = render_to_string(template, context)

        send_mail(
            subjet,
            message,
            settings.EMAIL_HOST_USER,
            receivers,
            fail_silently=True,
            html_message=message,
        )
        
        return True
        
    except Exception as e:
        logger.error(e)
        
    return False

def generate_verif_code():
    code = ''
    
    for i in range(6):
        code += str(random.randint(0, 9))
    
    return int(code)

def handle_uploaded_file(f, filename):
    """Enregistrer les fichiers téléchargés dans le système de fichiers."""
    with open(f'media/{filename}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
def get_raster_bounds(tiff_path):
    """Obtenir les limites géographiques d'un raster géoréférencé avec validation des coordonnées"""
    dataset = gdal.Open(tiff_path)
    
    if not dataset:
        raise Exception(f"Impossible d'ouvrir le fichier raster : {tiff_path}")
    
    try:
        # Obtenir la transformation géographique
        geotransform = dataset.GetGeoTransform()
        if not geotransform:
            raise Exception(f"Le fichier raster n'a pas de transformation géographique : {tiff_path}")
        
        # Vérifier que le fichier a une projection définie
        projection = dataset.GetProjection()
        if not projection:
            raise Exception(f"Le fichier raster n'a pas de projection : {tiff_path}")
        
        # Calculer les limites géographiques
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        
        minx = geotransform[0]
        maxy = geotransform[3]
        maxx = minx + width * geotransform[1]
        miny = maxy + height * geotransform[5]

        # Validation des limites géographiques pour la latitude et la longitude
        minx = max(min(minx, 180), -180)  # Limiter minx entre -180 et 180
        maxx = max(min(maxx, 180), -180)  # Limiter maxx entre -180 et 180
        miny = max(min(miny, 90), -90)    # Limiter miny entre -90 et 90
        maxy = max(min(maxy, 90), -90)    # Limiter maxy entre -90 et 90

        return minx, miny, maxx, maxy

    finally:
        dataset = None  # Fermer le dataset proprement

