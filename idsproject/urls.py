from django.contrib import admin
from django.urls import path, include

from  authentification import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
]
