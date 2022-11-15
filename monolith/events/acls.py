from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests
import json


def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f'https://api.pexels.com/v1/search?query={city} {state}&per_page=1'
    response = requests.get(url, headers=headers)
    content = json.loads(response.content)
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_weather_data(city, state):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&appid={OPEN_WEATHER_API_KEY}"

    response = requests.get(url)
    content = json.loads(response.content)
    weather_details = {
        "lat": content[0]["lat"],
        "lon": content[0]["lon"],
    }

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={weather_details['lat']}&lon={weather_details['lon']}&appid={OPEN_WEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    content = json.loads(response.content)
    weather_temp = {
        "description": content["weather"][0]["description"],
        "temp": content["main"]["temp"]
    }

    return weather_temp
