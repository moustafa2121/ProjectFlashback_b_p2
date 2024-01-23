from . import views
from django.urls import path, include

app_name = "ProjectFlashback_b_p2_app"
urlpatterns = [
    path('', views.phase2View, name='phase2View'),
]