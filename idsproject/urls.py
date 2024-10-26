from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from  authentification import views

urlpatterns = [
    path('', views.acceuil, name='acceuil'),
    path('admin/', admin.site.urls),
    path('authentification/', include('authentification.urls')),
    path('igogek/', include('igogek.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()