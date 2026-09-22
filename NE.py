import random

# Base Shastriya Suffixes for Boy Names (Devata, Swaroop & Mahatva)
UNIVERSAL_SUFFIXES_BOY = [
    ("ेश", "esh", "का सर्वोपरि अधिपति व स्वामी", "नेतृत्व एवं समाज में प्रतिष्ठा"),
    ("इन्द्र", "indra", "का श्रेष्ठ नायक व रक्षक", "विजय एवं पराक्रम"),
    ("देव", "dev", "का पावन दिव्य स्वरूप", "सात्विक विचार एवं ईश्वरीय कृपा"),
    ("राज", "raj", "का चक्रवर्ती तेजस्वी राजा", "यश, मान एवं कीर्ति"),
    ("कांत", "kant", "की चंद्रमा जैसी पावन कांति", "सौम्य वाणी एवं आकर्षण"),
    ("अंशु", "anshu", "की प्रकाशमान आलोकित किरण", "सकारात्मक जीवन एवं आरोग्यता"),
    ("नाथ", "nath", "का पालक व पोषक", "कर्तव्यपरायणता एवं दयाभाव"),
    ("वर्धन", "vardhan", "की वृद्धि करने वाला तेजस्वी", "उन्नति एवं कुल की समृद्धि"),
    ("तेजस", "tejas", "का अखंड ऊर्जावान तेज", "आत्मबल एवं पराक्रम"),
    ("पाल", "pal", "का धर्मनिष्ठ रक्षक", "धार्मिक निष्ठा एवं सुरक्षा"),
    ("दीप", "deep", "का पावन प्रकाश पुंज", "कुल का नाम रोशन करने वाला"),
    ("दत्त", "datta", "ईश्वर का अनमोल उपहार", "भगवद् कृपा एवं सौभाग्य")
]

# Base Shastriya Suffixes for Girl Names (Devi, Kalyankari & Pavani Bhav)
UNIVERSAL_SUFFIXES_GIRL = [
    ("िका", "ika", "सृष्टिकर्ता की सुकोमल व कलात्मक मूरत", "कला, विद्या एवं अद्वितीय रचनात्मकता"),
    ("मयी", "mayi", "आनंद और शांति से परिपूर्ण साक्षात देवी", "समस्त सद्गुणों का वास"),
    ("प्रिया", "priya", "परमात्मा एवं सबकी अत्यंत लाडली", "पारिवारिक प्रेम एवं आदर"),
    ("नन्दिनी", "nandini", "आनंद और खुशियां बिखेरने वाली", "घर-आंगन में सदा उल्लास"),
    ("कांति", "kanti", "की मनोहर पावन आभा", "सौंदर्य, शालीनता एवं आकर्षण"),
    ("दा", "da", "कल्याण एवं शुभ फल प्रदान करने वाली", "सुख और समृद्धि की दात्री"),
    ("वती", "vati", "सद्गुणों से अलंकृत विदुषी", "ज्ञान, विवेक एवं संस्कार"),
    ("सुन्दरी", "sundari", "अत्यंत मनभावन व पवित्र", "निर्मल हृदय एवं सौम्यता"),
    ("धारिणी", "dharini", "संस्कारों को संजोने वाली", "मर्यादा एवं आत्मबल")
]

# Specific Known High-Vedic Roots for Specific Alphabets
SPECIAL_LEXICON = {
    "ख": {
        "Boy": [
            ("खगेश", "Khagesh", "गरुड़ देव, आकाश का स्वामी", "तीव्र बुद्धि एवं विजय"),
            ("खगेन्द्र", "Khagendra", "भगवान विष्णु के वाहन गरुड़", "अपार बल एवं पराक्रम"),
            ("खंजन", "Khanjan", "सुंदर चंचल नयनों वाला पक्षी", "उत्साह एवं प्रसन्नता"),
            ("ख्यात", "Khyat", "संसार में प्रसिद्ध एवं सम्मानित", "उच्च कीर्ति एवं यश"),
            ("खद्योत", "Khadyot", "आकाश का प्रकाश, सूर्य देव", "अखंड प्रकाश एवं तेज"),
            ("खग", "Khag", "आकाश में स्वतंत्र विचरण करने वाला", "स्वतंत्र विचार एवं उच्च लक्ष्य"),
            ("खलेश", "Khalesh", "समस्त सिद्धियों का स्वामी", "आत्मज्ञान एवं बल"),
            ("खिरोद", "Khirod", "क्षीर सागर, पावन अमृतमय", "शांत चित्त एवं आरोग्यता")
        ],
        "Girl": [
            ("ख्याति", "Khyati", "सद्कर्मों से अर्जित पवित्र कीर्ति", "समाज में आदर एवं मान"),
            ("खंजनिका", "Khanjanika", "चंचल व मनोहर भाव वाली", "सदा प्रसन्न रहने का वरदान"),
            ("खगेशा", "Khagesha", "आकाश स्वरूपा, माँ सरस्वती", "विद्या एवं ज्ञान की देवी"),
            ("खिला", "Khila", "प्रफुल्लित पुष्प कली", "स्नेहमयी एवं कोमल स्वभाव"),
            ("खीराब्धि", "Kheerabdhi", "अमृतमयी क्षीर सागर की देवी", "गृह-लक्ष्मी एवं शांति"),
            ("खगवती", "Khagavati", "उच्च गगनगामी चेतना", "उन्नत विचार एवं एकाग्रता")
        ]
    }
}

