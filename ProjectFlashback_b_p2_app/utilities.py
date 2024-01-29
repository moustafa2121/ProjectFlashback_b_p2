#provides decorators and test functions for the views

from .models import CookieUser, Story, StoryStage, RequestTracker, GlobalModel
from PIL import Image
import requests, shutil, json, time, uuid, os
from django.utils import timezone
from datetime import timedelta, datetime

"""
test function for fetching data from chatGPT api
"""
def fetchChatGptJson_test(prompt, currentUser):
    with open("caesar.json", 'r') as file:
        data = json.load(file)
    
    #delete the story to simulate adding it as if a new one
    newStory = Story.objects.get(storyTitle="new title")
    newStory.delete()
    
    #save the story to the DB
    newStory = Story(storyTitle="new title", storyPrompt=prompt,
                        generatedOn=timezone.now(), userCreator=currentUser,
                        complete=False)
    newStory.save()
    
    #save the story stages to the DB
    for i, key in enumerate(data.keys()):
        storyStage = StoryStage(story=newStory, 
                                stageNumber=i+1,
                                stageTitle=data[key]["STORY TITLE"],
                                stageStory=data[key]["STORY"],
                                illustrationStyle=data[key]["Illustration style"],
                                imgPrompt=data[key]["PROMPT"],
                                imgExists=False,
                                )
        storyStage.save()
    
    #return the new story instance
    return newStory

"""
test function for fetching images from Dall-e api
"""
#@delayResponse(timeMultiplier=2)#dectorator to delay response for testing
def fetchDallEImg_test(prompt, baseImgPath, storyNumber, storyStage):
    #five random images from the internet
    donkeyLst =['https://upload.wikimedia.org/wikipedia/commons/1/1a/Donkey_in_Clovelly%2C_North_Devon%2C_England.jpg',
                'https://i0.wp.com/barronparkdonkeys.org/wp-content/uploads/2021/08/IMG_0194.jpg?ssl=1',
                'https://images.squarespace-cdn.com/content/v1/62da63f9ec4d5d07d12a1056/e74680d7-fa63-4668-bce7-6730dce45ed9/Donkeys+with+CF.jpg',
                'https://www.boredpanda.com/blog/wp-content/uploads/2018/03/cute-miniature-baby-donkeys-22-5aaa4a99d5eae__605.jpg',
                'https://cottagesatblackadonfarm.co.uk/wp-content/uploads/Blackadon-March-043-2.jpg']
    
    #mkdir if it doesn't exist for the given story
    dirPath = os.path.join(baseImgPath, str(storyNumber))
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
    
    #get the image by prompting dall-e api
    imgLink = donkeyLst[storyStage.stageNumber-1]
    
    #save the image
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
            #mark the user 
            
        
        #resize the image to have a managable size
        resizeImg(imgPath, imgPath)
    else:
        print('Image Couldn\'t be retrieved')
    
    #return the path of the image in the backend
    return os.path.join(dirPath, str(storyStage.stageNumber)+".png")


def resizeImg(imgPath, imgOutput, newSize=(750,750)):
    try:
        with Image.open(imgPath) as img:
            resizedImg = img.resize(newSize)
            resizedImg.save(imgOutput)
    except Exception as e:
        print(f"Error resizing image: {e}")
        

"""
decorator that delays view functions
simulates getting data from the API to test frontend functionality
"""
def delayResponse(timeMultiplier):
    def decorator(viewFunc):
        def wrapper(request, *args, **kwargs):
            delayTime = timeMultiplier * int(kwargs.get('stageNumber', 0))
            time.sleep(delayTime)
            response = viewFunc(request, *args, **kwargs)

            return response
        return wrapper
    return decorator


