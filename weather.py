import requests
from pygetindia import cities
from functools import lru_cache

API_KEY = 'aa9e073530a9dcf797be542ec139ef34'
HEADERS = {"x-api-key": API_KEY}



#step 1: load all cities of india and cache it for future use
#--------------------------------------------------------------
@lru_cache(maxsize=1)
def load_cities():
    return set([c.lower() for c in cities()])


#step 2: load cities once and reuse it for all requests
#_-------------------------------------------------------------
all_indian_cities = load_cities()



#step 3: extract city name from user message using multiple strategies
#------------------------------------------------------------------------
#fatch the city name from user message
def extract_city(user_message):
    words = user_message.lower().split()
    
    # Words that can come after (in) but not city name
    non_city_words = {"house", "home", "office", "school", "college", "hospital", 
                      "park", "mall", "restaurant", "shop", "field", "farm", "village"}
    
#1 way to extract city name: look for "in [city]" pattern
    if "in" in words:
        index = words.index("in")
        if index + 1 < len(words):
            potential_city = words[index + 1]
            
            # skip that name it it availlble in non_city_words list
            if potential_city in non_city_words:
                return None  
            
            # If we have the cities database, validate it
            if all_indian_cities:
                if potential_city in all_indian_cities:
                    return potential_city.capitalize()
            else:
                #accept any word after "in" as city which is not in non_city_words list 
                return potential_city.capitalize()
    
    # way 2: Check if any word in the message is a known city
    if all_indian_cities:
        for word in words:
            if word in all_indian_cities:
                return word.capitalize()
    
    # way 3: Look for patterns like "weather in [city]" without "in"
    # Example: "Mumbai weather" - first word might be city
    if words and words[0] in all_indian_cities:
        return words[0].capitalize()
    
    return None  # No valid city found 



#step 4: use the extracted city name to fetch weather data and generate reply
#---------------------------------------------------------------------------------

#fetch weather data from weatherstack API and generate reply
def get_weather_reply(user_message):
    city = extract_city(user_message)
    
    # If no city found, ask user to specify
    if city is None:
        return "I couldn't find a city name in your message. Please mention the city name, for example: 'What's the weather in Ahmedabad?'"
    
    try:
        # Weatherstack API call
        url = f"http://api.weatherstack.com/current?access_key={API_KEY}&query={city}"
        data = requests.get(url).json()
        
        # Check if API returned an error
        if "error" in data:
            return f"Sorry, could not find weather data for '{city}'. Please check the city name."

        # extract values
        temp        = data["current"]["temperature"]
        humidity    = data["current"]["humidity"]
        condition   = data["current"]["weather_descriptions"][0]
        wind_speed  = data["current"]["wind_speed"]
        city_name   = data["location"]["name"]

        # farming advice
        advice = get_advice(temp, humidity, condition)

        return (
            f"🌤️ Weather in {city_name}:\n"
            f" 🌡️ Temperature : {temp}°C\n"
            f" 💧 Humidity    : {humidity}%\n"
            f" ☁️ Condition   : {condition}\n"
            f" 💨 Wind        : {wind_speed} km/h\n\n"
            f"🌾 Farming advice: {advice}"
        )

    except Exception as e:
        return f"Sorry, could not fetch weather. Error: {str(e)}"


#step 5: generate farming advice based on weather conditions
#---------------------------------------------------------------------------------


def get_advice(temp, humidity, condition):
    condition = condition.lower()

    if "rain" in condition:
        return "🌧️ Rain expected. Do NOT spray pesticide or fertilizer today."
    elif "storm" in condition or "thunder" in condition:
        return "⚡ Storm warning! Stay safe, avoid going to the field."
    elif temp > 40:
        return "🔥 Very hot! Water crops in early morning or evening only."
    elif temp > 35:
        return "☀️ Hot day. Increase irrigation. Avoid afternoon field work."
    elif temp < 10:
        return "❄️ Cold weather. Protect sensitive crops from frost tonight."
    elif humidity > 80:
        return "💦 High humidity. Watch for fungal disease on your crops."
    elif "clear" in condition or "sunny" in condition:
        return "✅ Clear sky. Good day for harvesting and field work."
    else:
        return "🌿 Weather looks normal. Good day for regular farm work."


#step 6: test the function with various user messages to ensure city extraction and weather fetching works correctly
#----------------------------------------------------------------------------------------------------------------------
# Test the function
if __name__ == "__main__":
    # Test cases
    print("Testing extract_city function:\n")
    print(get_weather_reply("weather in Ahmedabad"))

    test_messages = [
        "What is weather in Ahmedabad",
        "I am in Surat",
        "Weather in Vadodara please",
        "I am in house",  # Should return None
        "Rajkot temperature",  # Should work even without "in"
        "Hello how are you",  # Should return None
    ]
    
    for msg in test_messages:
        print(f"Message: {msg}")
        print(get_weather_reply(msg))