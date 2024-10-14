from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from  authentification import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