#decorator that handle cookies/user wrapper for the views
#note that this is necessary for some Views to work properly
# (even though there should be a seperation of concerns)
#testingModeCookie: boolean argument if true it will use default CookieUser for testing
def cookieHandler(testingModeCookie):
    def decorator(viewFunc):
        def wrapper(request, passedValue, **kwargs):
            setCookie = False
    
            if testingModeCookie:#ignores the cookies sent from the frontend
                currentUser = CookieUser.objects.get(cookie="e3d3abf1-a05a-4a97-a17e-a9c36e5a0265")
            elif request.COOKIES.get('user_id'):#if the front has a cookie, get the user or create it
                currentUser = CookieUser.objects.get_or_create(cookie=request.COOKIES.get('user_id'))[0]
            else:#if the front doesn't have a cookie, get a cookie and create a user
                currentUser = CookieUser.objects.create(cookie=str(uuid.uuid4()))
                setCookie = True

            #call the view
            response = viewFunc(request, passedValue, currentUser=currentUser, **kwargs)

            #set cookie if there is a need and attach it to the response
            if setCookie:
                response.set_cookie('user_id', currentUser.cookie, 
                        expires=timezone.now() + timezone.timedelta(days=30),
                        secure=True, httponly=True)
                
            return response
        return wrapper
    return decorator


"""
a function that used by a prompting view if a user can make a prompt
it checks for:
1- if the user exceeded their limit of daily prompting
2- if the global request limit is exeeded
3- if the user currently has a story that is not complete (i.e. still fetching data from AI)
if any of these conditions are true, the promping will be refused

it returns three values
1- if the user canPrompt
2- if 1 is True, specify the reason for the request limit
3- if 1 is True, specify time to check again
"""
def canUserPrompt(currentUser, userRequestLimit, globalRequestLimit):
    #if request limit has reached
    limitReached = False
    #default reason
    reason = 'on-going story'
    #default check again time (estimated time for a story to complete)
    #in seconds
    checkAgainTime = 120
    
    #condition 3, check if latest story is complete
    completedStory = False
    userStory = Story.objects.filter(userCreator=currentUser).order_by('-generatedOn')
    if userStory:
        if userStory[0].complete:
            completedStory = True
            
    #condition 1, check user request limit
    limitReached1, remainingTime1 = requestCountReached(currentUser, userRequestLimit)
    #condition 2, check the global limit
    limitReached2, remainingTime2 = requestCountReached(GlobalModel.objects.all()[0], globalRequestLimit)
    
    #if the user or global request limit has reached, then specify checkAgainTime
    if limitReached1 or limitReached2:
        reason = 'request limit'
        limitReached = True
        checkAgainTime = remainingTime1 if remainingTime1 > remainingTime2 else remainingTime2

    return (not limitReached and completedStory), reason, checkAgainTime

#check if an instance of type Requester has reached its given request limit
#by checking its most recent RequestTracker's request count
#if 24 hours has passed for the said RequestTracker, assign a new one
def requestCountReached(requester, requestLimit):
    currentTracker = RequestTracker.objects.filter(requester=requester).order_by('-firstRequestTime')
    #user is new and didn't make any request yet, assign it a new RequestTracker
    #or the latest RequestTracker has spanned 24 hours so assign a new 
    #tracker (i.e. can make more request for the next 24 hours)
    if not currentTracker or timePassed(currentTracker[0], 24):
        currentTracker = RequestTracker(requestCount=0,
                                        firstRequestTime=timezone.now(),
                                        requester=requester)
        currentTracker.save()
    elif currentTracker[0].requestCount >= requestLimit:
        #request limit reached
        return True, remainingTime(currentTracker[0].firstRequestTime)
    return False, 0
    

#increments both the current user and the global request counts
def incRequestCount(currentUser):
    incRequestCount_aux(GlobalModel.objects.all()[0])
    incRequestCount_aux(currentUser)
#hepler for the above function
def incRequestCount_aux(requester):
    currentTracker = RequestTracker.objects.filter(requester=requester).order_by('-firstRequestTime')
    if currentTracker:
        currentTracker[0].requestCount += 1
        currentTracker[0].save()
    else:
        #this assumes that the requester has no RequestTracker which is not 
        #not possible because it should've been set by canUserPrompt function
        pass

#checks if a requestTracker's first request has passed more than the given hours
def timePassed(requestTracker, hours=24):
    if requestTracker:
        timeDiff = timezone.now() - requestTracker.firstRequestTime
        return timeDiff.total_seconds() > hours * 3600
    return False


#given a time, it will calculate how many hours left for 24 
#hours to span from the given time, used to calculate time when a user
#can prompt again (so the front does not show the prompty submit 
#until that time has passed, thus limiting prompty requests)
def remainingTime(startTime):
    endTime = startTime + timedelta(hours=24)
    timeDiff = endTime - timezone.now()
    return timeDiff.total_seconds()
    

