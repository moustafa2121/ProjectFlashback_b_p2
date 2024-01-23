from django.contrib import admin
from .models import CookieUser, Story, StoryStage

admin.site.register(CookieUser)
admin.site.register(Story)
admin.site.register(StoryStage)
