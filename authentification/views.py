from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser

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

        if not all([first_name, last_name, email, username, password, profession]):
            return render(request, 'authentification/register.html', {'error': 'Tous les champs sont obligatoires.'})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'authentification/register.html', {'error': 'Le nom d’utilisateur est déjà pris.'})
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'authentification/register.html', {'error': 'L’adresse email est déjà utilisée.'})

        CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            profession=profession
        )
        return redirect('authentification:login')

    return render(request, 'authentification/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = user.username
            return redirect('igogek:index')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            
    return render(request, 'authentification/login.html')

def user_logout(request):
    logout(request)
    return redirect('authentification:login')