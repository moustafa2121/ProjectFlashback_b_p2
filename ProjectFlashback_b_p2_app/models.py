from django.db import models


#identified by a cookie. its main purpose is to keep track what the user has prompted so far
#to limit the number of requests
class CookieUser(models.Model):
    cookie = models.CharField(primary_key=True, max_length=200)
    requestCount = models.IntegerField(default=0)

class Story(models.Model):
    storyId = models.AutoField(primary_key=True)
    storyTitle = models.CharField(max_length=100)
    storyPrompt = models.CharField(max_length=200)
    generatedOn = models.DateTimeField(null=True, blank=True)
    userCreator = models.ForeignKey(CookieUser, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    
    def __str__(self) -> str:
        return self.storyTitle
    

class StoryStage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    stageNumber = models.IntegerField()
    stageTitle = models.CharField(max_length=100)
    stageStory = models.CharField(max_length=5000)
    illustrationStyle = models.CharField(max_length=100)
    imgPrompt = models.CharField(max_length=1000)
    
    def __str__(self) -> str:
        return self.stageTitle
    