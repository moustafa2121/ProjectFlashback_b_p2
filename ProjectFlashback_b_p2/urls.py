
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ProjectFlashback_b_p2_app.urls')),
]
