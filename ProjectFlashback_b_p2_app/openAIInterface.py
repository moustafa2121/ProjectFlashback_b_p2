#handles sending and getting data from the OpenAI API's

from openai import OpenAI
import json

client = OpenAI()

#prompts chatGPT
def chatGPT_inter(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
    {"role": "system", "content": "You are a witness to events throughout history. You will describe the required scenes and provide Dall-e 3 prompt that are within the context of the story"},
    {"role": "user", "content": """WHAT TO DO: Then I would like you to come up with a history text and the create associated illustrations for that story to tell a more complete picture, with each Dall-e 3 prompt being the continuation of the story.

    STORY: Can you please create a short story about:""" + prompt + """. Please make it interesting.

    KEY PARAMETERS: Please come up with the following:

    Five stages of the meeting from the start till the end. Make sure you keep the descriptions and styles consistent and never mix them.
    each stage MUST have the following:

    STORY: storyline of each of the 5 stages

    PROMPTS: Illustration style. You must make sure that EVERY PROMPT has the following information.

    Each prompt should be independently self contained and has all the information needed (do NOT rely on neighbouring prompts for info). For example, if a character is a fluffy white dog, you must mention that they are a fluffy white dog, otherwise the image will be wrong.
    the final results must be in JSON format where each stage is a key and its value is 3 following items 'STORY TITLE', 'STORY', 'Illustration style', 'PROMPT'"""},
    ])
    
    responseContent = response.choices[0].message.content
    return json.loads(responseContent)
    
    
#prompts Dall-E
def dallE_inter(prompt, model="dall-e-3"):
    return client.images.generate(
      model=model,
      prompt=prompt,
      size="1024x1024",
      quality="standard",
      n=1,
    ).data[0].url




























