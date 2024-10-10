from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from .models import CustomUser
from .utils import generate_verif_code, send_email_with_html_body, handle_uploaded_file, get_raster_bounds

from rest_framework.response import Response
from rest_framework.views import APIView
from osgeo import gdal
import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.naive_bayes import GaussianNB
import rasterio
import subprocess

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profession = request.POST.get('profession')
        
        code = generate_verif_code()
        subject = 'Code de confirmation'
        template = 'authentification/email.html'
        context = {
            'name': f"{first_name} {last_name}",
            'code': code,
        }
        receivers = [email]

        if not all([first_name, last_name, email, username, password, profession]):
            return render(request, 'authentification/register.html', {'error': 'Tous les champs sont obligatoires.'})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'authentification/register.html', {'error': 'Le nom d’utilisateur est déjà pris.'})
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'authentification/register.html', {'error': 'L’adresse email est déjà utilisée.'})

        try:
            has_send = send_email_with_html_body(
                subject=subject,
                receivers=receivers,
                template=template,
                context=context
            )
            
            if has_send:
                user = CustomUser.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                    profession=profession,
                )
                request.session['id'] = user.id
                request.session['code'] = code
                return redirect('authentification:code')
            else:
                return render(request, 'authentification/register.html', {'error': 'Une erreur s\'est produite'})
        except Exception as e:
            return render(request, 'authentification/register.html', {'error': str(e)})

    return render(request, 'authentification/register.html')

def code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            code = int(code)
        except ValueError:
            return render(request, 'authentification/code.html', {'error': 'Code non valide'})

        user = get_object_or_404(CustomUser, id=request.session.get('id'))
        if code == request.session.get('code'):
            user.code = code 
            user.save()
            return redirect('authentification:login')
        else:
            return render(request, 'authentification/code.html', {'error': 'Code non valide'})
            
    return render(request, 'authentification/code.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.code != 0:
            login(request, user)
            request.session['username'] = user.username
            return redirect('authentification:index')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            
    return render(request, 'authentification/login.html')

def user_logout(request):
    logout(request)
    return redirect('authentification:login')

def edit_profil(request):
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        profession = request.POST.get('profession')
        
        user = get_object_or_404(CustomUser, username=request.session.get('username'))
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.profession = profession
        
        request.session['username'] = user.username
        user.save()
        return redirect('authentification:edit')
        
    return render(request, 'authentification/edit.html')

@login_required
def index(request):
    if request.method == 'POST':
        if 'raster' not in request.FILES:
            messages.error(request, 'Veuillez télécharger un fichier raster.')
            return redirect('authentification:index')

        raster_file = request.FILES['raster']
        raster_file.name = 'raster_extrait.tif'
                
        if not raster_file.name.endswith('.tif'):
            messages.error(request, 'Le fichier doit être au format TIFF.')
            return redirect('authentification:index')

        try:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            handle_uploaded_file(raster_file, raster_file.name)
        
            raster_path = os.path.join(settings.MEDIA_ROOT, raster_file.name)
                
            nom_fichier_png = os.path.join(settings.MEDIA_ROOT, 'output_image.png')
            chemin_fichier_png = nom_fichier_png

            commande = ['gdal_translate', '-of', 'PNG', raster_path, chemin_fichier_png]
            
            try:
                # Exécuter la commande
                subprocess.run(commande, check=True)
                print(f"Conversion réussie : {chemin_fichier_png}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la conversion : {e}")
                
            file = open(raster_path, 'rb')
            response = FileResponse(file)
            response['Content-Disposition'] = 'attachment; filename="raster_extrait/tif"'
            return response

        except Exception as e:
            messages.error(request, f"Erreur lors du traitement du fichier: {str(e)}")
            return redirect('authentification:index')
    
    return render(request, 'authentification/index.html')

class RasterImageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            gdal.UseExceptions()
            
            tiff_path = os.path.join(settings.MEDIA_ROOT, 'raster_extrait.tif')

            if not os.path.exists(tiff_path):
                return Response({"error": "Fichier TIFF introuvable"}, status=404)
            
            try:
                minx, miny, maxx, maxy = get_raster_bounds(tiff_path)
            except Exception as e:
                return Response({"error": f"Erreur lors de la récupération des limites: {str(e)}"}, status=500)

            output_filename = 'output_image.png'
            
            image_url = request.build_absolute_uri(settings.MEDIA_URL + output_filename)

            return Response({
                'image': image_url,
                'bounds': [minx, miny, maxx, maxy]
            })

        except Exception as e:
            return Response({"error": f"Erreur inattendue: {str(e)}"}, status=500)

@login_required
def profil(request):
    return render(request, 'authentification/profil.html')