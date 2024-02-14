#provides decorators and utilities for the views

from .models import CookieUser, Story, StoryStage, RequestTracker, GlobalModel
from PIL import Image
import uuid, os, json
from django.utils import timezone
from datetime import timedelta

#given data fetched from ChatGPT, save it to the DB models,
#it returns an instance of Story
#also creates new directory for the images for this story
def saveStoryFromData(data, prompt, currentUser, baseImgPath, testingChatGpt):
    storyTitle = "test title" if testingChatGpt else "new title"
    #save the story to the DB
    newStory = Story(storyTitle=storyTitle, 
                        storyPrompt=prompt,
                        generatedOn=timezone.now(), 
                        userCreator=currentUser,
                        complete=False)
    newStory.save()
    
    # saves data to .json to validate the format
    # json_object = json.dumps(data, indent=4)
    # with open("test2.json", "w") as outfile:
    #     outfile.write(json_object)
        
    #save the story stages to the DB
    for i, key in enumerate(data.keys()):
        print("i=", key)
        storyStage = StoryStage(story=newStory, 
                                stageNumber=i+1,
                                stageTitle=data[key]["STORY TITLE"],
                                stageStory=data[key]["STORY"],
                                illustrationStyle=data[key]["Illustration style"],
                                imgPrompt=data[key]["PROMPT"],
                                imgExists=False,
                                )
        storyStage.save()
    
    #mkdir if it doesn't exist for the given story
    dirPath = os.path.join(baseImgPath, str(newStory.pk))
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
        
    #return the new story instance
    return newStory

#resizes the given image
def resizeImg(imgPath, imgOutput, newSize=(750,750)):
    try:
        with Image.open(imgPath) as img:
            resizedImg = img.resize(newSize)
            resizedImg.save(imgOutput)
    except Exception as e:
        print(f"Error resizing image: {e}")
        

#decorator that handle cookies
#note that this is necessary for some Views to work properly
#(even though there should be a seperation of concerns)
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
if any of these conditions are true, the prompting will be refused

it returns three values
1- boolean: if the user canPrompt
2- string: if 1 is True, specify the reason for the request limit
3- int: if 1 is True, specify time (in seconds) to check again
"""
def canUserPrompt(currentUser, userRequestLimit, globalRequestLimit):
    #if request limit has reached
    limitReached = False
    #default reason
    reason = 'on-going story'
    #default check again time (estimated time for a story to complete)
    checkAgainTime = 120
    
    #condition 3, check if latest story is complete
    completedStory = True
    userStory = Story.objects.filter(userCreator=currentUser).order_by('-generatedOn')
    if userStory:#if there are stories
        if not userStory[0].complete:#if the lastest story is incomplete
            #if the incomplete story hasn't finished 5 minutes after initiated, then delete it
            if timePassed_aux(userStory[0].generatedOn, 180):
                print("delete")
                #userStory[0].delete()
            else:#else the story is processing
                completedStory = False
    
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
    if not currentTracker or timePassed(currentTracker[0], 24*3600):
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

#checks if a requestTracker's first request has passed more than the
# given time
def timePassed(requestTracker, timePassed=24*3600):
    if requestTracker:
        return timePassed_aux(requestTracker.firstRequestTime, timePassed)
    return False

def timePassed_aux(givenTime, timePassed):
    timeDiff = timezone.now() - givenTime
    return timeDiff.total_seconds() > timePassed

#given a time, it will calculate how many hours left for 24 
#hours to span from the given time, used to calculate time when a user
#can prompt again (so the front does not show the prompt submit 
#until that time has passed, thus limiting prompt requests)
def remainingTime(startTime):
    endTime = startTime + timedelta(hours=24)
    timeDiff = endTime - timezone.now()
    return timeDiff.total_seconds()
    

