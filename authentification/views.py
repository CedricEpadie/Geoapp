from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.geos import MultiPolygon, GEOSGeometry
from .models import *
import json
from .utils import send_email_with_html_body
import random
import ee
import folium

def jsonview(request):
    with open('authentification/static/authentification/TC_14.geojson', 'r') as jsonfile:
        data = json.load(jsonfile)
        
    return JsonResponse(data)

def generate_verif_code():
    code = ''
    
    for i in range(6):
        code += str(random.randint(0, 9))
    
    return int(code)

def register(request):
    if request.method == 'POST':
        
        def insert_electricity_lines_data(sql_data):
            lines = []
            for line in sql_data.split('\n'):
                if line.strip() and not line.startswith('COPY'):
                    fields = line.split('\t')
                    if len(fields) == 10:
                        lines.append(ElectricityLines(
                            geom=GEOSGeometry(fields[1]),
                            osm_id=fields[2],
                            power=fields[3],
                            cables=fields[4] if fields[4] != '\\N' else None,
                            circuits=fields[5] if fields[5] != '\\N' else None,
                            voltage=fields[6] if fields[6] != '\\N' else None,
                            wires=fields[7] if fields[7] != '\\N' else None,
                            location=fields[8] if fields[8] != '\\N' else None,
                            division=fields[9]
                        ))
            
            ElectricityLines.objects.bulk_create(lines)

        # Exemple de données SQL avec tous les champs remplis
        sql_data = """COPY public."yde_CM_2018-09-19_WGS84_energy_electricity_lines_electricity-di" (id, geom, osm_id, power, cables, circuits, voltage, wires, location, "DIVISION") FROM stdin;
        1	0105000020E6100000010000000102000000050000006DC83F3388FF2640399787F13FDE0E40837F5BC180FF26402400492245DE0E40530F2CA281FF264067D9EE7959DE0E403D58101489FF26402E77C13B54DE0E406DC83F3388FF2640399787F13FDE0E40	192841766	line	3	2	220000	4	overhead	Mfoundi
        2	0105000020E610000001000000010200000005000000CA94C5B3BAFB26402E4EC642BE450E401CD4D9249AFB26402A38BC2022450E4011BB004576FB26401DC06C4C99450E40BF7BECD396FB264020D6766E35460E40CA94C5B3BAFB26402E4EC642BE450E40	193588031	minor_line	1	1	11000	3	underground	Mfoundi
        3	0105000020E610000001000000010200000003000000A69BC420B0FD2640E17A14AE47E10E40B81E85EBB1FD26404C37894160E10E40C6A1F2BED3FD2640C3F5285C8FE10E40	193588032	cable	6	3	400000	6	submarine	Mfoundi
        """

        # Appel de la fonction pour insérer les données
        insert_electricity_lines_data(sql_data)
        
        
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profession = request.POST.get('profession')
        
        code = generate_verif_code()
        subjet = 'Code de confirmation'
        template = 'authentification/email.html'
        context = {
            'name': first_name + ' ' + last_name,
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
                subjet=subjet,
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
        code=int(code)
        user = CustomUser.objects.get(id=request.session['id'])
        if code == request.session['code']:
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
        
        if user is not None and user.code == 0 :
            return redirect('authentification:register')
        else:
            if user is not None:
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
        
        user = CustomUser.objects.get(username=request.session.get('username'))
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
    return render(request, 'authentification/index.html')

@login_required
def profil(request):
      return render(request,'authentification/profil.html')
  
def test(request):
    ee.Authenticate()
    # Authentification à Google Earth Engine
    ee.Initialize()

    # Définir les coordonnées de la carte
    kribi_coords = [2.9397, 9.9106]

    # Créer une carte folium
    m = folium.Map(location=kribi_coords, zoom_start=13)

    # Charger une image satellite depuis GEE
    image = ee.Image('COPERNICUS/S2')

    # Charger les tuiles à partir de l'image dans GEE
    map_id_dict = image.getMapId({'min': 0, 'max': 3000, 'bands': ['B4', 'B3', 'B2']})
    folium.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        overlay=True,
        name='Satellite',
    ).add_to(m)

    # Affichage de la carte
    m.save('kribi_map.html')
    return render(request, 'authentification/test.html')