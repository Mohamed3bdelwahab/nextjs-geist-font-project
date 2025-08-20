from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/diagrams/(?P<diagram_id>\w+)/$', consumers.DiagramConsumer.as_asgi()),
]
