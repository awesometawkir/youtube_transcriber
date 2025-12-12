
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='summarizer_index'),
    path('api/summarize/', views.summarize_view, name='api_summarize'),
    path('api/snippet/create/', views.create_snippet, name='api_create_snippet'),
    path('api/delete/<str:type_>/<int:id_>/', views.delete_context, name='api_delete_context'),
]
