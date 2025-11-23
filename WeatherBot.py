
import datetime
import requests
from config import WEATHER_CODE_MAP


class WeatherAPI:
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    WEEKDAY_MAP = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    RELATIVE_DAYS = {
        "today": 0,
        "now": 0,
        "tonight": 0,
        "tomorrow": 1,
    }

    # Get date from keyword
    def get_time(self, keyword: str | None) -> datetime.date:
        current_date = datetime.date.today()

        if keyword is None:
            return current_date

        kw = keyword.lower()

        # relative keywords
        if kw in WeatherAPI.RELATIVE_DAYS:
            return current_date + datetime.timedelta(days=WeatherAPI.RELATIVE_DAYS[kw])

        # weekdays
        if kw in WeatherAPI.WEEKDAY_MAP:
            target = WeatherAPI.WEEKDAY_MAP[kw]
            today_wd = current_date.weekday()
            delta = (target - today_wd) % 7
            return current_date + datetime.timedelta(days=delta)

        # return date
        try:
            return datetime.date.fromisoformat(kw)
        except ValueError:
            return current_date

    # Get lat/lon from city name
    def geocode_city(self, city: str):
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        try:
            r = requests.get(self.GEO_URL, params=params, timeout=5)
        except Exception as e:
            return None, None, f"Geocoding error: {e}"

        if r.status_code != 200:
            return None, None, f"Geocoding HTTP error: {r.status_code}"

        data = r.json()
        results = data.get("results")
        if not results:
            return None, None, f"Could not find city '{city}'."

        first = results[0]
        return first["latitude"], first["longitude"], first["name"]

	# Get weather data
    def get_weather(self, city: str, time_keyword: str | None = None) -> dict:
        
		# Find the date corresponding to time_keyword
        target_date = self.get_time(time_keyword)

        lat, lon, resolved_name_or_error = self.geocode_city(city)
        if lat is None:
            return {"error": resolved_name_or_error}  # error message

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": (
                "weathercode,temperature_2m_max,temperature_2m_min,"
                "sunrise,sunset,windspeed_10m_max"
            ),
            "forecast_days": 7,
            "timezone": "auto",
        }

        try:
            r = requests.get(self.FORECAST_URL, params=params, timeout=5)
        except Exception as e:
            return {"error": f"Weather API connection error: {e}"}

        if r.status_code != 200:
            return {"error": f"Weather API HTTP error: {r.status_code}"}

        data = r.json()
        daily = data.get("daily")
        if not daily:
            return {"error": "No daily weather data available."}

        # choose correct day index
        dates_str = daily.get("time", [])
        if not dates_str:
            return {"error": "Missing dates in weather data."}

        dates = [datetime.date.fromisoformat(ds) for ds in dates_str]
        try:
            idx = dates.index(target_date)
        except ValueError:
            # if requested date is outside forecast, choose closest
            diffs = [abs((d - target_date).days) for d in dates]
            idx = diffs.index(min(diffs))

        code = daily["weathercode"][idx]
        description = WEATHER_CODE_MAP.get(code, "Unknown weather")

        temp_max = daily["temperature_2m_max"][idx]
        temp_min = daily["temperature_2m_min"][idx]
        wind = daily["windspeed_10m_max"][idx]
        sunrise = daily["sunrise"][idx]
        sunset = daily["sunset"][idx]
        chosen_date = dates[idx].isoformat()

        cw = data.get("current_weather")
        current_temp = cw["temperature"] if cw and idx == 0 else None
        current_wind = cw["windspeed"] if cw and idx == 0 else None

        return {
            "status": "ok",
            "city": resolved_name_or_error,
            "requested_keyword": time_keyword,
            "date": chosen_date,
            "description": description,
            "weathercode": code,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "daily_wind": wind,
            "sunrise": sunrise,
            "sunset": sunset,
            "current_temp": current_temp,
            "current_wind": current_wind,
        }