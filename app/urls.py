from django.urls import path
from app import views

urlpatterns = [
    path('incoming-call/', views.incoming),
    path('outgoing-call/', views.outgoing)
]
