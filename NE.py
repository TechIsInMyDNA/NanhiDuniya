import random

# Sanskrit Dhatu Roots & Divine Attributes mapped by phonetic vargas
PHONETIC_ROOTS = {
    "त": {
        "m_roots": [
            ("तन्", "Tan", "विस्तार, निरंतरता एवं वंश वृद्धि", "चिरंतन विकास"),
            ("तुष्", "Tush", "परम संतोष, प्रसन्नता एवं तृप्ति", "आत्मसंतुष्टि"),
            ("तेज्", "Tej", "सूर्य तुल्य प्रकाश, ओज एवं पराक्रम", "अदम्य तेज"),
            ("तप्", "Tap", "तपस्या, साधना एवं आत्मबल", "तपोबल"),
            ("तर्", "Tar", "भवसागर से पार कराने वाला, रक्षक", "मुक्तिदाता"),
            ("तोष्", "Tosh", "आनंद, उल्लास एवं तुष्टि", "सदा प्रसन्न"),
            ("तार", "Tar", "ध्रुवतारा, उच्च मार्गदर्शन", "दृढ़ संकल्प"),
            ("तुहिन्", "Tuhin", "निर्मल पावन हिम, शांति", "पवित्र चित्त"),
            ("तीर्थ्", "Teerth", "पवित्र पावन धाम, शुचिता", "आध्यात्मिक आभा"),
            ("त्रि", "Tri", "त्रिलोकीनाथ, तीन कालों के ज्ञाता", "दूरदर्शिता")
        ],
        "f_roots": [
            ("तन्", "Tan", "सुकुमारता, लालित्य एवं संस्कार", "सौम्य स्वरूप"),
            ("तनिष्", "Tanish", "स्वर्णमयी कांति, उज्ज्वल आभा", "सौभाग्य एवं समृद्धि"),
            ("तृष्", "Trish", "ज्ञान एवं भक्ति की पावन पिपासा", "सकारात्मक दृष्टिकोण"),
            ("तुष्", "Tush", "साक्षात लक्ष्मी स्वरूपा संतुष्टि", "पारिवारिक शांति"),
            ("तरं", "Tarang", "अविरल बहती पावन सरिता", "ऊर्जा एवं गतिशीलता"),
            ("तारा", "Tara", "आकाश की पावन देवी, मार्गदर्शक", "दिव्य आलोक"),
            ("तोषि", "Toshi", "सदा प्रसन्नचित्त एवं स्नेहमयी", "मधुर स्वभाव"),
            ("तुल", "Tul", "अतुलनीय पावन तुलसी, शुचिता", "आरोग्य एवं भक्ति"),
            ("तेजस्", "Tejas", "ज्ञान का आलोक एवं तेजस्विता", "प्रतिभा एवं गरिमा"),
            ("तन्वी", "Tanvi", "अत्यंत सुकोमल एवं शालीन", "संस्कार एवं लालित्य")
        ]
    },
    "ख": {
        "m_roots": [
            ("खग्", "Khag", "आकाशगामी, गरुड़ देव", "उच्च लक्ष्य एवं विजय"),
            ("ख्यात्", "Khyat", "संसार में प्रसिद्ध एवं सम्मानित", "उच्च कीर्ति"),
            ("खद्योत्", "Khadyot", "सूर्य का दिव्य प्रकाश", "आत्मबल एवं तेज"),
            ("खंज्", "Khanj", "चंचल एवं मनोहर नयन", "उल्लास एवं स्फूर्ति"),
            ("खिरोद्", "Khirod", "क्षीरसागर, पावन अमृतमय", "शांत चित्त")
        ],
        "f_roots": [
            ("ख्याति", "Khyati", "सद्कर्मों से अर्जित पावन यश", "मान-सम्मान"),
            ("खंजनि", "Khanjani", "मनोहर एवं प्रफुल्लित रूप", "प्रसन्नता"),
            ("खिला", "Khila", "प्रफुल्लित सुंदर पुष्प कली", "स्नेहमयी स्वभाव"),
            ("खगेशा", "Khagesha", "आकाश स्वरूपा माँ सरस्वती", "अगाध विद्या"),
            ("खीरा", "Kheer", "अमृतमयी क्षीरसागर की देवी", "गृह-लक्ष्मी")
        ]
    },
    "श": {
        "m_roots": [
            ("शिव्", "Shiv", "कल्याणकारी, मंगलमय भगवान शिव", "दिव्यता एवं शक्ति"),
            ("शौर्य्", "Shaurya", "अद्वितीय पराक्रम एवं वीरता", "निर्भीकता"),
            ("शाश्वत्", "Shashwat", "सदा सनातन एवं चिरंतन सत्य", "धैर्य एवं स्थिरता"),
            ("शुभ्", "Shubh", "सर्वदा कल्याणकारी एवं मंगलमय", "सद्गुण एवं उन्नति"),
            ("शौनक्", "Shaunak", "महान वैदिक ऋषि, ज्ञान के समुद्र", "विद्या एवं साधना")
        ],
        "f_roots": [
            ("शिवा", "Shiva", "माँ पार्वती का शुभ व सुंदर रूप", "शक्ति एवं शालीनता"),
            ("श्राव्य", "Shravya", "कर्णप्रिय मधुर संगीत स्वर", "मधुर वाणी"),
            ("श्रेय", "Shreya", "सर्वश्रेष्ठ शुभता एवं कल्याण", "समृद्धि एवं यश"),
            ("शुचि", "Shuchi", "परम पवित्र एवं पावन", "सात्विकता")
        ]
    }
}