SEEN_NAMES = set()

def clean_letter(hindi_syllable: str) -> str:
    matras = ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः']
    clean = hindi_syllable
    for m in matras:
        clean = clean.replace(m, '')
    return clean.strip()

def generate_ai_names(hindi_letter: str, gender: str = "All", mode: str = "strict"):
    global SEEN_NAMES
    root = clean_letter(hindi_letter)
    target_prefix = hindi_letter if mode == "strict" else root

    pool_boys = []
    pool_girls = []

    # 1. Check if special curated root exists
    if root in SPECIAL_LEXICON:
        for b_name, b_en, b_mean, b_sig in SPECIAL_LEXICON[root].get("Boy", []):
            if mode == "strict" and not b_name.startswith(hindi_letter):
                continue
            pool_boys.append({
                "name_hi": b_name, "name_en": b_en, "gender": "Boy",
                "meaning": b_mean, "significance": b_sig
            })
        for g_name, g_en, g_mean, g_sig in SPECIAL_LEXICON[root].get("Girl", []):
            if mode == "strict" and not g_name.startswith(hindi_letter):
                continue
            pool_girls.append({
                "name_hi": g_name, "name_en": g_en, "gender": "Girl",
                "meaning": g_mean, "significance": g_sig
            })

    # 2. Dynamic Algorithmic Synthesis for ANY Alphabet (क, ख, खी, ग, घ, etc.)
    # Synthesize dynamically so no letter ever fails
    for s_hi, s_en, s_mean, s_sig in UNIVERSAL_SUFFIXES_BOY:
        # Proper vowel sandhi
        if s_hi.startswith("े") or s_hi.startswith("इ"):
            syn_name = f"{root}{s_hi}"
        else:
            syn_name = f"{target_prefix}{s_hi}"
            
        syn_mean = f"'{target_prefix}' अक्षर जनित: {s_mean}"
        pool_boys.append({
            "name_hi": syn_name,
            "name_en": f"{target_prefix}-{s_en}",
            "gender": "Boy",
            "meaning": syn_mean,
            "significance": s_sig
        })

    for s_hi, s_en, s_mean, s_sig in UNIVERSAL_SUFFIXES_GIRL:
        if s_hi.startswith("ि"):
            syn_name = f"{root}{s_hi}"
        else:
            syn_name = f"{target_prefix}{s_hi}"
            
        syn_mean = f"'{target_prefix}' स्वर जनित: {s_mean}"
        pool_girls.append({
            "name_hi": syn_name,
            "name_en": f"{target_prefix}-{s_en}",
            "gender": "Girl",
            "meaning": syn_mean,
            "significance": s_sig
        })

    # Filter unseen
    avail_b = [x for x in pool_boys if x["name_hi"] not in SEEN_NAMES]
    avail_g = [x for x in pool_girls if x["name_hi"] not in SEEN_NAMES]

    if len(avail_b) < 6:
        avail_b = pool_boys
        SEEN_NAMES.clear()
    if len(avail_g) < 6:
        avail_g = pool_girls
        SEEN_NAMES.clear()

    random.shuffle(avail_b)
    random.shuffle(avail_g)

    results = []
    if gender in ["Boy", "All"]:
        count = 3 if gender == "All" else 6
        for item in avail_b[:count]:
            SEEN_NAMES.add(item["name_hi"])
            results.append(item)

    if gender in ["Girl", "All"]:
        count = 3 if gender == "All" else 6
        for item in avail_g[:count]:
            SEEN_NAMES.add(item["name_hi"])
            results.append(item)

    random.shuffle(results)
    return results
