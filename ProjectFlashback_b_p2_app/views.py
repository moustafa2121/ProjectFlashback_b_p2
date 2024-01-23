from urllib import response
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json, os


"""
The main view of the phase2
It will take the user input (story subject) and it will return
a description of it in 5 stages an image for each stage
"""
@api_view(['GET'])
def phase2View(response):
    #Step 1: invoke the ChatGPT api and fetch data describing the story in 5 stages.
    #it will return dict that contains all 5 stages.
    response = Response(fetchChatGptJson("story"))
    
    #Step 2: invoke the DAll-E api to fetch an image for each stage 
    #using the PROMPT from the chatGPT returned data, 
    #this will be invoked 5 times
    
    #todo: cookies

    return response



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
def fetchDallEImg(prompt):
    
    return ''


def testData():
    dataFile = open('napleon_test.json', 'r')
    data = json.load(dataFile)
    dataFile.close()
    print(type(data))
    return data

def testImgStatic(num):
    image_data = open(str(num)+".png", "rb").read()
    return HttpResponse(image_data, content_type="image/png")