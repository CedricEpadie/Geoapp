from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser
from .utils import generate_verif_code, send_email_with_html_body

def acceuil(request):
    return render(request, 'authentification/acceuil.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profession = request.POST.get('profession')
        
        print(profession)
        
        code = generate_verif_code()
        subjet = 'Code de confirmation'
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
            return redirect('igogek:index')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            
    return render(request, 'authentification/login.html')

def user_logout(request):
    logout(request)
    return redirect('authentification:login')