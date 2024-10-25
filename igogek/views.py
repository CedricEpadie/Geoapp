from django.shortcuts import render, redirect, get_object_or_404
from authentification.models import CustomUser
from django.contrib.auth.decorators import login_required


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
        return redirect('igogek:edit')
        
    return render(request, 'igogek/edit.html')

@login_required
def index(request):
    return render(
        request,
        'igogek/index.html',
        {
            'api_key': 'pk.eyJ1IjoiY2VkcmljZXBhZGllIiwiYSI6ImNtMXE3aTRsNDBibTAycG9qajR5YjFjdm4ifQ.uMkRry3szVbv-cKeqJDBtg'
        }
    )
@login_required
def profil(request):
    return render(request, 'igogek/profil.html')