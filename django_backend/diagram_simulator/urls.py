"""
URL configuration for diagram_simulator project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('simulator.urls')),
]
