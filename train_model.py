#train the model

import json
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer


#step 1
#load the intents file for training the model
#intents file contains the patterns and responses for the chatbot
with open('intents.json') as f:
    data = json.load(f)


#step 2
#now we extract the patterns and responses from the intents file and prepare the training data
labels = []#y intent labels for training the model, output like greeting, goodbye, etc
sentences = []#x patterns for training the model, user input like hii, hello, how are you etc

for intent in data['intents']:
    for pattern in intent['patterns']:

#we are saving the patterns and their corresponding tags in the labels list, 
# and the patterns in the sentences list for training the model
#we are not writing the responses in the training data because we will use them later 
# for generating responses based on the predicted intent

        labels.append((pattern, intent['tag']))
        sentences.append(pattern.lower()) #convert the patterns to lowercase for better processing



print(f"Total patterns: {len(sentences)}")
print(f"labels: {len(labels)}")
print(f"total labels: {len(set(labels))}")



#step 3
#we split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(sentences, labels, test_size=0.2, random_state=42)
print(f"Training patterns: {len(x_train)}")
print(f"Testing patterns: {len(x_test)}")



#step 4 Build the pipeline for training the model
#tf-idf vectorizer to convert the text data into numerical features