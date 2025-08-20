from django.urls import path
from . import views

urlpatterns = [
    # Diagram CRUD operations
    path('diagrams/create/', views.create_new_diagram, name='create_diagram'),
    path('diagrams/save/', views.save_diagram, name='save_diagram'),
    path('diagrams/load/', views.load_diagram, name='list_diagrams'),
    path('diagrams/load/<int:diagram_id>/', views.load_diagram, name='load_diagram'),
    path('diagrams/history/<int:diagram_id>/', views.diagram_history, name='diagram_history'),
    path('diagrams/delete/<int:diagram_id>/', views.delete_diagram, name='delete_diagram'),
    
    # Export functionality
    path('diagrams/export/<int:diagram_id>/<str:format_type>/', views.export_diagram, name='export_diagram'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
