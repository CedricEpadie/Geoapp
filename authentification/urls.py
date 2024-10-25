from django.urls import path
from authentification import views

app_name = 'authentification'

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('code/', views.code, name='code'),
    path('logout/', views.user_logout, name='logout'),
]