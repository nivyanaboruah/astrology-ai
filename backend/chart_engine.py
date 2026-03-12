import ephem
import math
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

geolocator = Nominatim(user_agent="astrology-ai")

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

TIMEZONE_OFFSETS = {
    "india": 5.5, "mumbai": 5.5, "delhi": 5.5, "kolkata": 5.5,
    "bangalore": 5.5, "chennai": 5.5, "hyderabad": 5.5,
    "tezpur": 5.5, "guwahati": 5.5, "pune": 5.5, "jaipur": 5.5,
    "london": 0, "new york": -5, "los angeles": -8,
    "dubai": 4, "singapore": 8, "sydney": 10,
    "paris": 1, "berlin": 1, "tokyo": 9,
}

def get_timezone_offset(place: str) -> float:
    place_lower = place.lower()
    for key, offset in TIMEZONE_OFFSETS.items():
        if key in place_lower:
            return offset
    return 5.5

def get_coordinates(place: str):
    location = geolocator.geocode(place)
    if not location:
        raise ValueError(f"Could not find location: {place}")
    return location.latitude, location.longitude

def get_lahiri_ayanamsa(year: int) -> float:
    """Lahiri ayanamsa — increases ~0.014 degrees per year."""
    base_year      = 2000
    base_ayanamsa  = 23.85
    precession     = 0.013972
    return base_ayanamsa + (year - base_year) * precession

def get_tropical_longitude(body, ephem_date) -> float:
    body.compute(ephem_date)
    ecl = ephem.Ecliptic(body, epoch='2000')
    return math.degrees(ecl.lon) % 360

def get_zodiac_sign(longitude_deg: float) -> str:
    index = int(longitude_deg / 30) % 12
    return ZODIAC_SIGNS[index]

def get_house(planet_lon: float, sun_lon: float) -> int:
    relative = (planet_lon - sun_lon) % 360
    house = int(relative / 30) + 1
    return house

def compute_birth_chart(name: str, dob: str, tob: str, place: str, system: str = "vedic") -> dict:
    """
    system: 'vedic' for Sidereal (Lahiri), 'western' for Tropical
    """
    lat, lon = get_coordinates(place)

    local_dt  = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    tz_offset = get_timezone_offset(place)
    utc_dt    = local_dt - timedelta(hours=tz_offset)
    birth_year = local_dt.year

    ephem_date = ephem.Date(utc_dt.strftime("%Y/%m/%d %H:%M:%S"))
    ayanamsa   = get_lahiri_ayanamsa(birth_year)

    planet_objects = {
        "Sun":     ephem.Sun(),
        "Moon":    ephem.Moon(),
        "Mercury": ephem.Mercury(),
        "Venus":   ephem.Venus(),
        "Mars":    ephem.Mars(),
        "Jupiter": ephem.Jupiter(),
        "Saturn":  ephem.Saturn(),
    }

    # Step 1 — get all tropical longitudes
    tropical_lons = {}
    for planet_name, planet_obj in planet_objects.items():
        tropical_lons[planet_name] = get_tropical_longitude(planet_obj, ephem_date)

    # Step 2 — compute sidereal longitudes
    sidereal_lons = {}
    for planet_name, trop_lon in tropical_lons.items():
        sidereal_lons[planet_name] = (trop_lon - ayanamsa) % 360

    # Step 3 — pick which system to use for display
    active_lons = sidereal_lons if system == "vedic" else tropical_lons
    sun_lon     = active_lons["Sun"]

    result = {
        "name":      name,
        "dob":       dob,
        "tob":       tob,
        "place":     place,
        "system":    system,
        "ayanamsa":  round(ayanamsa, 4),
        "utc_time":  utc_dt.strftime("%Y-%m-%d %H:%M"),
        "latitude":  lat,
        "longitude": lon,
        "planets":   {}
    }

    for planet_name in planet_objects:
        trop_lon = tropical_lons[planet_name]
        sid_lon  = sidereal_lons[planet_name]
        disp_lon = sid_lon if system == "vedic" else trop_lon

        result["planets"][planet_name] = {
            "longitude":          round(disp_lon, 2),
            "tropical_longitude": round(trop_lon, 2),
            "sidereal_longitude": round(sid_lon, 2),
            "sign":               get_zodiac_sign(disp_lon),
            "western_sign":       get_zodiac_sign(trop_lon),
            "vedic_sign":         get_zodiac_sign(sid_lon),
            "house":              get_house(disp_lon, sun_lon)
        }

    return result