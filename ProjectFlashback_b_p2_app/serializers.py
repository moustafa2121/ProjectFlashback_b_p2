from rest_framework import serializers
from .models import Story, StoryStage



class Story_ser(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = ('storyTitle', 'generatedOn', 'userCreator', 'complete')
        
class StoryStage_ser(serializers.ModelSerializer):
    class Meta:
        model = StoryStage
        exclude = ('story',)


def packIt(story, storyStages):
    returnedStory = Story_ser(story).data
    returnedStages = StoryStage_ser(storyStages, many=True).data
    returnedStages.append(returnedStory)
    return returnedStages