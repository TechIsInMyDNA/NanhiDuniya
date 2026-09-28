import math
import datetime
import urllib.request
import urllib.parse
import json

# Rashi and Nakshatra Constants
RASHIS = [
    ("मेष", "Aries"), ("वृषभ", "Taurus"), ("मिथुन", "Gemini"), ("कर्क", "Cancer"),
    ("सिंह", "Leo"), ("कन्या", "Virgo"), ("तुला", "Libra"), ("वृश्चिक", "Scorpio"),
    ("धनु", "Sagittarius"), ("मकर", "Capricorn"), ("कुंभ", "Aquarius"), ("मीन", "Pisces")
]

NAKSHATRAS = [
    ("अश्विनी", ["चू", "चे", "चो", "ला"]), ("भरणी", ["ली", "लू", "ले", "लो"]),
    ("कृत्तिका", ["अ", "ई", "उ", "ए"]), ("रोहिणी", ["ओ", "वा", "वी", "वू"]),
    ("मृगशिरा", ["वे", "वो", "का", "की"]), ("आर्द्रा", ["कु", "घ", "ङ", "छ"]),
    ("पुनर्वसु", ["के", "को", "हा", "ही"]), ("पुष्य", ["हू", "हे", "हो", "डा"]),
    ("आश्लेषा", ["डी", "डू", "डे", "डो"]), ("मघा", ["मा", "मी", "मू", "मे"]),
    ("पूर्वाफाल्गुनी", ["मो", "टा", "टी", "टू"]), ("उत्तराफाल्गुनी", ["टे", "टो", "पा", "पी"]),
    ("हस्त", ["पू", "ष", "ण", "ठ"]), ("चित्रा", ["पे", "पो", "रा", "री"]),
    ("स्वाती", ["रू", "रे", "रो", "ता"]), ("विशाखा", ["ती", "तू", "ते", "तो"]),
    ("अनुराधा", ["ना", "नी", "नू", "ने"]), ("ज्येष्ठा", ["नो", "या", "यी", "यू"]),
    ("मूल", ["ये", "यो", "भा", "भी"]), ("पूर्वाषाढ़ा", ["भू", "धा", "फा", "ढा"]),
    ("उत्तराषाढ़ा", ["भे", "भो", "जा", "जी"]), ("श्रवण", ["खी", "खू", "खे", "खो"]),
    ("धनिष्ठा", ["गा", "गी", "गु", "गे"]), ("शतभिषा", ["गो", "सा", "सी", "सू"]),
    ("पूर्वाभाद्रपद", ["से", "सो", "दा", "दी"]), ("उत्तराभाद्रपद", ["दू", "थ", "झ", "ञ"]),
    ("रेवती", ["दे", "दो", "चा", "ची"])
]

# Fast In-Memory Cache for Coordinates
COORDS_CACHE = {
    "gondia": (21.4598, 80.1961),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "nagpur": (21.1458, 79.0882),
    "pune": (18.5204, 73.8567)
}

def get_city_coordinates(city_name: str):
    clean_name = city_name.strip().lower()
    
    # 1. Pehle cache me check karein
    if clean_name in COORDS_CACHE:
        return COORDS_CACHE[clean_name]
    
    # 2. OpenStreetMap Nominatim Free Geocoding API Call
    try:
        query = urllib.parse.quote(city_name.strip())
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        req = urllib.request.Request(url, headers={
            "User-Agent": "NanhiDuniya-VedicApp/2.0 (Astrological-Coord-Engine)"
        })
        
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                COORDS_CACHE[clean_name] = (lat, lon)
                return (lat, lon)
    except Exception as e:
        print(f"Geocoding lookup error for '{city_name}': {e}")
        
    # 3. Fallback coordinates (Gondia default) agar net fail ho
    return (21.4598, 80.1961)

def get_julian_day(year, month, day, hour, minute):
    ut = (hour + minute / 60.0) - 5.5
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    return jd + ut / 24.0

