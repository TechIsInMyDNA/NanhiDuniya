import random

# Track displayed names in memory to prevent immediate repetitions
SEEN_NAMES = set()

# 1. BEHIND-THE-NAME MODEL: Verified Classical Vedic/Puranic Reservoir
VERIFIED_SHASTRIYA_REGISTRY = {
    "तू": {
        "Boy": [
            ("तुषार", "Tushar", "शीतल पावन हिम कण, निर्मल चित्त", "शांति एवं शुचिता"),
            ("तुष्यदेव", "Tushyadev", "सदा संतुष्ट व प्रसन्न रहने वाले देव", "आत्मसंतुष्टि एवं सद्बुद्धि"),
            ("तुल्य", "Tulya", "अतुलनीय, समदर्शी एवं न्यायप्रिय", "समानता एवं विवेक"),
            ("तुहिन", "Tuhin", "निर्मल पावन ओस की बूंद", "शीतलता एवं पावनता"),
            ("तुंगेश", "Tungesh", "सर्वोच्च शिखर के अधिपति, भगवान शिव", "उच्च विचार एवं पराक्रम"),
            ("तुंगिश", "Tungish", "तेजस्वी एवं उच्च ध्येय वाले", "नेतृत्व एवं अडिग संकल्प"),
            ("तुषारकांत", "Tusharkant", "चंद्रमा जैसी शीतल धवल कांति", "आकर्षण एवं सौम्य तेज"),
            ("तुषित", "Tushit", "परम आनंदित, तृप्त एवं मोक्षगामी", "सदा प्रसन्नचित्त स्वभाव"),
            ("तूर्य", "Toorya", "विजय का पावन वाद्य एवं शंखघोष", "विजय, उत्साह एवं स्फूर्ति"),
            ("तुल्यांश", "Tulyansh", "समता एवं न्याय का पावन अंश", "सद्भावना एवं धर्म"),
            ("तुंगनाथ", "Tungnath", "हिमालय के सर्वोच्च शिव स्वरूप", "तपोबल एवं शुचिता"),
            ("तुहिनकर", "Tuhinkar", "शीतल किरणें बिखेरने वाला चंद्रमा", "शांत चित्त एवं शीतलता"),
            ("तुष्टिद", "Tushtid", "आनंद एवं संतोष प्रदान करने वाला", "परोपकार एवं दया"),
            ("तुंगधर", "Tungdhar", "महानता एवं गरिमा को धारण करने वाला", "दृढ़ता एवं सम्मान")
        ],
        "Girl": [
            ("तुष्टि", "Tushti", "साक्षात माँ लक्ष्मी का संतोष स्वरूप", "पारिवारिक शांति एवं समृद्धि"),
            ("तुलसी", "Tulsi", "परम पावन, पूजनीय एवं आरोग्यदायिनी वृंदा", "भक्ति, शुचिता एवं सौभाग्य"),
            ("तुषिता", "Tushita", "सदा तृप्त, संतुष्ट एवं आनंदमयी", "सद्भाव एवं मधुर स्वभाव"),
            ("तुहिनिका", "Tuhinika", "निर्मल पावन हिम कणिका", "कोमलता, सौंदर्य एवं सादगी"),
            ("तुंगिशा", "Tungisha", "सर्वोच्च शिखर स्वरूपा माँ पार्वती", "शक्ति, गरिमा एवं तेज"),
            ("तुलिका", "Tulika", "सृजन करने वाली कलामयी तूलिका", "रचनात्मकता एवं प्रज्ञा"),
            ("तुषारिका", "Tusharika", "पावन हिमपात की कोमल बूंद", "शालीनता एवं निष्पाप चित्त"),
            ("तुष्टिदा", "Tushtida", "संतोष एवं सुख देने वाली देवी", "करुणा एवं वात्सल्य"),
            ("तुल्या", "Tulya", "अद्वितीय एवं समदर्शी कन्या", "न्यायप्रियता एवं विवेक"),
            ("तूर्या", "Toorya", "दिव्य विजय का उद्घोष", "ऊर्जा एवं कीर्ति"),
            ("तुहिनश्री", "Tuhinshree", "हिम जैसी धवल एवं पावन कांति", "सौंदर्य एवं सात्विकता"),
            ("तुलसीप्रिया", "Tulsipriya", "भगवान नारायण की परम प्रिय", "अनन्य भक्ति एवं शुचिता")
        ]
    },
    "त": {
        "Boy": [
            ("तन्मय", "Tanmay", "ईश्वर भक्ति एवं ध्यान में एकाग्र", "ध्यान, स्थिरता एवं समर्पण"),
            ("तन्वीश", "Tanveesh", "समस्त सिद्धियों के स्वामी", "पराक्रम एवं ऐश्वर्य"),
            ("तेजस", "Tejas", "सूर्य सदृश दिव्य आभा एवं तेज", "आत्मबल एवं ओज"),
            ("तरण", "Taran", "भवसागर से पार कराने वाला, रक्षक", "मुक्तिदाता एवं शक्ति"),
            ("तपोमय", "Tapomay", "तपस्या एवं साधना से परिपूर्ण", "तपोबल एवं संयम"),
            ("तोषान", "Toshan", "सदा प्रसन्नचित्त एवं आनंदित", "उल्लास एवं संतुष्टि"),
            ("तारांक", "Tarank", "आकाश का पावन ध्रुवतारा", "मार्गदर्शन एवं स्थिरता"),
            ("तेजोमय", "Tejomay", "साक्षात प्रकाश स्वरूप", "सकारात्मक ऊर्जा एवं यश"),
            ("त्रिविक्रम", "Trivikram", "तीनों लोकों को नापने वाले वामन भगवान", "असीमित सामर्थ्य एवं विजय"),
            ("तीर्थेश", "Teerthesh", "समस्त पावन तीर्थों के अधिपति", "आध्यात्मिक ज्ञान एवं शुचिता"),
            ("तोमर", "Tomar", "अजेय योद्धा एवं मर्यादा रक्षक", "साहस एवं दृढ़ता"),
            ("तन्वीर", "Tanveer", "प्रबुद्ध, ज्ञानी एवं तेजस्वी", "बुद्धिमत्ता एवं पराक्रम")
        ],
        "Girl": [
            ("तन्वी", "Tanvi", "सुकोमल, सौम्य एवं शालीन", "संस्कार, लालित्य एवं सौम्यता"),
            ("तनिष्का", "Tanishka", "स्वर्ण जैसी पावन व देदीप्यमान", "समृद्धि, सौभाग्य एवं यश"),
            ("तृषा", "Trisha", "ज्ञान एवं भक्ति की पावन अभीप्सा", "जिज्ञासा एवं सकारात्मकता"),
            ("तरंगिणी", "Tarangini", "पवित्र एवं अविरल बहती नदी", "ऊर्जा, गतिशीलता एवं जीवन"),
            ("तारा", "Tara", "आकाश की पावन देवी, मुक्तिदायिनी", "दिव्य आलोक एवं रक्षा"),
            ("तन्मयी", "Tanmayi", "भगवद् चिंतन में तल्लीन", "भक्ति, निष्ठा एवं एकाग्रता"),
            ("तोषिका", "Toshika", "सदा प्रसन्नचित्त रहने वाली", "आनंद, माधुर्य एवं सौहार्द"),
            ("तेजस्वी", "Tejaswi", "आत्मतेज एवं ज्ञान से संपन्न", "प्रतिभा, गरिमा एवं आभा"),
            ("तपस्या", "Tapasya", "निष्ठा एवं साधना की प्रतिमूर्ति", "धैर्य, लगन एवं आत्मबल"),
            ("तीर्था", "Teertha", "पावन तीर्थ स्थल स्वरूपा", "पवित्रता एवं कल्याण")
        ]
    }
}

