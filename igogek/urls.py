from django.urls import path
from igogek import views

app_name = 'igogek'

urlpatterns = [
    path('', views.index, name='login'),
    path('index/', views.index, name='index'),
    path('profil/', views.profil, name='profil'),
    path('edit_profil/', views.edit_profil, name='edit'),
]