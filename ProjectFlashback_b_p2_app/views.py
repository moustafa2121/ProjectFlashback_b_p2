from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Story, StoryStage
from .serializers import packIt
from .utilities import cookieHandler, canUserPrompt, incRequestCount, saveStoryFromData, resizeImg
from .testFunctions import delayResponse, getTestData_gpt, getTestData_dalle
import os, requests, shutil

#set the path of the img based on the story and the stage
baseImgPath = os.path.join('ProjectFlashback_b_p2_app', 'images')
#requests limit to limit requests for the user, and all users, respectively
userRequestLimit, globalRequestLimit = 3, 10
#set to True during testing to use defaily cookie/CookieUser
testingCookie = True
#set to true to use test data instead of prompting chatGpt API
testingChatGpt = True

"""
The main view of the phase2, returns old stories in the DB
each call is one story, also handles cookies
Note that this only returns the Story and StoryStage as a JSON,
images will be fetched individually by the frontend using fetchImgFromDB
passedValue: index of queryset of Story
"""
@api_view(['GET'])
@cookieHandler(testingCookie)
def phase2View(request, passedValue, **_):
    try:#get story based on the index number
        story = Story.objects.filter(complete=True).order_by('-generatedOn')[passedValue]
        storyStages = StoryStage.objects.filter(story=story)
        returnedStages = packIt(story, storyStages)
        returnedData = Response([returnedStages])
    except Exception as _:
        returnedData = JsonResponse({'error': 'Story not found'}, status=404)
    
    #return the data
    return returnedData

"""
gets images from the local dir given the stageNumber that was already passed to the frontend
in the Phase2View function, and sends it to the frontend as blobs
fetching images is separate from the phase2View since images usually take longer to load
This is used for fetching images of old stories (i.e. stories that have been prompted
and saved to the DB) and images that are currently being prompted by the DAll-E API
each img is fetched individually
"""
@api_view(['GET'])
#@delayResponse(timeMultiplier=2)#dectorator to delay response for testing
def fetchImgFromDB(request, storyNumber, stageNumber):
    imgPath = os.path.join(baseImgPath, str(storyNumber), str(stageNumber) + ".png")

    #get the StoryStage instance
    storyStage = StoryStage.objects.get(story__storyId=storyNumber, stageNumber=stageNumber)
    
    #if the image does not exists, it means that this is a current story and the
    #image needs to be prompted by DAll-E
    if not storyStage.imgExists:
        #prompt the image, wait for it, resize it, save it, 
        #and set the storyStage.imgExists to True and if the images of all 5
        #stages are complete it will set the story to complete as well
        newImgPath = fetchDallEImg(storyStage.imgPrompt, storyNumber, storyStage)
        imgData = open(newImgPath, "rb").read()
    elif not os.path.exists(imgPath):#img exist according to the DB but couldn't be found
        return HttpResponse("Image not found", status=404)
    else:#img exists
        imgData = open(imgPath, "rb").read()
    
    return HttpResponse(imgData, content_type="image/png")

"""
called on by the form from the frontend to process a user's input (story prompt)
it makes a request to the ChatGPT
save the results of the data/images from the API in the db
passedValue: prompt for the story
other arguments are the same as phase2View
kwargs arguments:
currentUser: the user as passed by the cookie decorator
"""
@api_view(['GET'])
@cookieHandler(testingCookie)
def promptView(request, passedValue, **kwargs):
    #check if the user can still make request
    canPrompt, reason, checkAgainTime = canUserPrompt(kwargs['currentUser'], userRequestLimit, globalRequestLimit)
    if not canPrompt:
        response = JsonResponse({'reason': reason,
                                 'checkAgainTime': checkAgainTime}, status=429)
    else:#make the request
        #todo: if there is a similar item in the db, refuse the request
        #Step 1: invoke the ChatGPT api and fetch data describing the story in 5 stages.
        #it will save the new data for Story and StoryStage in the DB
        #it will return dict that contains all 5 stages.
        newStory = fetchChatGptStory(passedValue, kwargs['currentUser'])
        storyStages = StoryStage.objects.filter(story=newStory)
        returnedStages = packIt(newStory, storyStages)
        response = Response([returnedStages])

        #inc user/global request count
        # incRequestCount(kwargs['currentUser'])

    #return data
    return response

"""
Step 1: chatgpt data
takes the story as requested by the frontend/user
saves it in the DB, returns the saved model
"""
def fetchChatGptStory(prompt, currentUser, testingChatGpt=testingChatGpt):
    if testingChatGpt:
        data = getTestData_gpt()
    else:#prompt chatGPT
        pass
    
    #save the data to a Story/StoryStage instances and return the Story instance
    return saveStoryFromData(data, prompt, currentUser, baseImgPath)

"""
Step 2: Dall-E images
Get images from Dall-E images based on the 
since the URL of the generated image expires in 4 hours as of 23/01/2024 
the images will be saved in the directory specified for that story
and it will be named based on its stageNumber.
returns the path to the saved image
"""
#todo: error handling: https://platform.openai.com/docs/guides/images/error-handling
def fetchDallEImg(prompt, storyNumber, storyStage, testingChatGpt=testingChatGpt):
    #get the image link
    if testingChatGpt:
        imgLink = getTestData_dalle(storyStage.stageNumber)
    else:#prompt Dall-E
       pass

    #save the image
    dirPath = os.path.join(baseImgPath, str(storyNumber))
    res = requests.get(imgLink, stream = True)
    if res.status_code == 200:
        #the img save path
        imgPath = os.path.join(dirPath, str(storyStage.stageNumber)+".png")
        with open(imgPath,'wb') as f:
            shutil.copyfileobj(res.raw, f)
            #set the img to exist in the db so it can be fetched
            storyStage.imgExists = True
            storyStage.save()
         
        #if all 5 stages have their images, set the story to be complete=True
        #todo: does this guarantee that the story will be marked as complete?
        #need to change this, make a global variable that tracks if all images
        #have been saved
        if len(os.listdir(dirPath)) == 5:
            #make the story complete so it can be fetched
            story = Story.objects.get(pk=storyNumber)
            story.complete = True
            story.save()
        
        #resize the image to have a managable size
        resizeImg(imgPath, imgPath)
    else:
        print('Image Couldn\'t be retrieved')
    
    #return the path of the image in the backend
    return os.path.join(dirPath, str(storyStage.stageNumber)+".png")

