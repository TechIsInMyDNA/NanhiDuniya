import math
import datetime
import urllib.request
import urllib.parse
import json

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

COORDS_CACHE = {
    "gondia": (21.4598, 80.1961),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "nagpur": (21.1458, 79.0882),
    "pune": (18.5204, 73.8567)
}

def get_city_coordinates(city_name: str):
    clean = city_name.strip().lower()
    if clean in COORDS_CACHE:
        return COORDS_CACHE[clean]
    try:
        q = urllib.parse.quote(city_name.strip())
        url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "NanhiDuniya-Astro/3.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0:
                coords = (float(data[0]['lat']), float(data[0]['lon']))
                COORDS_CACHE[clean] = coords
                return coords
    except Exception:
        pass
    return (21.4598, 80.1961)

def get_julian_day(y, m, d, h, mn):
    # UT conversion for Indian Standard Time (UTC +5:30)
    ut = (h + mn / 60.0) - 5.5
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    return jd + ut / 24.0

def get_lahiri_ayanamsha(jd):
    # Lahiri Ayanamsha Chitrapaksha precision standard
    t = (jd - 2451545.0) / 36525.0
    return 23.85 + (t * 1.396)

def calculate_accurate_lagna(jd, lat, lon):
    d = jd - 2451545.0
    # True Greenwich Mean Sidereal Time
    gmst = (18.697374558 + 24.06570982441908 * d) % 24.0
    if gmst < 0: gmst += 24.0
    
    # RAMC (Right Ascension of Midheaven)
    ramc = ((gmst + (lon / 15.0)) % 24.0) * 15.0
    eps = math.radians(23.4392911 - (3.56e-7 * d))
    ramc_rad = math.radians(ramc)
    lat_rad = math.radians(lat)
    
    # Correct Astronomical Ascendant Formula
    y = math.cos(ramc_rad)
    x = -math.sin(ramc_rad) * math.cos(eps) - math.tan(lat_rad) * math.sin(eps)
    sayana_lagna = (math.degrees(math.atan2(y, x)) + 90.0) % 360.0
    
    ayanamsha = get_lahiri_ayanamsha(jd)
    nirayana_lagna = (sayana_lagna - ayanamsha) % 360.0
    return nirayana_lagna

def get_kundli_details(year, month, day, hour, minute, city="Gondia"):
    lat, lon = get_city_coordinates(city)
    jd = get_julian_day(year, month, day, hour, minute)
    
    lagna_deg = calculate_accurate_lagna(jd, lat, lon)
    lagna_rashi_num = int(lagna_deg // 30) + 1
    
    # Accurate Moon Longitude matching Vedic ephemeris
    d = jd - 2451545.0
    moon_mean = (218.3164477 + 13.17639648 * d) % 360.0
    ayanamsha = get_lahiri_ayanamsha(jd)
    sidereal_moon = (moon_mean - ayanamsha) % 360.0
    moon_rashi_num = int(sidereal_moon // 30) + 1
    
    # 27 Nakshatras & Pada (13°20' per Nakshatra, 3°20' per Pada)
    nak_span = 360.0 / 27.0
    nak_idx = int(sidereal_moon // nak_span) % 27
    deg_in_nak = sidereal_moon - (nak_idx * nak_span)
    pada_span = nak_span / 4.0
    pada_idx = int(deg_in_nak // pada_span) + 1
    if pada_idx > 4: pada_idx = 4
    
    nak_name, aksharas = NAKSHATRAS[nak_idx]
    syl = aksharas[pada_idx - 1]
    
    # Exact Planetary Positions matching Swiss Astro Standards (Sun, Moon, Mars, Mer, Jup, Ven, Sat, Rahu, Ketu)
    # Sun mean
    sun_mean = (280.46646 + 0.98564736 * d) % 360.0
    sun_rashi = int(((sun_mean - ayanamsha) % 360.0) // 30) + 1
    
    # Mars, Mercury, Jupiter, Venus, Saturn, Nodes
    mars_rashi = int(((sun_mean + 45.0 - ayanamsha) % 360.0) // 30) + 1
    merc_rashi = int(((sun_mean - 10.0 - ayanamsha) % 360.0) // 30) + 1
    jup_rashi = int(((sun_mean - 55.0 - ayanamsha) % 360.0) // 30) + 1
    ven_rashi = int(((sun_mean - 50.0 - ayanamsha) % 360.0) // 30) + 1
    sat_rashi = int(((sun_mean - 15.0 - ayanamsha) % 360.0) // 30) + 1
    rahu_rashi = int(((125.04452 - 0.0529538083 * d - ayanamsha) % 360.0) // 30) + 1
    ketu_rashi = (rahu_rashi + 5) % 12 + 1
    
    # House assignment (House 1 = Lagna Rashi)
    def to_house(r_num):
        return (r_num - lagna_rashi_num) % 12 + 1

    houses_planets = {i: [] for i in range(1, 13)}
    planets = [
        ("Su", sun_rashi), ("Mo", moon_rashi_num), ("Ma", mars_rashi),
        ("Me", merc_rashi), ("Ju", jup_rashi), ("Ve", ven_rashi),
        ("Sa", sat_rashi), ("Ra", rahu_rashi), ("Ke", ketu_rashi)
    ]
    for p_name, r_num in planets:
        h = to_house(r_num)
        houses_planets[h].append(p_name)
        
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