# 2. FANTASY-NAME-GENERATOR MODEL: Combinatorial Mathematical Array System
EXPANSION_ROOTS = {
    "तू": [
        ("तुषार", "Tushar", "शीतल पावन हिम"),
        ("तुंग", "Tung", "सर्वोच्च उन्नत शिखर"),
        ("तुल्य", "Tulya", "समदर्शी एवं अद्वितीय"),
        ("तुहिन", "Tuhin", "निर्मल पावन ओस कण"),
        ("तुष्ट", "Tusht", "सदा संतुष्ट एवं तृप्त"),
        ("तूर्य", "Toorya", "विजय वाद्य एवं शंख"),
        ("तूर्ण", "Toorna", "तीव्र बुद्धि एवं स्फूर्ति"),
        ("तूल", "Tool", "कपास सदृश निष्पाप कोमल")
    ],
    "त": [
        ("तन्म", "Tanm", "एकाग्रचित्त एवं समर्पित"),
        ("तेज", "Tej", "सूर्य सदृश दिव्य तेज"),
        ("तप", "Tap", "तपस्या एवं आत्मबल"),
        ("तर", "Tar", "भवसागर से तारने वाला"),
        ("तोष", "Tosh", "उल्लास एवं संतोष"),
        ("तार", "Tar", "ध्रुवतारा सदृश मार्गदर्शक"),
        ("तीर्थ", "Teerth", "पवित्र पावन तीर्थ"),
        ("त्रिलोक", "Trilok", "तीनों लोकों के ज्ञाता")
    ],
    "अ": [
        ("अनंत", "Anant", "अविनाशी एवं असीम"),
        ("अद्वैत", "Advait", "अद्वितीय ब्रह्म स्वरूप"),
        ("अयान", "Ayaan", "सूर्य का दिव्य तेज"),
        ("अगस्त्य", "Agastya", "ऋषि तुल्य ज्ञान"),
        ("अथर्व", "Atharva", "वेद ज्ञाता एवं प्रज्ञा")
    ],
    "क": [
        ("कवि", "Kavi", "काव्य एवं प्रज्ञा"),
        ("केशव", "Keshav", "भगवान श्रीकृष्ण स्वरूप"),
        ("कुश", "Kush", "पराक्रमी एवं कुलीन"),
        ("कार्तिक", "Kartik", "साहस एवं नेतृत्व")
    ],
    "श": [
        ("शिव", "Shiv", "कल्याणकारी एवं शांत"),
        ("शौर्य", "Shaurya", "अदम्य वीरता एवं मान"),
        ("शुभ", "Shubh", "मंगलकारी एवं पवित्र"),
        ("शौनक", "Shaunak", "महान वैदिक ऋषि")
    ]
}

