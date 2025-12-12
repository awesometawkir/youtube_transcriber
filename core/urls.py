
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transcribe/', views.transcribe, name='transcribe'),
    path('status/<uuid:job_id>/', views.check_status, name='check_status'),
]
