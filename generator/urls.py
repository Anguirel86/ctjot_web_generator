from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.index, name='index'),
    path('tracker/', views.tracker, name='tracker'),
    path('options/', views.options, name='options'),
    path('generate-rom/', views.generate, name='generate'),
    path('share/<str:share_id>/', views.share, name='share'),
    path('seed/', views.download_seed, name='seed'),
    path('spoiler_log/<str:share_id>/', views.download_spoiler_log, name='spoiler_log'),
]
