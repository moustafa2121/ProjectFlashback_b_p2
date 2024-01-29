from django.contrib import admin
from .models import CookieUser, Story, StoryStage, GlobalModel, RequestTracker

admin.site.register(CookieUser)
admin.site.register(Story)
admin.site.register(StoryStage)
admin.site.register(GlobalModel)
admin.site.register(RequestTracker)
