from rest_framework import serializers
from .models import Story, StoryStage



class Story_ser(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = ('storyTitle', 'generatedOn', 'userCreator')
        
class StoryStage_ser(serializers.ModelSerializer):
    class Meta:
        model = StoryStage
        exclude = ('story',)


