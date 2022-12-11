from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'generator'

urlpatterns = [
    path('', TemplateView.as_view(template_name="generator/index.html"), name='index'),
    path('tracker/', TemplateView.as_view(template_name="generator/tracker.html"), name='tracker'),
    path('options/', views.OptionsView.as_view(), name='options'),
    path('generate-rom/', views.GenerateView.as_view(), name='generate'),
    path('share/<str:share_id>/', views.ShareLinkView.as_view(), name='share'),
    path('practice/<str:share_id>/', views.PracticeSeedView.as_view(), name='practice'),
    path('seed/', views.DownloadSeedView.as_view(), name='seed'),
    path('spoiler_log/<str:share_id>.txt', views.DownloadSpoilerLogView.as_view(), name='spoiler_log'),
    path('spoiler_log/<str:share_id>.json', views.DownloadJSONSpoilerLogView.as_view(), name='json_spoiler_log'),
]