M_SUFFIXES = [
    ("ेश", "esh", "अधिपति एवं स्वामी"),
    ("इंद्र", "indra", "श्रेष्ठ एवं तेजस्वी"),
    ("अंश", "ansh", "दिव्य अंश"),
    ("देव", "dev", "ईश्वरीय स्वरूप"),
    ("राज", "raj", "सम्राट एवं अधिपति"),
    ("कांत", "kant", "अत्यंत प्रिय एवं मनमोहक"),
    ("पाल", "pal", "रक्षक एवं पालक"),
    ("मय", "may", "परिपूर्ण एवं युक्त"),
    ("वर्धन", "vardhan", "उन्नति करने वाला"),
    ("दीप", "deep", "मार्गदर्शक प्रकाश"),
    ("वर", "var", "सर्वश्रेष्ठ एवं उत्कृष्ट"),
    ("आनंद", "anand", "सदा प्रसन्न रहने वाला")
]

F_SUFFIXES = [
    ("ा", "a", "पावन स्वरूप"),
    ("ी", "i", "सौभाग्यशालिनी"),
    ("िका", "ika", "प्रिय एवं सुंदर"),
    ("िता", "ita", "अलंकृत एवं संपन्न"),
    ("्या", "ya", "पूजनीय एवं आदरणीय"),
    ("वती", "vati", "सद्गुणों से युक्त"),
    ("मयी", "mayi", "स्नेह से परिपूर्ण"),
    ("प्रिया", "priya", "सबकी लाडली"),
    ("श्री", "shree", "समृद्धि एवं सौभाग्य"),
    ("नंदिनी", "nandini", "आनंद देने वाली")
]

# Universal Sanskrit Vocabulary for all alphabets
UNIVERSAL_ROOTS = {
    "Boy": [
        ("आरव", "Aarav", "शांत एवं गंभीर ध्वनि", "शांति एवं एकाग्रता"),
        ("विहान", "Vihaan", "नया प्रभात एवं स्वर्णिम किरण", "उन्नति एवं प्रकाश"),
        ("अद्वैत", "Advait", "अद्वितीय ब्रह्म स्वरूप", "एकात्म भाव"),
        ("अयांश", "Ayaansh", "सूर्य की प्रथम पावन किरण", "तेजस्विता"),
        ("अगस्त्य", "Agastya", "महान वैदिक ऋषि", "तपस्या एवं ज्ञान"),
        ("वेदांत", "Vedant", "वेदों का परम सत्य", "आध्यात्मिक विवेक"),
        ("अनंत", "Anant", "जिसका कोई अंत न हो", "असीम शक्ति"),
        ("रुद्र", "Rudra", "पराक्रमी भगवान शिव", "निर्भीकता एवं बल"),
        ("प्रणव", "Pranav", "पवित्र ओंकार (ॐ) ध्वनि", "सर्वोच्च चेतना"),
        ("माधव", "Madhav", "भगवान श्रीकृष्ण", "समृद्धि एवं आनंद")
    ],
    "Girl": [
        ("अनिका", "Anika", "माँ दुर्गा का अनुग्रह रूप", "साहस एवं गरिमा"),
        ("आराध्या", "Aaradhya", "सदा वंदनीय एवं पूजनीय", "भक्ति एवं आदर"),
        ("सान्वी", "Saanvi", "माँ लक्ष्मी का पावन रूप", "समृद्धि एवं सौभाग्य"),
        ("अदिति", "Aditi", "समस्त देवों की जननी", "मातृत्व एवं संप्रभुता"),
        ("काव्या", "Kavya", "ज्ञानमयी एवं भावपूर्ण कविता", "सृजनात्मकता"),
        ("अवनी", "Avani", "सहनशील पृथ्वी", "धैर्य एवं स्थिरता"),
        ("मीरा", "Meera", "कृष्ण भक्ति की अमर गायिका", "अनन्य समर्पण"),
        ("गार्गी", "Gargi", "वैदिक काल की विदुषी", "अगाध ज्ञान"),
        ("प्रिशा", "Prisha", "ईश्वर का अनमोल उपहार", "कृतज्ञता एवं प्रेम"),
        ("सिया", "Siya", "माँ सीता का पावन रूप", "मर्यादा एवं धैर्य")
    ]
}

