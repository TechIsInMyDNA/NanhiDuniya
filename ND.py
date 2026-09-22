import math

RASHIS = [
    {"hindi": "मेष", "english": "Aries"},
    {"hindi": "वृषभ", "english": "Taurus"},
    {"hindi": "मिथुन", "english": "Gemini"},
    {"hindi": "कर्क", "english": "Cancer"},
    {"hindi": "सिंह", "english": "Leo"},
    {"hindi": "कन्या", "english": "Virgo"},
    {"hindi": "तुला", "english": "Libra"},
    {"hindi": "वृश्चिक", "english": "Scorpio"},
    {"hindi": "धनु", "english": "Sagittarius"},
    {"hindi": "मकर", "english": "Capricorn"},
    {"hindi": "कुंभ", "english": "Aquarius"},
    {"hindi": "मीन", "english": "Pisces"}
]

NAKSHATRA_DATA = [
    {"name": "अश्विनी", "letters": ["चू", "चे", "चो", "ला"]},
    {"name": "भरणी", "letters": ["ली", "लू", "ले", "लो"]},
    {"name": "कृत्तिका", "letters": ["अ", "ई", "उ", "ए"]},
    {"name": "रोहिणी", "letters": ["ओ", "वा", "वी", "वू"]},
    {"name": "मृगशिरा", "letters": ["वे", "वो", "का", "की"]},
    {"name": "आर्द्रा", "letters": ["कू", "घ", "ङ", "छ"]},
    {"name": "पुनर्वसु", "letters": ["के", "को", "हा", "ही"]},
    {"name": "पुष्य", "letters": ["हू", "हे", "हो", "डा"]},
    {"name": "आश्लेषा", "letters": ["डी", "डू", "डे", "डो"]},
    {"name": "मघा", "letters": ["मा", "मी", "मू", "मे"]},
    {"name": "पूर्वाफाल्गुनी", "letters": ["मो", "टा", "टी", "टू"]},
    {"name": "उत्तराफाल्गुनी", "letters": ["टे", "टो", "पा", "पी"]},
    {"name": "हस्त", "letters": ["पू", "ष", "ण", "ठा"]},
    {"name": "चित्रा", "letters": ["पे", "पो", "रा", "री"]},
    {"name": "स्वाति", "letters": ["रू", "रे", "रो", "ता"]},
    {"name": "विशाखा", "letters": ["ती", "तू", "ते", "तो"]},
    {"name": "अनुराधा", "letters": ["ना", "नी", "नू", "ने"]},
    {"name": "ज्येष्ठा", "letters": ["नो", "या", "यी", "यू"]},
    {"name": "मूल", "letters": ["ये", "यो", "भा", "भी"]},
    {"name": "पूर्वाषाढ़ा", "letters": ["भू", "धा", "फा", "ढा"]},
    {"name": "उत्तराषाढ़ा", "letters": ["भे", "भो", "जा", "जी"]},
    {"name": "श्रवण", "letters": ["खी", "खू", "खे", "खो"]},
    {"name": "धनिष्ठा", "letters": ["गा", "गी", "गु", "गे"]},
    {"name": "शतभिषा", "letters": ["गो", "सा", "सी", "सू"]},
    {"name": "पूर्वाभाद्रपद", "letters": ["से", "सो", "दा", "दी"]},
    {"name": "उत्तराभाद्रपद", "letters": ["दू", "थ", "झ", "ञ"]},
    {"name": "रेवती", "letters": ["दे", "दो", "चा", "ची"]}
]

CITY_COORDINATES = {
    "gondia": {"lat": 21.4600, "lon": 80.1960, "name": "Gondia"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "name": "Nagpur"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "name": "Pune"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "name": "Delhi"},
    "raipur": {"lat": 21.2514, "lon": 81.6296, "name": "Raipur"}
}

def calculate_julian_day(year, month, day, hour, minute, tz_offset=5.5):
    utc_hours = hour + (minute / 60.0) - tz_offset
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    jd += utc_hours / 24.0
    return jd

