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

#packs the Story and StoryStage instances using their 
#respective serializers to send to the frontend
def packIt(story, storyStages):
    returnedStory = Story_ser(story).data
    returnedStages = StoryStage_ser(storyStages, many=True).data
    returnedStages.append(returnedStory)
    print(returnedStages)
    print(type(returnedStages))
    # returnedStages.append({"userSubmit":False})
    return returnedStages