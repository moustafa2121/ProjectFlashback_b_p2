from . import views
from django.urls import path

app_name = "ProjectFlashback_b_p2_app"
urlpatterns = [
    path('<int:passedValue>', views.phase2View, name='phase2View'),
    path('getImage/<int:storyNumber>/<int:stageNumber>', views.fetchImgFromDB, name='fetchImgFromDB'),
    path('makeRequest/<str:passedValue>', views.promptView, name='promptView'),
]