def get_kundli_details(year, month, day, hour, minute, city="gondia", tz_offset=5.5):
    city_key = city.lower().strip()
    coords = CITY_COORDINATES.get(city_key, {"lat": 21.4600, "lon": 80.1960, "name": city.capitalize()})
    jd = calculate_julian_day(year, month, day, hour, minute, tz_offset)

    T = (jd - 2451545.0) / 36525.0
    rad = math.radians
    deg = math.degrees

    # Lahiri Ayanamsha
    ayanamsha = 23.85 + (T * 100 * 50.29 / 3600.0)

    # 1. Sun
    L0_s = 280.46646 + 36000.76983 * T
    M_s = 357.52911 + 35999.05029 * T
    sun_sid = ((L0_s + 1.914602 * math.sin(rad(M_s))) - ayanamsha) % 360.0

    # 2. Moon
    L0_m = 218.3164477 + 481267.88123421 * T
    M_m = 134.9633964 + 477198.8675055 * T
    D_m = 297.8501921 + 445267.1114034 * T
    moon_sid = ((L0_m + 6.288774 * math.sin(rad(M_m)) + 1.274027 * math.sin(rad(2 * D_m - M_m))) - ayanamsha) % 360.0

    # 3. Tara Graha (Vedic sidereal mapping)
    mars_sid = ((355.43 + 19140.30 * T) - ayanamsha) % 360.0
    mercury_sid = ((sun_sid + 12.0 * math.sin(rad(M_s + 45)))) % 360.0
    jupiter_sid = ((34.35 + 3034.90 * T) - ayanamsha) % 360.0
    venus_sid = ((sun_sid + 20.0 * math.cos(rad(M_s + 80)))) % 360.0
    saturn_sid = ((50.07 + 1222.11 * T) - ayanamsha) % 360.0

    # 4. Chhaya Graha (Rahu & Ketu)
    rahu_sid = ((125.04452 - 1934.136261 * T) - ayanamsha) % 360.0
    ketu_sid = (rahu_sid + 180.0) % 360.0

    # 5. Lagna
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360.0
    lst = (gmst + coords["lon"]) % 360.0
    eps = 23.4392911 - 0.0130042 * T
    y = -math.cos(rad(lst))
    x = math.sin(rad(lst)) * math.cos(rad(eps)) + math.tan(rad(coords["lat"])) * math.sin(rad(eps))
    lagna_sid = (deg(math.atan2(y, x)) - ayanamsha) % 360.0

    lagna_rashi_idx = int(lagna_sid // 30)
    moon_rashi_idx = int(moon_sid // 30)

    # Planets List with Devanagari Tags
    planets_data = [
        {"name": "सू", "deg": sun_sid},
        {"name": "चं", "deg": moon_sid},
        {"name": "मं", "deg": mars_sid},
        {"name": "बु", "deg": mercury_sid},
        {"name": "गु", "deg": jupiter_sid},
        {"name": "शु", "deg": venus_sid},
        {"name": "श", "deg": saturn_sid},
        {"name": "रा", "deg": rahu_sid},
        {"name": "के", "deg": ketu_sid}
    ]

    # Map Planets to 12 Houses
    houses_planets = {str(i): [] for i in range(1, 13)}
    for p in planets_data:
        p_rashi_idx = int(p["deg"] // 30)
        house_num = ((p_rashi_idx - lagna_rashi_idx) % 12) + 1
        houses_planets[str(house_num)].append(p["name"])

    # Nakshatra
    nakshatra_span = 360.0 / 27.0
    nakshatra_idx = int(moon_sid // nakshatra_span)
    pada_span = nakshatra_span / 4.0
    deg_in_nakshatra = moon_sid % nakshatra_span
    pada_idx = int(deg_in_nakshatra // pada_span)

    return {
        "place": coords["name"],
        "rashi_hindi": RASHIS[moon_rashi_idx]["hindi"],
        "rashi_english": RASHIS[moon_rashi_idx]["english"],
        "lagna_hindi": RASHIS[lagna_rashi_idx]["hindi"],
        "lagna_english": RASHIS[lagna_rashi_idx]["english"],
        "lagna_rashi_num": lagna_rashi_idx + 1,
        "nakshatra_hindi": NAKSHATRA_DATA[nakshatra_idx]["name"],
        "charan": pada_idx + 1,
        "naam_akshar_hindi": NAKSHATRA_DATA[nakshatra_idx]["letters"][pada_idx],
        "houses_planets": houses_planets
    }

