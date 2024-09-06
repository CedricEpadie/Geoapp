from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('index/', views.index, name='index'),
    path('mainpage/', views.mainpage, name='mainpage'),
]