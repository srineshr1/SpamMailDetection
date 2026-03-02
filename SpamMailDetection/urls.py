from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .views import predict


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health),                        # Health check — Render pings this
    path('api/predict/', predict, name='predict'),
]
