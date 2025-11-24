from WeatherBot import WeatherAPI
import random
import re
import string
import nltk
from spellchecker import SpellChecker
import datetime
from config import KNOWN_CITIES


class Chatbot:
    def __init__(self):
        self.keywords = {
            "greetings": ["hello", "hi", "hey", "howdy", "hullo"],
            "feeling": ["how are you", "how is it going", "how do you do"],
            "goodbye": ["bye", "goodbye", "see you", "later"],
            "weather": ["weather", "rain", "sunny", "forecast", 'sunrise', 'sunset', 'temperature', 'temp', 'wind', 'weather', 'rain', 'windy', 'hot', 'cold', 'freezing', 'chilly', 'warm', 'humid'],
            "time": ["time", "hour", "clock"],
            "name": ["your name", "who are you"],
            "thanks": ["thank", "thanks", "thank you", "ty"],
            "rude": ["rude", "mean", "stupid", "idiot", "dumb" ]
        }
        self.responses = {
            "greetings": ["Hello!", "Hey there!", "Hi! How can I help you?"],
            "feeling": ["I'm just a bot, but thanks for asking!", "Doing great, how about you?"],
            "goodbye": ["Hasta la vista baby!", "Ciao"],
            "time": ["We said a weather bot, this is not a time bot, check your watch!", "Time is an illusion."],
            "name": ["You really want me to be your friend huh ? I am just a robot... Sorry you are so lonely.",],
            "thanks": ["You're welcome!", "No problem!", "Glad I could help!"],
            "rude": ["You are the rude own here"],
            "unknown": ["wtf are you saying ?"]
        }
        self.weather_api = WeatherAPI()

		# building regex patterns
            # First let's add a bunch of synonyms to our keywords and expand the list
        self.complete_keywords_dict(self.keywords)
        self.patterns = self.build_patterns_dict(self.keywords)

        # define spellchecker
        self.spell = SpellChecker()

    # normalization
    def normalize(self, text: str) -> str:
        # Lowercase, remove punctuation, strip whitespace
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text.strip()
    
    # find synonym for a given word
    def get_synonyms(self, word):
        synonyms = set()
        for syn in nltk.corpus.wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().lower())
        return synonyms
    
    # Expands the keyword list 
    def expand_keywords(self, intent, keywords_list):
        expanded_keywords = set()
        
        # Add synonyms for the intent itself
        expanded_keywords.update(self.get_synonyms(intent))
        
        # Add synonyms for each keyword in the list
        for keyword in keywords_list:
            expanded_keywords.update(self.get_synonyms(keyword))
            # Also add the original keyword
            expanded_keywords.add(self.normalize(keyword))
        
        return expanded_keywords

    # complete keywords dict
    def complete_keywords_dict(self, keywords):
        completed = {}

        for intent, kw_list in keywords.items():
            completed[intent] = list(self.expand_keywords(intent, kw_list))

        self.keywords = completed
        return completed
    
    # Build regex pattern from keyword list
    def build_regex_pattern(self, keyword_list):
        parts = []
        for kw in keyword_list:
            kw = re.escape(kw)
            parts.append(rf".*\b{kw}\b.*")
        # join with OR
        pattern = "|".join(parts)
        return pattern
    
    # Build patterns dict
    def build_patterns_dict(self, keywords_list):
        patterns = {}
        for intent, kw_list in keywords_list.items():
            patterns[intent] = self.build_regex_pattern(kw_list)
        return patterns

    # Spellchecker
    def correct_spelling(self, word):
        corrected_word = self.spell.candidates(word)
        if corrected_word:
            return list(corrected_word)[0]
        return word
    
    # find intent from user message
    def match_patterns(self, user_message):
        # extract words
        words = user_message.split()

        # Normalize words
        normalized_words = [self.normalize(w) for w in words]
        
        # correct spelling
        corrected_words = [self.correct_spelling(w) for w in normalized_words]

        # Normalize words
        corrected_message = " ".join(corrected_words)

        for intent, pattern in self.patterns.items():
            if re.match(pattern, corrected_message, re.IGNORECASE):
                return intent
        return "unknown"
    
    # get response from intent
    def get_message_from_intent(self, intent, responses_dict):
        if intent in responses_dict:
            return random.choice(responses_dict[intent])
        else:
            return random.choice(responses_dict["unknown"])
    
    # extract cities 
    def extract_cities(self, user_input, known_cities):
        user_input = user_input.lower()
        user_input = user_input.translate(str.maketrans("", "", string.punctuation))
        user_input = user_input.replace("-", " ").replace(' ', '')
        for city in known_cities:
            city_normalized = city.lower().replace(" ", "")
            if city_normalized in user_input:
                return city
        return None
    
    # extract date
    def extract_date(self, user_input):
        user_input = user_input.lower()
        user_input = user_input.translate(str.maketrans("", "", string.punctuation))
        user_input = user_input.replace("-", " ").replace(' ', '')
        today_keywords = ["today", "now", "tonight", "thisday"]
        tomorrow_keywords = ["tomorrow", "nextday"]
        weekdays = [
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
        ]
        if any(kw in user_input for kw in today_keywords):
            return "today"
        elif any(kw in user_input for kw in tomorrow_keywords):
            return "tomorrow"
        else:
            for day in weekdays:
                if day in user_input:
                    return day
        return None
    
    # extract keywords
    def extract_keywords(self, user_input):
        accepted = [
            'sunrise', 'sunset', 'temperature', 'temp', 'wind', 'rain', 'windy'
        ]
        user_input = user_input.lower()
        user_input = user_input.translate(str.maketrans("", "", string.punctuation))
        words = user_input.split()
        keywords = [w for w in words if w in accepted]
        return keywords
    
    # temperature mood
    def _temperature_mood(self, t_min, t_max):
        avg = (t_min + t_max) / 2

        if avg < 0:
            return "It's absolutely freezing out there, bring everything you own.", "🥶❄️"
        elif avg < 5:
            return "Pretty cold, coat and maybe a scarf are a good idea.", "🧣🥶"
        elif avg < 15:
            return "Cool and fresh, perfect hoodie weather.", "🧥🙂"
        elif avg < 25:
            return "Very pleasant, you picked a good day.", "🌤🙂"
        elif avg < 32:
            return "Warm and a bit sweaty, stay hydrated.", "😅🌞"
        else:
            return "Scorching hot, like walking into an oven.", "🥵🔥"
    
    # Human date
    def _human_date(self, iso_date: str) -> str:
        #Convert '2025-11-24' → '24th of November'
        dt = datetime.date.fromisoformat(iso_date)
        day = dt.day

        # Determine suffix
        if 11 <= day % 100 <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        month_name = dt.strftime("%B")  # e.g. "November"
        return f"{day}{suffix} of {month_name}"

    def human_time(self, iso_time: str) -> str:
        # Convert '2025-11-24T06:53' → '6:53 AM'
        dt = datetime.datetime.fromisoformat(iso_time)
        return dt.strftime("%I:%M %p").lstrip("0")

    def chat(self, user_input):
        intent = self.match_patterns(user_input)
        print("Detected intent:", intent)
        if intent == "weather":
            # We use our own entity extraction, more robust than generic regex
            city = self.extract_cities(user_input, KNOWN_CITIES)
            time_keyword = self.extract_date(user_input)
            additional_keyword = self.extract_keywords(user_input)  # ['sunrise'], ['temp']

            print("Extracted city:", city)
            print("Extracted time keyword:", time_keyword)
            print("Extracted additional keywords:", additional_keyword)

            weather_info = self.weather_api.get_weather(city, time_keyword)

            if "error" in weather_info:
                response = weather_info["error"]
                return response, intent

            # Common pieces
            t_min = weather_info["temp_min"]
            t_max = weather_info["temp_max"]
            mood_text, mood_emoji = self._temperature_mood(t_min, t_max)

            response = None 

            # If the user asked for something specific (sunrise, temp, wind, rain...)
            if additional_keyword:
                for w in additional_keyword:
                    w_low = w.lower()
                    if w_low in ["sunrise", "sunset"]:
                        response = (
                            f"The {w_low} in {weather_info['city']} on {self._human_date(weather_info['date'])} "
                            f"is at {self.human_time(weather_info[w_low])} {mood_emoji}"
                        )
                        break
                    elif w_low in ["temperature", "temp"]:
                        response = (
                            f"In {weather_info['city']} on {self._human_date(weather_info['date'])}, "
                            f"temperatures go from {t_min}°C to {t_max}°C. "
                            f"{mood_text} {mood_emoji}"
                        )
                        break
                    elif w_low == "wind" or w_low == "windy":
                        response = (
                            f"On {self._human_date(weather_info['date'])} in {weather_info['city']}, "
                            f"the maximum wind speed is {weather_info['daily_wind']} km/h. "
                            f"Better hold your hat! 💨🧢"
                        )
                        break
                    elif w_low == "rain":
                        response = (
                            f"The weather in {weather_info['city']} on {self._human_date(weather_info['date'])} is "
                            f"{weather_info['description'].lower()}. "
                            f"Maybe keep an umbrella nearby, just in case. we never know... ☔"
                        )
                        break

            # If no specific keyword matched, fall back to a general summary
            if response is None:
                response = (
                    f"Here's the weather for {weather_info['city']} on {self._human_date(weather_info['date'])}: "
                    f"{weather_info['description'].lower()}. "
                    f"Temperatures between {t_min}°C and {t_max}°C. "
                    f"Wind up to {weather_info['daily_wind']} km/h. "
                    f"{mood_text} {mood_emoji}"
                )

        else:
            # Non-weather intents
            response = self.get_message_from_intent(intent, self.responses)

        return response, intent