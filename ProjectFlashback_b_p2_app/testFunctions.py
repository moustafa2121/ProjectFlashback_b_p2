#provides decorators and test functions for the views

import json, time
from .models import Story

"""
test function for fetching test data that have the same format
as a ChatGPT data
"""
def getTestData_gpt():
    with open("caesar.json", 'r') as file:
        data = json.load(file)
    
    #delete the story to simulate adding it as if a new one
    newStory = Story.objects.get(storyTitle="new title")
    newStory.delete()
    
    return data
    
"""
test function for fetching images from Dall-e api
"""
#@delayResponse(timeMultiplier=2)#dectorator to delay response for testing
def getTestData_dalle(stageNumber):
    #five random images from the internet
    donkeyLst =['https://upload.wikimedia.org/wikipedia/commons/1/1a/Donkey_in_Clovelly%2C_North_Devon%2C_England.jpg',
                'https://i0.wp.com/barronparkdonkeys.org/wp-content/uploads/2021/08/IMG_0194.jpg?ssl=1',
                'https://images.squarespace-cdn.com/content/v1/62da63f9ec4d5d07d12a1056/e74680d7-fa63-4668-bce7-6730dce45ed9/Donkeys+with+CF.jpg',
                'https://www.boredpanda.com/blog/wp-content/uploads/2018/03/cute-miniature-baby-donkeys-22-5aaa4a99d5eae__605.jpg',
                'https://cottagesatblackadonfarm.co.uk/wp-content/uploads/Blackadon-March-043-2.jpg']
    
    return donkeyLst[stageNumber-1]
    

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