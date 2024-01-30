from django.db import models

#a model that tracks how many requests a Requester has made
#also helps historical data (later features)
class RequestTracker(models.Model):
    requestCount = models.IntegerField(default=0)
    #track when the request count will reset
    firstRequestTime = models.DateTimeField(null=True, blank=True)
    requester = models.ForeignKey("Requester", on_delete=models.CASCADE)

#an empty model for RequestTracker to refer to
#not gonna make it abstract because it messes with serializer for some reason
class Requester(models.Model):
    pass

#a model to keep track of daily limits for API prompts for all users
class GlobalModel(Requester):
    pass

#identified by a cookie. its main purpose is to keep track what the 
#user has prompted so far to limit the number of requests
class CookieUser(Requester):
    cookie = models.CharField(primary_key=True, max_length=200)

#story model. holds the story prompt and is refered to by related
#StoryStage instances
class Story(models.Model):
    storyId = models.AutoField(primary_key=True)
    storyTitle = models.CharField(max_length=100)
    storyPrompt = models.CharField(max_length=200)
    generatedOn = models.DateTimeField(null=True, blank=True)
    userCreator = models.ForeignKey(CookieUser, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    #a story is complete=True when all its images have 
    #been prompted and saved in the backend
    #only then it will be serviced to other users
    complete = models.BooleanField()
    
    def __str__(self) -> str:
        return self.storyTitle
    
#a stage is different part of the story, total of 5 stage
#each stage has a title, a text, and img it describes
class StoryStage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    stageNumber = models.IntegerField()
    stageTitle = models.CharField(max_length=100)
    stageStory = models.CharField(max_length=5000)
    illustrationStyle = models.CharField(max_length=100)
    imgPrompt = models.CharField(max_length=1000)
    #imgExists is True when the img have beem prompted and saved in the backend
    imgExists = models.BooleanField()    

    def __str__(self) -> str:
        return self.stageTitle
    
    