from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('code/', views.code, name='code'),
    path('logout/', views.user_logout, name='logout'),
    path('index/', views.index, name='index'),
    path('profil/', views.profil, name='profil'),
    path('edit_profil/', views.edit_profil, name='edit'),
    path('test/', views.test, name='test'),
    path('json/', views.jsonview, name='jsonview'),
]