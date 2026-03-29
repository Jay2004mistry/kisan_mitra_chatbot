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
        advice = get_advice(temp, humidity, condition, wind_speed)

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


def get_advice(temp, humidity, condition, wind_speed):
    condition = condition.lower()
    advice_list = []
    
    # 1. STORM / THUNDER CHECK (Highest Priority)
    if "storm" in condition or "thunder" in condition:
        advice_list.append("⚡⚡ STORM WARNING! Stay safe, avoid going to the field completely.")
        if wind_speed > 30:
            advice_list.append("💨 Very strong winds (>30 km/h) with storm - secure all farm equipment")
        if "rain" in condition:
            advice_list.append("🌧️ Heavy rain expected - risk of waterlogging")
        return "\n".join(advice_list)
    
    # 2. RAIN CHECK
    if "rain" in condition:
        advice_list.append("🌧️ Rain detected/expected")
        if wind_speed > 30:
            advice_list.append("💨 Very strong winds with rain - DO NOT spray anything")
        elif wind_speed > 20:
            advice_list.append("🍃 Strong winds with rain - chemicals will drift away")
        elif wind_speed > 10:
            advice_list.append("🌬️ Moderate winds with rain - delay spraying")
        else:
            advice_list.append("🎯 Calm rain - good for natural irrigation")
        
        if temp > 35:
            advice_list.append("☀️ Hot rain - can cause leaf burn, check crops after rain")
        if humidity > 80:
            advice_list.append("💦 High humidity + rain = HIGH fungal disease risk")
        
        if not advice_list:
            advice_list.append("Do NOT spray pesticide or fertilizer today")
        return "\n".join(advice_list)
    
    # 3. SMOKE / FOG / HAZE CHECK
    if "smoke" in condition or "fog" in condition or "haze" in condition:
        advice_list.append(f"🌫️ {condition.capitalize()} detected - poor air quality")
        
        if wind_speed > 20:
            advice_list.append("💨 Strong winds spreading smoke/haze - DO NOT spray pesticides")
        elif wind_speed > 10:
            advice_list.append("🍃 Moderate winds - chemicals will drift in smoky conditions")
        else:
            advice_list.append("🎯 Calm conditions - smoke/fog may settle on crops")
        
        advice_list.append("😷 Limit outdoor field work - wear N95 mask if possible")
        advice_list.append("🌱 Smoke can reduce photosynthesis - monitor crop health")
        
        if temp > 35:
            advice_list.append("🔥 Heat + smoke = additional crop stress")
        if humidity > 70:
            advice_list.append("💦 High humidity + smoke = smoke particles stick to leaves")
        
        return "\n".join(advice_list)
    
    # 4. EXTREME HEAT (temp > 40°C)
    if temp > 40:
        advice_list.append("🔥🔥 EXTREME HEAT WARNING! Temperature above 40°C")
        
        if humidity < 30:
            advice_list.append("🏜️ Very dry conditions - extreme evaporation risk")
            advice_list.append("💧 Water crops immediately - increase irrigation by 50%")
        elif humidity > 70:
            advice_list.append("💦 Extreme heat with high humidity - dangerous heat stress for crops")
            advice_list.append("💧 Water crops heavily in early morning and evening")
        else:
            advice_list.append("💧 Water crops in early morning or evening only")
        
        if wind_speed > 20:
            advice_list.append("💨 Hot winds (>20 km/h) - rapid soil drying")
        elif wind_speed < 5:
            advice_list.append("🌡️ No breeze - heat accumulates on leaf surface")
        
        advice_list.append("🧑‍🌾 Avoid field work between 11 AM - 4 PM")
        advice_list.append("🌾 Use mulch to retain soil moisture")
        
        return "\n".join(advice_list)
    
    # 5. HIGH HEAT (35°C - 40°C)
    if temp > 35:
        advice_list.append(f"☀️ Hot day: {temp}°C")
        
        if humidity > 70:
            advice_list.append("💦 Hot and humid = HIGH fungal disease risk")
            advice_list.append("🔍 Check crops daily for fungus")
        elif humidity < 30:
            advice_list.append("🏜️ Hot and dry - increase irrigation frequency")
        
        if wind_speed > 20:
            advice_list.append("💨 Hot and windy - high evaporation rate")
            advice_list.append("💧 Irrigate today to prevent wilting")
        elif wind_speed > 10:
            advice_list.append("🍃 Moderate breeze - good for air circulation")
        
        if wind_speed < 5:
            advice_list.append("🎯 Calm hot conditions - avoid spraying in afternoon")
        
        advice_list.append("⏰ Water crops in early morning only")
        advice_list.append("🧑‍🌾 Avoid afternoon field work")
        
        return "\n".join(advice_list)
    
    # 6. COLD WEATHER (temp < 10°C)
    if temp < 10:
        advice_list.append(f"❄️ Cold weather: {temp}°C")
        
        if wind_speed > 15:
            advice_list.append("💨 Cold winds - severe wind chill effect")
            advice_list.append("🛡️ Protect sensitive crops with wind barriers")
        
        if humidity > 80:
            advice_list.append("💦 Cold and damp - frost risk very high")
            advice_list.append("🌙 Cover crops tonight - use plastic or cloth")
        
        if "clear" in condition:
            advice_list.append("✨ Clear cold night - highest frost risk")
        
        advice_list.append("🔥 Delay morning irrigation until temperature rises")
        advice_list.append("🌾 Harvest sensitive crops before cold spell")
        
        return "\n".join(advice_list)
    
    # 7. MODERATE COLD (10°C - 15°C)
    if temp < 15:
        advice_list.append(f"🍂 Cool weather: {temp}°C")
        
        if wind_speed > 15:
            advice_list.append("💨 Cool winds - protect young plants")
        
        if humidity > 80:
            advice_list.append("💦 Cool and damp - watch for fungal issues")
        
        advice_list.append("✅ Good for leafy vegetable growth")
        advice_list.append("⏰ Delay early morning spraying until dew dries")
        
        return "\n".join(advice_list)
    
    # 8. HIGH HUMIDITY (>80%) - No rain
    if humidity > 80:
        advice_list.append(f"💦 High humidity: {humidity}%")
        
        if temp > 30:
            advice_list.append("☀️ Warm + humid = HIGH fungal disease risk!")
            advice_list.append("🔍 Inspect crops for powdery mildew and blight")
        elif temp > 25:
            advice_list.append("🌡️ Moderate warmth + humidity - fungal risk moderate")
        else:
            advice_list.append("🌙 Cool + humid - morning dew expected")
        
        if wind_speed < 5:
            advice_list.append("🎯 Calm conditions - moisture stays on leaves")
            advice_list.append("⏰ Delay morning spraying - let dew dry first")
        elif wind_speed > 15:
            advice_list.append("💨 Good air movement - helps dry leaves")
        
        advice_list.append("🌾 Consider preventive fungicide when conditions improve")
        
        return "\n".join(advice_list)
    
    # 9. LOW HUMIDITY (<30%) - No rain
    if humidity < 30:
        advice_list.append(f"🏜️ Low humidity: {humidity}% - dry conditions")
        
        if temp > 35:
            advice_list.append("🔥 Hot and dry - extreme evaporation")
            advice_list.append("💧 Drip irrigation recommended")
        elif temp > 30:
            advice_list.append("☀️ Warm and dry - increase irrigation frequency")
        
        if wind_speed > 15:
            advice_list.append("💨 Dry winds - soil drying fast")
            advice_list.append("💧 Irrigate today")
        
        advice_list.append("🌾 Mulch to retain soil moisture")
        advice_list.append("✅ Low disease risk due to dry conditions")
        
        return "\n".join(advice_list)
    
    # 10. WIND SPEED BASED ADVICE
    if wind_speed > 30:
        advice_list.append("💨💨 VERY STRONG WINDS (>30 km/h)!")
        advice_list.append("❌ DO NOT spray pesticides - extreme drift risk")
        advice_list.append("🔒 Secure loose farm equipment and greenhouse covers")
        advice_list.append("🌾 Tall crops may lodge - consider support")
        
    elif wind_speed > 20:
        advice_list.append(f"🍃 Strong winds: {wind_speed} km/h")
        advice_list.append("❌ Avoid spraying - high chemical drift risk")
        if humidity > 70:
            advice_list.append("💦 High humidity + strong wind = poor spray coverage")
        advice_list.append("🔒 Secure light equipment")
        
    elif wind_speed > 15:
        advice_list.append(f"🍃 Moderate winds: {wind_speed} km/h")
        advice_list.append("⚠️ Be careful if spraying - reduce pressure")
        advice_list.append("🎯 Use coarser nozzles to reduce drift")
        
    elif wind_speed > 8:
        advice_list.append(f"🌬️ Light breeze: {wind_speed} km/h")
        advice_list.append("✅ Acceptable for spraying with caution")
        
    elif wind_speed < 5 and wind_speed >= 0:
        advice_list.append(f"🎯 Calm winds: {wind_speed} km/h")
        if temp > 15 and temp < 32 and humidity > 40 and humidity < 70:
            advice_list.append("✅ PERFECT spraying conditions!")
        else:
            advice_list.append("✅ Good conditions for spraying")
    
    # 11. CLEAR / SUNNY SKY
    if "clear" in condition or "sunny" in condition:
        if "clear" in advice_list:
            pass
        else:
            advice_list.append("☀️ Clear sky / sunny")
        
        if wind_speed < 10 and humidity > 40 and humidity < 60:
            advice_list.append("✅ PERFECT harvesting weather!")
        elif wind_speed > 20:
            advice_list.append("⚠️ Windy - delay harvesting tall crops")
        elif temp > 35:
            advice_list.append("🌡️ Hot - harvest early morning only")
        
        if humidity > 70:
            advice_list.append("💦 Morning dew present - wait for it to dry")
        
        advice_list.append("✅ Good for field work and harvesting")
    
  
    if not advice_list:
        advice_list.append("🌿 Weather looks normal")
        advice_list.append("✅ Good day for regular farm work")
        
        if temp > 20 and temp < 30 and humidity > 40 and humidity < 60:
            advice_list.append("🎯 Ideal conditions for most farming activities")
    
    # Return combined advice
    return "\n".join(advice_list)


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