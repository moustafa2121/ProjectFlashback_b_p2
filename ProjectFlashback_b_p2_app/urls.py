from . import views
from django.urls import path

app_name = "ProjectFlashback_b_p2_app"
urlpatterns = [
    path('<int:batch>', views.phase2View, name='phase2View'),
]