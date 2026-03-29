from fastapi import FastAPI
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
with open("intents.json") as f:
    data = json.load(f)




# message sent by user
class Message(BaseModel):
    message: str

# helper function to get response from intents.json based on predicted tag
def get_response(tag):
    for intent in data["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"]) 


# post method to receive user message, predict intent and return response
@app.post("/chat")
def chat(request: Message):

    #convert user message to number using the loaded vectorizer
    user_vector = vectorizer.transform([request.message.lower()])

    #predict the intent tag (label) using the loaded model
    tag = model.predict(user_vector)[0]

    # if intent is weather, call the weather function to get weather data and advice
    if tag == "weather":
        reply = get_weather_reply(request.message)
    else:
        reply = get_response(tag)

# return the predicted tag and the corresponding reply
    return {
        "intent" : tag,
        "reply"  : reply
    }

#run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)