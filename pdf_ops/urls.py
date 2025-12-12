
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='pdf_index'),
    path('split/', views.split_view, name='pdf_split'),
    path('extract/', views.extract_view, name='pdf_extract'),
    path('unlock/', views.unlock_view, name='pdf_unlock'),
    path('delete-text/<int:text_id>/', views.delete_text_view, name='pdf_delete_text'),
]
