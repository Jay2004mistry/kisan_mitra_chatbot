from fastapi import FastAPI
#basemodel for request body validation means the message sent by the user will be validated using this model
from pydantic import BaseModel
import joblib
import json
from weather import get_weather_reply
import random
from fastapi.middleware.cors import CORSMiddleware

#app
app = FastAPI(title="Kisan Mitra Chatbot API")

# CORS section
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load model and normalizer
model      = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

#load intents.json which contains the predefined responses for different intents
#we are using encoding utf-8 because it allow us to read special character with diffrent language.
with open("intents.json", encoding='utf-8') as f:
    data = json.load(f)




# message sent by user
#it is user input structure and it will be validated using this model
class Message(BaseModel):
    message: str

# helper function to get response from intents.json based on predicted tag
#check all tags in the intents.json file and return a random response from the corresponding tag
def get_response(tag):
    for intent in data["intents"]:
        #match the predicted tag with the tag in the intents.json file a
        if intent["tag"] == tag:
            #return a random response from the that tag
            return random.choice(intent["responses"]) 
    return "I'm not sure how to respond to that. Could you please rephrase your question about farming?"


# post method to receive user message, predict intent and return response
@app.post("/chat")
#take message as input request
#this message is class which represent the structure of user input and validate using pydantic
def chat(request: Message):

    #convert user message to number using the loaded vectorizer
    user_vector = vectorizer.transform([request.message.lower()])

    #predict the intent tag (label) using the loaded model
    #predict the tag based on the user input and the patterns in the intent.json file
    tag = model.predict(user_vector)[0]

    # if intent is weather, call the weather function to get weather data and advice 
    # otherwise get response from intents.json
    if tag == "weather":
        reply = get_weather_reply(request.message)
    else:
        reply = get_response(tag)

# return the predicted tag and the corresponding reply to the user
    return {
        "intent" : tag,
        "reply"  : reply
    }

#run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)