BOY_ENDINGS = [
    ("ेश", "esh", "के परम स्वामी", "नेतृत्व एवं ऐश्वर्य"),
    ("इंद्र", "indra", "में सर्वश्रेष्ठ", "पराक्रम एवं प्रतिष्ठा"),
    ("अंश", "ansh", "का पावन अंश", "दिव्यता एवं शुचिता"),
    ("देव", "dev", "स्वरूप एवं पूजनीय", "सदाचार एवं विवेक"),
    ("राज", "raj", "सम्राट एवं मार्गदर्शक", "गरिमा एवं मान"),
    ("कांत", "kant", "अत्यंत प्रिय", "सौम्य आकर्षण"),
    ("पाल", "pal", "के मर्यादा रक्षक", "सुरक्षा एवं धर्म"),
    ("मय", "may", "से परिपूर्ण", "सकारात्मक ऊर्जा"),
    ("वर्धन", "vardhan", "की उन्नति करने वाले", "विकास एवं यश"),
    ("दीप", "deep", "का प्रकाश फैलाने वाले", "ज्ञान का आलोक"),
    ("धर", "dhar", "को धारण करने वाले", "धैर्य एवं शक्ति"),
    ("वर", "var", "सर्वश्रेष्ठ एवं अनुपम", "कुलीनता एवं मान"),
    ("आनंद", "anand", "के परमानंद स्वरूप", "हर्ष एवं शांति"),
    ("नाथ", "nath", "के पालक", "करुणा एवं आश्रय")
]

GIRL_ENDINGS = [
    ("ा", "a", "पावन स्वरूपा", "शालीनता एवं सौम्यता"),
    ("ी", "i", "सौभाग्यशालिनी", "समृद्धि एवं शुचिता"),
    ("िका", "ika", "अत्यंत प्रिय व सुंदर", "माधुर्य एवं लालित्य"),
    ("िता", "ita", "अलंकृत एवं संपन्न", "संस्कार एवं प्रतिष्ठा"),
    ("्या", "ya", "सर्वदा पूजनीय", "भक्ति एवं आदर"),
    ("वती", "vati", "सद्गुणों से संपन्न", "धैर्य एवं विवेक"),
    ("मयी", "mayi", "स्नेह से परिपूर्ण", "वात्सल्य एवं दया"),
    ("प्रिया", "priya", "सबकी अत्यंत लाडली", "आत्मीयता एवं प्रेम"),
    ("श्री", "shree", "समृद्धि एवं सौभाग्य", "महालक्ष्मी का अनुग्रह"),
    ("नंदिनी", "nandini", "आनंद देने वाली", "पारिवारिक उल्लास")
]

