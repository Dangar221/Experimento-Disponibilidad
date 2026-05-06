from django.urls import path
from . import views

urlpatterns = [
    path('consumos/', views.ConsumosView.as_view(), name='consumos'),
    path('health/', views.health_check, name='health'),
]

