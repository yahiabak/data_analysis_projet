from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('statistics/', views.statistical_analysis, name='statistical_analysis'),
    path('visualization/', views.visualization, name='visualization'),
    path('data-preview/', views.data_preview, name='data_preview'),
    path('access/', views.access_row_column, name='access_row_column'),
]