def clean_syllable(s):
    for m in ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः']:
        s = s.replace(m, '')
    return s.strip()

def sanskrit_join(r_hi, r_en, s_hi, s_en):
    # Perfect unicode joining without broken halant
    clean_h = r_hi[:-1] if r_hi.endswith('्') else r_hi
    if s_hi == "ेश": name_h = clean_h + "ेश"
    elif s_hi == "इंद्र": name_h = clean_h + "ेंद्र"
    elif s_hi == "अंश": name_h = clean_h + "ांश" if not clean_h.endswith(('ा', 'ि', 'ी', 'ु', 'ू')) else clean_h + "ंश"
    elif s_hi == "आनंद": name_h = clean_h + "ानंद"
    elif s_hi in ["ा", "ी", "िका", "िता", "्या"]:
        name_h = clean_h + s_hi if not clean_h.endswith(('ा', 'ि', 'ी', 'ु', 'ू')) else clean_h
    else:
        name_h = clean_h + s_hi

    clean_e = r_en.rstrip('a').rstrip('h')
    if s_en.startswith(('a', 'e', 'i', 'o', 'u')):
        name_e = (clean_e + s_en).title()
    else:
        name_e = (r_en + s_en).title()

    return name_h, name_e

def generate_ai_names(letter, gender="All", mode="strict"):
    global SEEN_NAMES
    base_char = clean_syllable(letter)
    
    # Reset seen cache if it grows excessively
    if len(SEEN_NAMES) > 1000:
        SEEN_NAMES.clear()

    curated_pool = []

    # 1. Fetch from Verified Classical Registry
    target_bucket = None
    if mode == "strict" and letter in VERIFIED_SHASTRIYA_REGISTRY:
        target_bucket = VERIFIED_SHASTRIYA_REGISTRY[letter]
    elif base_char in VERIFIED_SHASTRIYA_REGISTRY:
        target_bucket = VERIFIED_SHASTRIYA_REGISTRY[base_char]

    if target_bucket:
        if gender in ["Boy", "All"]:
            for b in target_bucket.get("Boy", []):
                curated_pool.append({"name_hi": b[0], "name_en": b[1], "gender": "Boy", "meaning": b[2], "significance": b[3]})
        if gender in ["Girl", "All"]:
            for g in target_bucket.get("Girl", []):
                curated_pool.append({"name_hi": g[0], "name_en": g[1], "gender": "Girl", "meaning": g[2], "significance": g[3]})

    # 2. Expand via Combinatorial Grammar Arrays
    roots = EXPANSION_ROOTS.get(letter if mode == "strict" else base_char) or EXPANSION_ROOTS.get("त")
    for r_hi, r_en, r_mean in roots:
        if gender in ["Boy", "All"]:
            for s_hi, s_en, s_mean, sig in BOY_ENDINGS:
                nh, ne = sanskrit_join(r_hi, r_en, s_hi, s_en)
                curated_pool.append({
                    "name_hi": nh,
                    "name_en": ne,
                    "gender": "Boy",
                    "meaning": f"{r_mean}, {s_mean}",
                    "significance": sig
                })
        if gender in ["Girl", "All"]:
            for s_hi, s_en, s_mean, sig in GIRL_ENDINGS:
                nh, ne = sanskrit_join(r_hi, r_en, s_hi, s_en)
                curated_pool.append({
                    "name_hi": nh,
                    "name_en": ne,
                    "gender": "Girl",
                    "meaning": f"{r_mean}, {s_mean}",
                    "significance": sig
                })

    # Filter out already seen names to guarantee fresh results on every click
    fresh_candidates = [n for n in curated_pool if n["name_hi"] not in SEEN_NAMES]

    # If pool is exhausted, clear seen and cycle
    if len(fresh_candidates) < 12:
        SEEN_NAMES.clear()
        fresh_candidates = curated_pool

    random.shuffle(fresh_candidates)
    batch = fresh_candidates[:12]

    # Mark as seen
    for item in batch:
        SEEN_NAMES.add(item["name_hi"])

    return batch
