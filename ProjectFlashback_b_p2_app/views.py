from turtle import st
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Story, StoryStage, GlobalModel
from .serializers import packIt
from .testFunctions import delayResponse, cookieHandler, fetchChatGptJson_test, fetchDallEImg_test
import os, time
from django.utils import timezone


#requests limit to limit requests for the user, and all users, respectively
userRequestLimit, globalRequestLimit = 3, 10
testingModeCookie = True

"""
The main view of the phase2
handles cookies
fetches stories from the DB
"""
#@permission_classes([AllowAny])
@api_view(['GET'])
@cookieHandler(testingModeCookie)
def phase2View(request, passedValue, currentUser, setCookie):
    #get story based on the batch number
    try:
        #todo: sort by most recent
        story = Story.objects.filter(complete=True)[passedValue]
        storyStages = StoryStage.objects.filter(story=story)
        returnedStages = packIt(story, storyStages)
        returnedData = Response([returnedStages])
    except Exception as e:
        print(e)
        returnedData = JsonResponse({'error': 'Story not found'}, status=404)

    
    #set cookie if there is a need
    if setCookie:
        returnedData.set_cookie('user_id', currentUser.cookie, 
                        expires=timezone.now() + timezone.timedelta(days=30),
                        secure=True, httponly=True)
    
    #return the data
    return returnedData

"""
gets images from the local dir given the stageNumber that was already passed to the frontend
in the Phase2View function, and sends it to the frontend as blobs
fetching images is separate from the phase2View since images usually take longer to load
"""
@api_view(['GET'])
#@delayResponse(timeMultiplier=2)#dectorator to delay response for testing
def fetchImgFromDB(request, storyNumber, stageNumber):
    baseImgPath = os.path.join('ProjectFlashback_b_p2_app', 'images')
    imgPath = os.path.join(baseImgPath, str(storyNumber), str(stageNumber) + ".png")

    #get the StoryStage instance
    storyStage = StoryStage.objects.get(story__storyId=storyNumber, stageNumber=stageNumber)
    
    if not storyStage.imgExists:
        newImgPath = fetchDallEImg_test(storyStage.imgPrompt, baseImgPath, storyNumber, storyStage)
        imgData = open(newImgPath, "rb").read()
    elif not os.path.exists(imgPath):
        return HttpResponse("Image not found", status=404)
    else:
        imgData = open(imgPath, "rb").read()
    
    return HttpResponse(imgData, content_type="image/png")

"""
called on by the form from the frontend to process a user's input (story prompt)
it makes a request to the ChatGPT and Dall-e API
save the results of the data/images from the API in the db
"""
from .models import CookieUser
@api_view(['GET'])
@cookieHandler(testingModeCookie)
def promptView(request, passedValue, currentUser, setCookie):
    #get the global data of today (used to limit daily requests for all users)    
    #if there is no model for today, create one
    todayDate = timezone.now().date()
    globalModel, created = GlobalModel.objects.get_or_create(date=todayDate)
    
    #check if the user can still make request and did not exceed the limit
    if currentUser.requestCount >= userRequestLimit or globalModel.requestCount >= 10:
        response = JsonResponse({'error': "Can't make more requests"}, status=404)
    else:
        print("made a request", passedValue)
        #todo: if there is a similar item in the db, refuse the request
        #Step 1: invoke the ChatGPT api and fetch data describing the story in 5 stages.
        #it will return dict that contains all 5 stages.
        newStory = fetchChatGptJson_test(passedValue, currentUser)
        storyStages = StoryStage.objects.filter(story=newStory)
        returnedStages = packIt(newStory, storyStages)
        response = Response([returnedStages])

        #todo: inc user/global request

    #set cookie if there is a need
    if setCookie:
        response.set_cookie('user_id', currentUser.cookie, 
                        expires=timezone.now() + timezone.timedelta(days=30),
                        secure=True, httponly=True)


    return response

"""
Step 1: chatgpt data
takes the story as requested by the frontend/user
saves it in the DB, returns the saved model
"""
def fetchChatGptJson(prompt):
    pass

"""
Step 2: Dall-E images
Get images from Dall-E images based on the 
returns an img url for the generated image that as of
23/01/2024 expires in 4 hours
"""
#todo: error handling: https://platform.openai.com/docs/guides/images/error-handling
def fetchDallEImg(prompt):
    pass


def sseEndpoint(request):
    def eventStream():
        for i, stageData in enumerate(genTestData()):
            time.sleep(1)
            yield f'data: {stageData}\n\n'
        
    return StreamingHttpResponse(eventStream(), content_type='text/event-stream')

def genTestData():
    x = [1,2,3,4,5]
    for i in x:
        time.sleep(1)
        yield i