def clean_syllable(s):
    for m in ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः']:
        s = s.replace(m, '')
    return s.strip()

def generate_ai_names(letter, gender="All", mode="strict"):
    base_char = clean_syllable(letter)
    varga_data = PHONETIC_ROOTS.get(base_char) or PHONETIC_ROOTS.get(letter)

    generated_boys = []
    generated_girls = []
    seen = set()

    # Algorithmic Combinatorial Synthesis
    if varga_data:
        # Generate Boys
        for r_hi, r_en, r_mean, r_sig in varga_data.get("m_roots", []):
            for s_hi, s_en, s_mean in M_SUFFIXES:
                name_hi = f"{r_hi}{s_hi}"
                name_en = f"{r_en}{s_en}".title()
                if mode == "strict" and not (name_hi.startswith(letter) or name_hi.startswith(base_char)):
                    continue
                if name_hi not in seen:
                    seen.add(name_hi)
                    generated_boys.append({
                        "name_hi": name_hi,
                        "name_en": name_en,
                        "gender": "Boy",
                        "meaning": f"{r_mean}, {s_mean}",
                        "significance": r_sig
                    })

        # Generate Girls
        for r_hi, r_en, r_mean, r_sig in varga_data.get("f_roots", []):
            for s_hi, s_en, s_mean in F_SUFFIXES:
                name_hi = f"{r_hi}{s_hi}"
                name_en = f"{r_en}{s_en}".title()
                if mode == "strict" and not (name_hi.startswith(letter) or name_hi.startswith(base_char)):
                    continue
                if name_hi not in seen:
                    seen.add(name_hi)
                    generated_girls.append({
                        "name_hi": name_hi,
                        "name_en": name_en,
                        "gender": "Girl",
                        "meaning": f"{r_mean}, {s_mean}",
                        "significance": r_sig
                    })

    # Universal reservoir fallback for extensive variety
    for u in UNIVERSAL_ROOTS["Boy"]:
        n_hi = f"{letter}{u[0][1:]}" if mode == "strict" and len(u[0]) > 1 else u[0]
        n_en = f"{u[1]}"
        if n_hi not in seen:
            seen.add(n_hi)
            generated_boys.append({
                "name_hi": n_hi, "name_en": n_en, "gender": "Boy",
                "meaning": u[2], "significance": u[3]
            })

    for u in UNIVERSAL_ROOTS["Girl"]:
        n_hi = f"{letter}{u[0][1:]}" if mode == "strict" and len(u[0]) > 1 else u[0]
        n_en = f"{u[1]}"
        if n_hi not in seen:
            seen.add(n_hi)
            generated_girls.append({
                "name_hi": n_hi, "name_en": n_en, "gender": "Girl",
                "meaning": u[2], "significance": u[3]
            })

    # Filter by requested gender
    if gender == "Boy":
        final_list = generated_boys
    elif gender == "Girl":
        final_list = generated_girls
    else:
        final_list = generated_boys + generated_girls

    # Shuffle so every click gives a fresh unlimited batch of 12 names
    random.shuffle(final_list)
    return final_list[:12]
