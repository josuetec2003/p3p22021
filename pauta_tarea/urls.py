"""pauta_tarea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app_banco import views
from app_seguridad import views as views_sec

urlpatterns = [
    path('', views_sec.index, name='index_view'),
    path('login/', views_sec.log_in, name="login_view"),
    path('logout/', views_sec.log_out, name="logout_view"),

    path('home/', views.home, name='home_view'),
    path('historial/', views.historial, name='historial_view'),

    path('transferencias/', views.transferencias_view, name="transferencias_view"),
    path('clientes/', views.clientes_view, name="clientes_view"),

    path('clientes/gestion/', views.clientes_gestion, name="clientes_gestion"),
    path('clientes/actualizar/<int:id>/', views.clientes_gestion, name="clientes_actualizar"),
    

    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
