"""Open-Meteo tools used only by the weather sub-agent. No API key."""

from __future__ import annotations

from langchain_core.tools import tool

from agent.openmeteo import AIR_QUALITY_URL, FORECAST_URL, GEOCODE_URL, compact_json, get

WMO = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _decode_code(code) -> str:
    try:
        return WMO.get(int(code), f"WMO {code}")
    except (TypeError, ValueError):
        return str(code)


@tool
def geocode_place(name: str) -> str:
    """Resolve a city or place name to latitude, longitude, country, and timezone."""
    data = get(GEOCODE_URL, name=name, count=5, language="en", format="json")
    results = data.get("results")
    if not isinstance(results, list):
        return compact_json(data)
    places = []
    for item in results[:5]:
        places.append(
            {
                "name": item.get("name"),
                "admin1": item.get("admin1"),
                "country": item.get("country"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "timezone": item.get("timezone"),
                "population": item.get("population"),
            }
        )
    return compact_json({"places": places})


@tool
def get_current_weather(latitude: float, longitude: float) -> str:
    """Current conditions for a lat/lon: temperature, wind, precipitation, weather code."""
    data = get(
        FORECAST_URL,
        latitude=latitude,
        longitude=longitude,
        current=(
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        ),
        timezone="auto",
        forecast_days=1,
    )
    current = data.get("current")
    if isinstance(current, dict) and "weather_code" in current:
        current = {**current, "weather": _decode_code(current.get("weather_code"))}
    return compact_json(
        {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "current_units": data.get("current_units"),
            "current": current if isinstance(current, dict) else current,
        }
    )


@tool
def get_daily_forecast(latitude: float, longitude: float, forecast_days: int = 7) -> str:
    """Daily forecast for a lat/lon. forecast_days is 1–16 (default 7)."""
    days = max(1, min(int(forecast_days), 16))
    data = get(
        FORECAST_URL,
        latitude=latitude,
        longitude=longitude,
        daily=(
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        ),
        timezone="auto",
        forecast_days=days,
    )
    daily = data.get("daily")
    if not isinstance(daily, dict) or "time" not in daily:
        return compact_json(data)

    def col(key, i):
        vals = daily.get(key) or []
        return vals[i] if i < len(vals) else None

    rows = []
    for i, day in enumerate(daily.get("time") or []):
        rows.append(
            {
                "date": day,
                "weather": _decode_code(col("weather_code", i)),
                "temp_max_c": col("temperature_2m_max", i),
                "temp_min_c": col("temperature_2m_min", i),
                "precip_mm": col("precipitation_sum", i),
                "precip_prob_max": col("precipitation_probability_max", i),
                "wind_max_kmh": col("wind_speed_10m_max", i),
            }
        )
    return compact_json(
        {
            "timezone": data.get("timezone"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "daily": rows,
        }
    )


@tool
def get_air_quality(latitude: float, longitude: float) -> str:
    """Current air quality for a lat/lon: European AQI, US AQI, PM2.5, PM10, NO2, O3."""
    data = get(
        AIR_QUALITY_URL,
        latitude=latitude,
        longitude=longitude,
        current="european_aqi,us_aqi,pm10,pm2_5,nitrogen_dioxide,ozone,carbon_monoxide",
        timezone="auto",
        forecast_days=1,
    )
    return compact_json(
        {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "current_units": data.get("current_units"),
            "current": data.get("current"),
        }
    )


def get_weather_tools():
    return [geocode_place, get_current_weather, get_daily_forecast, get_air_quality]
