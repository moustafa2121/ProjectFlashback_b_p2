from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Story, StoryStage, CookieUser, GlobalModel
from .serializers import Story_ser, StoryStage_ser
from .testFunctions import testData, delayResponse
import os, time, uuid
from django.utils import timezone

"""
The main view of the phase2
handles cookies
fetches data from the DB (i.e. other user's inputs)
prompts the API for more data/images
save the results of the data/images from the API in the db
"""
@api_view(['GET'])
def phase2View(request, batch):
    #requests limit to limit requests for the user, and all users, respectively
    userRequestLimit, globalRequestLimit = 3, 10
    
    #get the global data of today (used to limit daily requests for all users)    
    #if there is no model for today, create one
    todayDate = timezone.now().date()
    globalModel, created = GlobalModel.objects.get_or_create(date=todayDate)

    #handle cookies/user
    testingModeCookie = True#ignores the cookies sent from the frontend
    setCookie = False
    currentUser = None
    if testingModeCookie:
        currentUser = CookieUser.objects.get(cookie="e3d3abf1-a05a-4a97-a17e-a9c36e5a0265")
    elif request.COOKIES.get('user_id'):#if the front has a cookie, get the user or create it
        currentUser = CookieUser.objects.get_or_create(cookie=request.COOKIES.get('user_id'))[0]
    else:#if the front doesn't have a cookie, get a cookie and create a user
        currentUser = CookieUser.objects.create(cookie=str(uuid.uuid4()))
        setCookie = True
    
    
    #get story based on the batch number
    try:
        #todo: sort by most recent
        story = Story.objects.filter(complete=True)[batch]
        storyStages = StoryStage.objects.filter(story=story)
        
        returnedStory = Story_ser(story).data
        returnedStages = StoryStage_ser(storyStages, many=True).data
        returnedStages.append(returnedStory)
        returnedData = Response([returnedStages])
    except Exception as e:
        print(e)
        returnedData = Response("Unfound")
    

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
@delayResponse(timeMultiplier=2)#dectorator to delay response for testing
def fetchImgFromDB(request, storyNumber, stageNumber):
    baseImages = os.path.join('ProjectFlashback_b_p2_app', 'images')
    imgPath = os.path.join(baseImages, str(storyNumber), str(stageNumber) + ".png")

    if not os.path.exists(imgPath):
        return HttpResponse("Image not found", status=404)

    image_data = open(imgPath, "rb").read()
    return HttpResponse(image_data, content_type="image/png")

"""
handles passing user's prompts and fetching data from the API
It will take the user input (story subject) and it will return
a description of it in 5 stages an image for each stage
"""
@api_view(['GET'])
def fetchingData(response):
    #get user's input

    #todo: if there is a similar item in the db, refuse the request

    #Step 1: invoke the ChatGPT api and fetch data describing the story in 5 stages.
    #it will return dict that contains all 5 stages.
    response = Response(fetchChatGptJson("story"))
    
    #Step 2: invoke the DAll-E api to fetch an image for each stage 
    #using the PROMPT from the chatGPT returned data, 
    #this will be invoked 5 times


"""
Step 1: chatgpt data
takes the story as requested by the frontend/user
returns a dict of the following format
dict['Stage 1']{
    'STORY TITLE':'the title of the stage',
    'STORY':'the description of the stage',
    'Illustration style':'style of the iamge',
    'PROMPT':'prompt describing the imagfe',
}
"""
def fetchChatGptJson(story):
    
    return testData()

"""
Step 2: Dall-E images
Get images from Dall-E images based on the 
returns an img url for the generated image that as of
23/01/2024 expires in 4 hours
"""
#todo: error handling: https://platform.openai.com/docs/guides/images/error-handling
def fetchDallEImg(prompt):
    
    return ''


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