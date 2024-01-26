#provides decorators and test functions for the views

from .models import CookieUser, Story, StoryStage
from PIL import Image
import requests, shutil, json, time, uuid, os
from django.utils import timezone

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
        if len(os.listdir(dirPath)) == 5:
            story = Story.objects.get(pk=storyNumber)
            story.complete = True
            story.save()
        
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


#handle cookies/user wrapper for the views
def cookieHandler(testingModeCookie):
    def decorator(viewFunc):
        def wrapper(request, passedValue, *args, **kwargs):
            setCookie = False

            if testingModeCookie:#ignores the cookies sent from the frontend
                currentUser = CookieUser.objects.get(cookie="e3d3abf1-a05a-4a97-a17e-a9c36e5a0265")
            elif request.COOKIES.get('user_id'):#if the front has a cookie, get the user or create it
                currentUser = CookieUser.objects.get_or_create(cookie=request.COOKIES.get('user_id'))[0]
            else:#if the front doesn't have a cookie, get a cookie and create a user
                currentUser = CookieUser.objects.create(cookie=str(uuid.uuid4()))
                setCookie = True

            #call the view
            response = viewFunc(request, passedValue, currentUser, setCookie, *args, **kwargs)

            return response
        return wrapper
    return decorator

