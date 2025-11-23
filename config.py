WEATHER_CODE_MAP = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Thick cloud cover",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    97: "Thunderstorm with heavy hail"
}

import pandas as pd

import nltk
import string
nltk.download('wordnet')
nltk.download('omw-1.4')

def load_city_list(path="cities1000.txt"):
    df = pd.read_csv(
        path,
        sep='\t',
        header=None,
        names=[
            "geonameid","name","asciiname","alternatenames","latitude","longitude",
            "feature class","feature code","country code","cc2","admin1","admin2",
            "admin3","admin4","population","elevation","dem","timezone","modification date"
        ],
        low_memory=False
    )
    df.sort_values("population", ascending=False, inplace=True)
    top_cities = df["name"].dropna().unique().tolist()[:1000]

    french_cities = df[df["country code"] == "FR"]["name"].dropna().unique().tolist()

    joined = [*top_cities, *french_cities]

    # remove countries with less than 4 letters to avoid false matches
    filtered = [city for city in joined if len(city) >= 4]

    return list(filtered)


KNOWN_CITIES = load_city_list("cities1000.txt")