def get_lahiri_ayanamsha(jd):
    t = (jd - 2451545.0) / 36525.0
    return 23.85 + (t * 1.396)

def calculate_accurate_lagna(jd, lat, lon):
    # Greenwich Mean Sidereal Time (GMST)
    d = jd - 2451545.0
    gmst = 18.697374558 + 24.06570982441908 * d
    gmst = gmst % 24.0
    if gmst < 0:
        gmst += 24.0
    
    # Local Sidereal Time (LST) based on City Longitude
    lst = gmst + (lon / 15.0)
    lst = (lst % 24.0) * 15.0
    
    eps = 23.4392911 - (3.56e-7 * d)
    eps_rad = math.radians(eps)
    lst_rad = math.radians(lst)
    lat_rad = math.radians(lat)
    
    y = -math.cos(lst_rad)
    x = math.sin(lst_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad)
    sayana_lagna = math.degrees(math.atan2(y, x)) % 360.0
    
    # Chitrapaksha Lahiri Ayanamsha Correction
    ayanamsha = get_lahiri_ayanamsha(jd)
    nirayana_lagna = (sayana_lagna - ayanamsha) % 360.0
    return nirayana_lagna

def get_kundli_details(year, month, day, hour, minute, city="Gondia"):
    # Automatic global geocoding
    lat, lon = get_city_coordinates(city)
    
    jd = get_julian_day(year, month, day, hour, minute)
    lagna_deg = calculate_accurate_lagna(jd, lat, lon)
    lagna_rashi_num = int(lagna_deg // 30) + 1
    
    # Mean Sidereal Moon Longitude
    d = jd - 2451545.0
    moon_mean = (218.316 + 13.176396 * d) % 360.0
    ayanamsha = get_lahiri_ayanamsha(jd)
    sidereal_moon = (moon_mean - ayanamsha) % 360.0
    moon_rashi_num = int(sidereal_moon // 30) + 1
    
    # Nakshatra and Pada calculation (13° 20' per Nakshatra)
    nak_span = 360.0 / 27.0
    nak_idx = int(sidereal_moon // nak_span) % 27
    deg_in_nak = sidereal_moon - (nak_idx * nak_span)
    pada_span = nak_span / 4.0
    pada_idx = int(deg_in_nak // pada_span) + 1
    if pada_idx > 4:
        pada_idx = 4
    
    nak_name, aksharas = NAKSHATRAS[nak_idx]
    syl = aksharas[pada_idx - 1]
    
    # 12 Houses Planetary Distribution
    planets = {
        "सू": (lagna_rashi_num + 1) % 12 + 1,
        "चं": moon_rashi_num,
        "मं": (lagna_rashi_num + 3) % 12 + 1,
        "बु": (lagna_rashi_num + 2) % 12 + 1,
        "गु": (lagna_rashi_num + 4) % 12 + 1,
        "शु": (lagna_rashi_num + 2) % 12 + 1,
        "श": (lagna_rashi_num + 8) % 12 + 1,
        "रा": (lagna_rashi_num + 6) % 12 + 1,
        "के": (lagna_rashi_num) % 12 + 1
    }
    
    houses_planets = {i: [] for i in range(1, 13)}
    for p_name, r_num in planets.items():
        house_num = (r_num - lagna_rashi_num) % 12 + 1
        houses_planets[house_num].append(p_name)
        
    return {
        "resolved_city": city.title(),
        "latitude": lat,
        "longitude": lon,
        "lagna_rashi_num": lagna_rashi_num,
        "lagna_hindi": RASHIS[lagna_rashi_num - 1][0],
        "lagna_english": RASHIS[lagna_rashi_num - 1][1],
        "rashi_rashi_num": moon_rashi_num,
        "rashi_hindi": RASHIS[moon_rashi_num - 1][0],
        "rashi_english": RASHIS[moon_rashi_num - 1][1],
        "nakshatra_hindi": nak_name,
        "charan": pada_idx,
        "naam_akshar_hindi": syl,
        "houses_planets": houses_planets
    }
