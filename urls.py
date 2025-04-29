
from django.urls import path, include

urlpatterns = [
    path('api/', include('ReshiKaserver.urls')),  # Добавьте маршрут для вашего API
]
