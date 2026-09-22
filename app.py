from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from ND import get_kundli_details
from NE import generate_ai_names
from TV import init_db, add_milestone, get_milestones, export_raw_backup, import_raw_backup

init_db()

HTML_PAGE = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nanhi Duniya - Vedic Kundli, Naming & Vault</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAF7F2; }
    .glass-card { background: rgba(255, 255, 255, 0.96); border: 1px solid #EFEAE1; }
    .kundli-box { position: relative; width: 280px; height: 280px; margin: 0 auto; background: #FFFDF9; border: 2px solid #854D0E; }
    .kundli-svg { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
    .h-item { position: absolute; text-align: center; width: 64px; z-index: 10; transform: translate(-50%, -50%); }
    .rashi-no { color: #9A3412; font-size: 11px; font-weight: 800; display: block; line-height: 1; }
    .grah-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 2px; margin-top: 2px; }
    .grah-badge { background: #EEF2FF; color: #1E40AF; font-size: 9px; font-weight: 800; padding: 1px 3px; border-radius: 4px; border: 1px solid #DBEAFE; }
    #pdfCertTemplate { background: #FFFFFF; color: #1C1917; width: 680px; padding: 30px; margin: 0 auto; }
  </style>
</head>
<body class="text-stone-800 pb-20">

  <header class="py-3 px-4 border-b border-stone-200 bg-white sticky top-0 z-50 shadow-xs flex justify-between items-center max-w-md mx-auto">
    <div>
      <h1 class="text-xl font-black text-amber-900 tracking-tight">🌸 Nanhi Duniya</h1>
      <p id="tSubHeader" class="text-[10px] text-stone-500">वैदिक लग्न कुंडली • नामकरण • माइलस्टोन वॉल्ट</p>
    </div>
    <div class="flex items-center bg-stone-100 p-1 rounded-xl border border-stone-200 text-xs font-bold">
      <button id="langHiBtn" onclick="switchLanguage('hi')" class="px-2.5 py-1 rounded-lg bg-amber-800 text-white transition shadow-2xs">हिंदी</button>
      <button id="langEnBtn" onclick="switchLanguage('en')" class="px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition">English</button>
    </div>
  </header>

  <main class="max-w-md mx-auto p-4 space-y-5">

    <!-- STEP 1: Janm Vivaran Form -->
    <div id="stepBirthForm" class="glass-card rounded-2xl p-5 shadow-sm space-y-3">
      <div class="flex justify-between items-center">
        <h2 id="tBirthHeader" class="text-base font-bold text-stone-800 flex items-center gap-2">
          <span>✨</span> जन्म विवरण (Birth Details)
        </h2>
        <span id="tStep1Tag" class="text-[11px] bg-amber-100 text-amber-900 font-bold px-2 py-0.5 rounded-full">चरण 1</span>
      </div>

      <div class="space-y-2.5 text-xs">
        <div>
          <label id="tCityLabel" class="block font-semibold text-stone-600 mb-1">जन्म स्थान (City / District)</label>
          <input type="text" id="bCity" value="Gondia" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none">
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label id="tDateLabel" class="block font-semibold text-stone-600 mb-1">जन्म तारीख (Date)</label>
            <input type="date" id="bDate" value="2026-09-22" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none">
          </div>
          <div>
            <label id="tTimeLabel" class="block font-semibold text-stone-600 mb-1">जन्म समय (Time)</label>
            <input type="time" id="bTime" value="11:05" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none">
          </div>
        </div>

        <button id="calcBtn" type="button" onclick="calculateKundli()" class="w-full py-2.5 bg-amber-800 hover:bg-amber-900 text-white font-bold rounded-xl mt-2 active:scale-95 transition shadow-sm">
          लग्न कुंडली एवं नामकरण अक्षर देखें
        </button>
      </div>

      <!-- Kundli & Akshar Results -->
      <div id="kundliResult" class="hidden mt-4 pt-3 border-t border-stone-200 space-y-4">
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="p-2.5 bg-amber-50 rounded-xl border border-amber-200">
            <span id="tLagnaLabel" class="text-[10px] text-stone-500 block">लग्न राशि</span>
            <span id="resLagna" class="font-bold text-amber-900 text-sm"></span>
          </div>
          <div class="p-2.5 bg-amber-50 rounded-xl border border-amber-200">
            <span id="tRashiLabel" class="text-[10px] text-stone-500 block">चन्द्र राशि</span>
            <span id="resRashi" class="font-bold text-stone-800 text-sm"></span>
          </div>
        </div>

        <div class="p-3 bg-stone-50 rounded-xl border border-stone-200 text-xs space-y-1">
          <div class="flex justify-between"><span id="tNakshatraLabel" class="text-stone-500">नक्षत्र:</span><span id="resNakshatra" class="font-bold"></span></div>
          <div class="flex justify-between"><span id="tPadaLabel" class="text-stone-500">चरण:</span><span id="resPada" class="font-bold"></span></div>
          <div class="flex justify-between items-center pt-1 border-t border-stone-200">
            <span id="tAksharLabel" class="text-stone-700 font-bold">शास्त्रसम्मत नामकरण अक्षर:</span>
            <span id="resAkshar" class="text-2xl font-black text-amber-800"></span>
          </div>
        </div>

        <div class="text-center pt-2">
          <p id="tChartTitle" class="text-xs font-bold text-stone-700 mb-2">Live Lagna Chart (लग्न एवं 9 ग्रह)</p>
          <div id="mainKundliBox" class="kundli-box rounded-xl shadow-xs">
            <svg class="kundli-svg" viewBox="0 0 280 280">
              <line x1="0" y1="0" x2="280" y2="280" stroke="#854D0E" stroke-width="1.5" />
              <line x1="0" y1="280" x2="280" y2="0" stroke="#854D0E" stroke-width="1.5" />
              <polygon points="140,0 280,140 140,280 0,140" fill="none" stroke="#854D0E" stroke-width="1.5" />
            </svg>
            <div id="box1" class="h-item" style="top: 70px; left: 140px;"></div>
            <div id="box2" class="h-item" style="top: 35px; left: 70px;"></div>
            <div id="box3" class="h-item" style="top: 70px; left: 35px;"></div>
            <div id="box4" class="h-item" style="top: 140px; left: 70px;"></div>
            <div id="box5" class="h-item" style="top: 210px; left: 35px;"></div>
            <div id="box6" class="h-item" style="top: 245px; left: 70px;"></div>
            <div id="box7" class="h-item" style="top: 210px; left: 140px;"></div>
            <div id="box8" class="h-item" style="top: 245px; left: 210px;"></div>
            <div id="box9" class="h-item" style="top: 210px; left: 245px;"></div>
            <div id="box10" class="h-item" style="top: 140px; left: 210px;"></div>
            <div id="box11" class="h-item" style="top: 70px; left: 245px;"></div>
            <div id="box12" class="h-item" style="top: 35px; left: 210px;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: Naming Engine -->
    <div id="namesSection" class="hidden glass-card rounded-2xl p-5 shadow-sm space-y-4">
      <div class="flex justify-between items-center">
        <div>
          <h2 id="tNamingTitle" class="text-base font-bold text-stone-800 flex items-center gap-1.5">
            <span>👶</span> वैदिक नाम चयन
          </h2>
          <p id="tNamingSub" class="text-[11px] text-stone-500">अक्षर '<span id="currentLetterBadge" class="font-bold text-amber-900"></span>' से नाम चुनें</p>
        </div>
        <button id="tRegenBtn" type="button" onclick="fetchAINames()" class="text-xs bg-amber-100 hover:bg-amber-200 text-amber-900 px-3 py-1.5 rounded-lg font-bold transition">
          और नाम देखें ↻
        </button>
      </div>

      <div class="grid grid-cols-2 gap-2 bg-stone-100 p-1.5 rounded-xl text-xs font-bold text-center">
        <button id="modeStrict" onclick="setNamingMode('strict')" class="py-2 rounded-lg bg-white text-amber-950 shadow-xs transition">
          🎯 <span id="tStrictLabel">केवल शुद्ध अक्षर</span> (<span id="strictLetterText"></span>)
        </button>
        <button id="modeAnumati" onclick="setNamingMode('anumati')" class="py-2 rounded-lg text-stone-500 hover:text-stone-800 transition">
          📜 <span id="tAnumatiLabel">अनुमति वर्ग</span> (<span id="anumatiLetterText"></span>)
        </button>
      </div>

      <div class="flex gap-2">
        <button id="btnAll" onclick="setGenderFilter('All')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-amber-800 text-white transition">सभी (All)</button>
        <button id="btnBoy" onclick="setGenderFilter('Boy')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600 hover:bg-stone-200 transition">👦 लड़के</button>
        <button id="btnGirl" onclick="setGenderFilter('Girl')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600 hover:bg-stone-200 transition">👧 लड़कियां</button>
      </div>

      <div id="namesList" class="space-y-2.5"></div>

      <div class="pt-3 border-t border-stone-200 text-xs space-y-2">
        <p id="tCustomPrompt" class="font-bold text-stone-700">या अपना पहले से तय किया हुआ नाम लिखें:</p>
        <div class="flex gap-2">
          <input type="text" id="customNameInput" placeholder="उदा. आरव, अनिका, विहान..." class="flex-1 p-2.5 rounded-xl border border-stone-300">
          <button id="tCustomBtn" onclick="useCustomName()" class="px-4 py-2.5 bg-stone-900 text-white font-bold rounded-xl active:scale-95 transition">
            चुनें
          </button>
        </div>
      </div>
    </div>

    <!-- STEP 3: Master Password Lock -->
    <div id="profileLockSection" class="hidden glass-card rounded-2xl p-5 shadow-sm space-y-4 border-2 border-amber-300">
      <div class="flex justify-between items-center">
        <div>
          <h2 id="tProfileLockTitle" class="text-base font-bold text-stone-900 flex items-center gap-1.5">
            <span>🔐</span> शिशु प्रोफ़ाइल एवं मास्टर पासवर्ड
          </h2>
          <p class="text-[11px] text-stone-500">Zero-Knowledge AES-256 Vault Encryption</p>
        </div>
        <span id="tStep2Tag" class="text-xs bg-emerald-100 text-emerald-900 font-bold px-2 py-0.5 rounded-md">चरण 2</span>
      </div>

      <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200 text-xs space-y-1.5">
        <div class="flex justify-between"><span id="tFinalNameLabel" class="text-stone-600">अंतिम चुना हुआ नाम:</span><span id="cardFinalName" class="font-black text-amber-900 text-sm"></span></div>
        <div class="flex justify-between"><span id="tFinalDateLabel" class="text-stone-600">जन्म तारीख:</span><span id="cardFinalDate" class="font-bold text-stone-800"></span></div>
        <div class="flex justify-between"><span id="tFinalTimeLabel" class="text-stone-600">जन्म समय:</span><span id="cardFinalTime" class="font-bold text-stone-800"></span></div>
        <div class="flex justify-between"><span id="tFinalCityLabel" class="text-stone-600">जन्म स्थान:</span><span id="cardFinalCity" class="font-bold text-stone-800"></span></div>
      </div>

      <div class="space-y-2 text-xs">
        <label id="tMasterPassPrompt" class="block font-bold text-stone-700">एक गुप्त मास्टर पासवर्ड (Family Secret Key) बनाएं:</label>
        <input type="password" id="masterPasswordInput" placeholder="यह पासवर्ड केवल आपको पता होना चाहिए" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none">
        <p id="tMasterPassNote" class="text-[10px] text-stone-500">✦ इसी पासवर्ड से भविष्य में शिशु की सारी यादें सुरक्षित रहेंगी।</p>
        
        <button id="tLockProfileBtn" onclick="lockProfileAndOpenVault()" class="w-full py-2.5 bg-emerald-800 hover:bg-emerald-900 text-white font-bold rounded-xl mt-2 active:scale-95 transition shadow-sm">
          प्रोफ़ाइल लॉक करें एवं माइलस्टोन वॉल्ट खोलें ➔
        </button>
      </div>
    </div>

    <!-- STEP 4: Lifetime Milestone Vault -->
    <div id="vaultSection" class="hidden glass-card rounded-2xl p-5 shadow-sm space-y-4">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-base font-bold text-stone-800 flex items-center gap-1.5">
            <span>🛡️</span> <span id="vaultBabyNameHeading">शिशु</span> <span id="tVaultHeadingText">का माइलस्टोन वॉल्ट</span>
          </h2>
          <p id="tVaultSub" class="text-[11px] text-stone-500">जीवन की अनमोल यादें एवं प्रश्न संदूक</p>
        </div>
        <span id="tSecureVaultTag" class="text-xs bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full font-bold">सुरक्षित वॉल्ट</span>
      </div>

      <div class="p-3.5 bg-stone-50 rounded-xl border border-stone-200 text-xs space-y-2.5">
        <p id="tAddMemoryTitle" class="font-bold text-stone-700">नई याद / प्रश्न (Add Question & Memory):</p>
        
        <div class="flex gap-2">
          <select id="milestoneType" onchange="toggleCustomQuestion()" class="w-1/2 p-2 rounded-xl border border-stone-300 bg-white">
            <option value="PRESET">तयशुदा माइलस्टोन</option>
            <option value="CUSTOM">अपना नया सवाल / घटना</option>
          </select>
          <input type="date" id="mEventDate" class="w-1/2 p-2 rounded-xl border border-stone-300 bg-white">
        </div>

        <div id="presetSelectDiv">
          <select id="mPresetTag" class="w-full p-2 rounded-xl border border-stone-300 bg-white">
            <option value="FIRST_SMILE">पहली बार मुस्कुराया (First Smile)</option>
            <option value="FIRST_STEP">पहला कदम रखा (First Steps)</option>
            <option value="FIRST_FOOD">पहला अन्नप्राशन (First Solid Food)</option>
            <option value="FIRST_WORD">पहला शब्द क्या बोला (First Word)</option>
            <option value="FIRST_TRIP">पहली यात्रा / ननिहाल आगमन</option>
          </select>
        </div>

        <div id="customQuestionDiv" class="hidden">
          <input type="text" id="mCustomQuestion" placeholder="उदा. पहला खिलौना कौन सा पसंद था? या लोरी सुनते ही क्या किया?" class="w-full p-2 rounded-xl border border-stone-300 bg-white">
        </div>

        <textarea id="mNotes" rows="2" placeholder="उस पल की पूरी याद, भावनाएं व बातें विस्तार से लिखें..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white"></textarea>

        <button id="tSaveVaultBtn" type="button" onclick="saveNewMilestone()" class="w-full py-2.5 bg-stone-900 text-white rounded-xl font-bold active:scale-95 transition">
          वॉल्ट में सुरक्षित सहेजें (Save to Vault)
        </button>
      </div>

      <div class="pt-2 border-t border-stone-200 flex justify-between items-center">
        <button id="tViewSavedBtn" type="button" onclick="loadSavedMilestones()" class="text-xs text-amber-800 font-bold underline">
          सहेजी हुई यादें देखें ↻
        </button>
        <button id="tDownloadPdfBtn" type="button" onclick="downloadAlbumPDF()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-3.5 py-2 rounded-xl font-bold shadow-sm active:scale-95 transition">
          📖 PDF एल्बम डाउनलोड
        </button>
      </div>

      <div id="albumView" class="space-y-2"></div>

      <!-- PARENTS DATA BACKUP & RESTORE UTILITY -->
      <div class="pt-3 border-t-2 border-dashed border-stone-200 text-xs space-y-2">
        <p class="font-bold text-stone-700 flex items-center gap-1.5">
          <span>💾</span> माता-पिता के लिए सुरक्षित बैकअप (Backup & Restore)
        </p>
        <p class="text-[10px] text-stone-500">फ़ोन बदलने या सुरक्षित रखने के लिए एन्क्रिप्टेड फ़ाइल डाउनलोड व रीस्टोर करें:</p>
        <div class="flex gap-2">
          <button onclick="downloadBackupFile()" class="flex-1 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 transition">
            📥 बैकअप डाउनलोड
          </button>
          <label class="flex-1 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 text-center cursor-pointer transition">
            📤 बैकअप रीस्टोर
            <input type="file" id="restoreFileInput" accept=".json" onchange="uploadRestoreFile(event)" class="hidden">
          </label>
        </div>
      </div>
    </div>

  </main>

  <!-- Complete Standalone Printable PDF Canvas Template -->
  <div style="position: absolute; left: -9999px; top: 0;">
    <div id="pdfCertTemplate">
      <div style="text-align: center; border-bottom: 2px solid #854D0E; padding-bottom: 12px; margin-bottom: 15px;">
        <h1 style="font-size: 26px; font-weight: 800; color: #78350F; margin: 0;">🌸 नन्ही दुनिया (Nanhi Duniya)</h1>
        <p style="font-size: 13px; color: #78716C; margin: 4px 0 0 0;">Official Digital Janmapatri & Lifetime Milestone Journal</p>
      </div>

      <div style="display: flex; justify-content: space-between; background: #FEF3C7; border: 1px solid #FDE68A; padding: 12px 18px; border-radius: 10px; margin-bottom: 20px;">
        <div>
          <span style="font-size: 11px; color: #92400E; display: block;">शिशु का नाम (Baby Name)</span>
          <span id="pdfBabyName" style="font-size: 20px; font-weight: 800; color: #78350F;"></span>
        </div>
        <div style="text-align: right; font-size: 11px; color: #78350F; font-weight: 600;">
          <p id="pdfBirthDate" style="margin: 0;"></p>
          <p id="pdfBirthTime" style="margin: 2px 0 0 0;"></p>
          <p id="pdfBirthCity" style="margin: 2px 0 0 0;"></p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 20px; text-align: center; font-size: 11px;">
        <div style="padding: 8px; background: #F5F5F4; border-radius: 6px;">
          <span style="color: #78716C; display: block;">लग्न राशि</span>
          <strong id="pdfLagna" style="color: #78350F;"></strong>
        </div>
        <div style="padding: 8px; background: #F5F5F4; border-radius: 6px;">
          <span style="color: #78716C; display: block;">चन्द्र राशि</span>
          <strong id="pdfRashi" style="color: #1C1917;"></strong>
        </div>
        <div style="padding: 8px; background: #F5F5F4; border-radius: 6px;">
          <span style="color: #78716C; display: block;">नक्षत्र एवं चरण</span>
          <strong id="pdfNakshatra" style="color: #1C1917;"></strong>
        </div>
        <div style="padding: 8px; background: #FEF3C7; border: 1px solid #FCD34D; border-radius: 6px;">
          <span style="color: #92400E; display: block;">नामकरण अक्षर</span>
          <strong id="pdfAkshar" style="color: #78350F; font-size: 16px;"></strong>
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 25px;">
        <p style="font-size: 12px; font-weight: bold; color: #78350F; margin-bottom: 8px;">लग्न कुण्डली (Lagna Chart)</p>
        <div id="pdfChartClone" style="display: inline-block;"></div>
      </div>

      <div style="border-top: 2px dashed #D6D3D1; padding-top: 15px;">
        <h3 style="font-size: 15px; font-weight: bold; color: #78350F; margin: 0 0 10px 0;">🛡️ अनमोल यादें एवं मील के पत्थर (Life Milestones & Memories)</h3>
        <div id="pdfMilestoneList" style="font-size: 11px;"></div>
      </div>

      <div style="margin-top: 30px; text-align: center; font-size: 9px; color: #A8A29E; border-top: 1px solid #E7E5E4; padding-top: 8px;">
        Encrypted with Zero-Knowledge AES-256 Vault • Generated by Nanhi Duniya Engine
      </div>
    </div>
  </div>

  <script>
    let currentLang = 'hi';
    let currentLetter = "तू";
    let selectedGender = "All";
    let namingMode = "strict";
    let currentSavedMilestones = [];
    let finalizedBaby = {
      name: "",
      city: "",
      date: "",
      time: "",
      masterPassword: ""
    };

    const UI_STRINGS = {
      hi: {
        subHeader: "वैदिक लग्न कुंडली • नामकरण • माइलस्टोन वॉल्ट",
        birthHeader: "✨ जन्म विवरण (Birth Details)",
        step1Tag: "चरण 1",
        cityLabel: "जन्म स्थान (City / District)",
        dateLabel: "जन्म तारीख (Date)",
        timeLabel: "जन्म समय (Time)",
        calcBtn: "लग्न कुंडली एवं नामकरण अक्षर देखें",
        lagnaLabel: "लग्न राशि",
        rashiLabel: "चन्द्र राशि",
        nakshatraLabel: "नक्षत्र:",
        padaLabel: "चरण:",
        aksharLabel: "शास्त्रसम्मत नामकरण अक्षर:",
        chartTitle: "Live Lagna Chart (लग्न एवं 9 ग्रह)",
        namingTitle: "👶 वैदिक नाम चयन",
        namingSub: "अक्षर '<span id='currentLetterBadge' class='font-bold text-amber-900'>" + currentLetter + "</span>' से नाम चुनें",
        regenBtn: "और नाम देखें ↻",
        strictLabel: "केवल शुद्ध अक्षर",
        anumatiLabel: "अनुमति वर्ग",
        btnAll: "सभी (All)",
        btnBoy: "👦 लड़के",
        btnGirl: "👧 लड़कियां",
        customPrompt: "या अपना पहले से तय किया हुआ नाम लिखें:",
        customPlaceholder: "उदा. आरव, अनिका, विहान...",
        customBtn: "चुनें",
        chooseThisNameBtn: "👑 यह नाम चुनें",
        meaningLabel: "अर्थ:",
        sigLabel: "ज्योतिषीय महत्व:",
        boyTag: "👦 लड़का",
        girlTag: "👧 लड़की",
        profileLockTitle: "🔐 शिशु प्रोफ़ाइल एवं मास्टर पासवर्ड",
        step2Tag: "चरण 2",
        finalNameLabel: "अंतिम चुना हुआ नाम:",
        finalDateLabel: "जन्म तारीख:",
        finalTimeLabel: "जन्म समय:",
        finalCityLabel: "जन्म स्थान:",
        masterPassPrompt: "एक गुप्त मास्टर पासवर्ड (Family Secret Key) बनाएं:",
        masterPassPlaceholder: "यह पासवर्ड केवल आपको पता होना चाहिए",
        masterPassNote: "✦ इसी पासवर्ड से भविष्य में शिशु की सारी यादें सुरक्षित रहेंगी।",
        lockProfileBtn: "प्रोफ़ाइल लॉक करें एवं माइलस्टोन वॉल्ट खोलें ➔",
        vaultHeadingText: "का माइलस्टोन वॉल्ट",
        vaultSub: "जीवन की अनमोल यादें एवं प्रश्न संदूक",
        secureVaultTag: "सुरक्षित वॉल्ट",
        addMemoryTitle: "नई याद / प्रश्न (Add Question & Memory):",
        notesPlaceholder: "उस पल की पूरी याद, भावनाएं व बातें विस्तार से लिखें...",
        saveVaultBtn: "वॉल्ट में सुरक्षित सहेजें (Save to Vault)",
        viewSavedBtn: "सहेजी हुई यादें देखें ↻",
        downloadPdfBtn: "📖 PDF एल्बम डाउनलोड"
      },
      en: {
        subHeader: "Vedic Lagna Kundli • Shastriya Naming • Milestone Vault",
        birthHeader: "✨ Birth Details (Janm Vivaran)",
        step1Tag: "Step 1",
        cityLabel: "Birth Place (City / District)",
        dateLabel: "Birth Date",
        timeLabel: "Birth Time",
        calcBtn: "Generate Lagna Chart & Vedic Syllable",
        lagnaLabel: "Ascendant (Lagna)",
        rashiLabel: "Moon Sign (Rashi)",
        nakshatraLabel: "Nakshatra:",
        padaLabel: "Quarter (Pada):",
        aksharLabel: "Scriptural Naming Syllable:",
        chartTitle: "Live Lagna Chart (Ascendant & 9 Planets)",
        namingTitle: "👶 Vedic Name Selection",
        namingSub: "Suggested Names for Syllable '<span id='currentLetterBadge' class='font-bold text-amber-900'>" + currentLetter + "</span>'",
        regenBtn: "Generate More ↻",
        strictLabel: "Strict Syllable",
        anumatiLabel: "Permitted Class",
        btnAll: "All",
        btnBoy: "👦 Boys",
        btnGirl: "👧 Girls",
        customPrompt: "Or enter your pre-decided name:",
        customPlaceholder: "e.g., Aarav, Anika, Vihaan...",
        customBtn: "Select",
        chooseThisNameBtn: "👑 Select This Name",
        meaningLabel: "Meaning:",
        sigLabel: "Significance:",
        boyTag: "👦 Boy",
        girlTag: "👧 Girl",
        profileLockTitle: "🔐 Baby Profile & Master Password",
        step2Tag: "Step 2",
        finalNameLabel: "Final Chosen Name:",
        finalDateLabel: "Birth Date:",
        finalTimeLabel: "Birth Time:",
        finalCityLabel: "Birth Place:",
        masterPassPrompt: "Create a Master Password (Family Secret Key):",
        masterPassPlaceholder: "This password should only be known to you",
        masterPassNote: "✦ All future memories, milestones and photos are securely encrypted with this key.",
        lockProfileBtn: "Lock Profile & Open Milestone Vault ➔",
        vaultHeadingText: "'s Milestone Vault",
        vaultSub: "Lifetime Memories & Questions Vault",
        secureVaultTag: "Secure Vault",
        addMemoryTitle: "Add Milestone / Question & Memory:",
        notesPlaceholder: "Record the emotions, memories and story in detail...",
        saveVaultBtn: "Save Securely to Vault",
        viewSavedBtn: "View Saved Memories ↻",
        downloadPdfBtn: "📖 Export PDF Album"
      }
    };

    function switchLanguage(lang) {
      currentLang = lang;
      if (lang === 'hi') {
        document.getElementById('langHiBtn').className = "px-2.5 py-1 rounded-lg bg-amber-800 text-white transition shadow-2xs";
        document.getElementById('langEnBtn').className = "px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition";
      } else {
        document.getElementById('langEnBtn').className = "px-2.5 py-1 rounded-lg bg-amber-800 text-white transition shadow-2xs";
        document.getElementById('langHiBtn').className = "px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition";
      }

      const s = UI_STRINGS[lang];
      document.getElementById('tSubHeader').innerText = s.subHeader;
      document.getElementById('tBirthHeader').innerHTML = `<span>✨</span> ${s.birthHeader}`;
      document.getElementById('tStep1Tag').innerText = s.step1Tag;
      document.getElementById('tCityLabel').innerText = s.cityLabel;
      document.getElementById('tDateLabel').innerText = s.dateLabel;
      document.getElementById('tTimeLabel').innerText = s.timeLabel;
      document.getElementById('calcBtn').innerText = s.calcBtn;
      document.getElementById('tLagnaLabel').innerText = s.lagnaLabel;
      document.getElementById('tRashiLabel').innerText = s.rashiLabel;
      document.getElementById('tNakshatraLabel').innerText = s.nakshatraLabel;
      document.getElementById('tPadaLabel').innerText = s.padaLabel;
      document.getElementById('tAksharLabel').innerText = s.aksharLabel;
      document.getElementById('tChartTitle').innerText = s.chartTitle;

      document.getElementById('tNamingTitle').innerHTML = `<span>👶</span> ${s.namingTitle}`;
      document.getElementById('tNamingSub').innerHTML = lang === 'hi' 
        ? `अक्षर '<span id='currentLetterBadge' class='font-bold text-amber-900'>${currentLetter}</span>' से नाम चुनें`
        : `Suggested Names for Syllable '<span id='currentLetterBadge' class='font-bold text-amber-900'>${currentLetter}</span>'`;
      document.getElementById('tRegenBtn').innerText = s.regenBtn;
      document.getElementById('tStrictLabel').innerText = s.strictLabel;
      document.getElementById('tAnumatiLabel').innerText = s.anumatiLabel;
      document.getElementById('btnAll').innerText = s.btnAll;
      document.getElementById('btnBoy').innerText = s.btnBoy;
      document.getElementById('btnGirl').innerText = s.btnGirl;
      document.getElementById('tCustomPrompt').innerText = s.customPrompt;
      document.getElementById('customNameInput').placeholder = s.customPlaceholder;
      document.getElementById('tCustomBtn').innerText = s.customBtn;

      document.getElementById('tProfileLockTitle').innerHTML = `<span>🔐</span> ${s.profileLockTitle}`;
      document.getElementById('tStep2Tag').innerText = s.step2Tag;
      document.getElementById('tFinalNameLabel').innerText = s.finalNameLabel;
      document.getElementById('tFinalDateLabel').innerText = s.finalDateLabel;
      document.getElementById('tFinalTimeLabel').innerText = s.finalTimeLabel;
      document.getElementById('tFinalCityLabel').innerText = s.finalCityLabel;
      document.getElementById('tMasterPassPrompt').innerText = s.masterPassPrompt;
      document.getElementById('masterPasswordInput').placeholder = s.masterPassPlaceholder;
      document.getElementById('tMasterPassNote').innerText = s.masterPassNote;
      document.getElementById('tLockProfileBtn').innerText = s.lockProfileBtn;

      document.getElementById('tVaultHeadingText').innerText = s.vaultHeadingText;
      document.getElementById('tVaultSub').innerText = s.vaultSub;
      document.getElementById('tSecureVaultTag').innerText = s.secureVaultTag;
      document.getElementById('tAddMemoryTitle').innerText = s.addMemoryTitle;
      document.getElementById('mNotes').placeholder = s.notesPlaceholder;
      document.getElementById('tSaveVaultBtn').innerText = s.saveVaultBtn;
      document.getElementById('tViewSavedBtn').innerText = s.viewSavedBtn;
      document.getElementById('tDownloadPdfBtn').innerText = s.downloadPdfBtn;

      const sel = document.getElementById('mPresetTag');
      if (lang === 'en') {
        sel.options[0].text = "First Smile";
        sel.options[1].text = "First Steps";
        sel.options[2].text = "First Solid Food (Annaprashan)";
        sel.options[3].text = "First Word Spoken";
        sel.options[4].text = "First Family Trip";
        document.getElementById('milestoneType').options[0].text = "Standard Milestone";
        document.getElementById('milestoneType').options[1].text = "Custom Question / Memory";
        document.getElementById('mCustomQuestion').placeholder = "e.g., Favorite first toy, reaction to lullaby...";
      } else {
        sel.options[0].text = "पहली बार मुस्कुराया (First Smile)";
        sel.options[1].text = "पहला कदम रखा (First Steps)";
        sel.options[2].text = "पहला अन्नप्राशन (First Solid Food)";
        sel.options[3].text = "पहला शब्द क्या बोला (First Word)";
        sel.options[4].text = "पहली यात्रा / ननिहाल आगमन";
        document.getElementById('milestoneType').options[0].text = "तयशुदा माइलस्टोन";
        document.getElementById('milestoneType').options[1].text = "अपना नया सवाल / घटना";
        document.getElementById('mCustomQuestion').placeholder = "उदा. पहला खिलौना कौन सा पसंद था? या लोरी सुनते ही क्या किया?";
      }

      fetchAINames();
    }

    function setNamingMode(mode) {
      namingMode = mode;
      if (mode === 'strict') {
        document.getElementById('modeStrict').className = "py-2 rounded-lg bg-white text-amber-950 shadow-xs transition";
        document.getElementById('modeAnumati').className = "py-2 rounded-lg text-stone-500 hover:text-stone-800 transition";
      } else {
        document.getElementById('modeAnumati').className = "py-2 rounded-lg bg-white text-amber-950 shadow-xs transition";
        document.getElementById('modeStrict').className = "py-2 rounded-lg text-stone-500 hover:text-stone-800 transition";
      }
      fetchAINames();
    }

    function setGenderFilter(gen) {
      selectedGender = gen;
      ['btnAll', 'btnBoy', 'btnGirl'].forEach(id => {
        document.getElementById(id).className = "flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600 hover:bg-stone-200 transition";
      });
      if (gen === 'All') document.getElementById('btnAll').className = "flex-1 py-1.5 rounded-xl text-xs font-bold bg-amber-800 text-white transition";
      if (gen === 'Boy') document.getElementById('btnBoy').className = "flex-1 py-1.5 rounded-xl text-xs font-bold bg-blue-700 text-white transition";
      if (gen === 'Girl') document.getElementById('btnGirl').className = "flex-1 py-1.5 rounded-xl text-xs font-bold bg-rose-700 text-white transition";
      fetchAINames();
    }

    async function calculateKundli() {
      const btn = document.getElementById('calcBtn');
      const bCity = document.getElementById('bCity').value.trim() || "Gondia";
      const bDate = document.getElementById('bDate').value;
      const bTime = document.getElementById('bTime').value;

      if (!bDate || !bTime) return alert(currentLang === 'hi' ? "Date aur time dalein" : "Please enter date and time");

      btn.innerText = currentLang === 'hi' ? "Kundli Banayi Ja Rahi Hai..." : "Calculating Kundli...";
      btn.disabled = true;

      try {
        const parts = bDate.split(/[-/]/);
        let year, month, day;
        if (parts[0].length === 4) {
          year = parseInt(parts[0]); month = parseInt(parts[1]); day = parseInt(parts[2]);
        } else {
          day = parseInt(parts[0]); month = parseInt(parts[1]); year = parseInt(parts[2]);
        }

        const tParts = bTime.split(':');
        const hour = parseInt(tParts[0]);
        const minute = parseInt(tParts[1]);

        const res = await fetch(`/api/kundli?y=${year}&m=${month}&d=${day}&h=${hour}&min=${minute}&city=${encodeURIComponent(bCity)}`);
        const data = await res.json();

        document.getElementById('resLagna').innerText = currentLang === 'hi' 
          ? `${data.lagna_hindi} (${data.lagna_english})`
          : `${data.lagna_english} (${data.lagna_hindi})`;
        document.getElementById('resRashi').innerText = currentLang === 'hi'
          ? `${data.rashi_hindi} (${data.rashi_english})`
          : `${data.rashi_english} (${data.rashi_hindi})`;

        document.getElementById('resNakshatra').innerText = data.nakshatra_hindi;
        document.getElementById('resPada').innerText = currentLang === 'hi' ? `Charan ${data.charan}` : `Quarter ${data.charan}`;
        document.getElementById('resAkshar').innerText = data.naam_akshar_hindi;

        currentLetter = data.naam_akshar_hindi;
        document.getElementById('currentLetterBadge').innerText = currentLetter;
        document.getElementById('strictLetterText').innerText = currentLetter;
        
        let rootChar = currentLetter.replace(/[ािीुूृेैोौंः]/g, '');
        document.getElementById('anumatiLetterText').innerText = rootChar;

        const lagnaNum = Number(data.lagna_rashi_num) || 1;
        const housesMap = data.houses_planets || {};

        for (let h = 1; h <= 12; h++) {
          let rashi = (lagnaNum + h - 2) % 12 + 1;
          let pList = housesMap[String(h)] || housesMap[h] || [];
          let grahHtml = pList.length > 0
            ? `<div class="grah-container">${pList.map(p => `<span class="grah-badge">${p}</span>`).join('')}</div>`
            : '';
          const box = document.getElementById(`box${h}`);
          if (box) box.innerHTML = `<span class="rashi-no">${rashi}</span>${grahHtml}`;
        }

        document.getElementById('kundliResult').classList.remove('hidden');
        document.getElementById('namesSection').classList.remove('hidden');

        setNamingMode('strict');
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        btn.innerText = UI_STRINGS[currentLang].calcBtn;
        btn.disabled = false;
      }
    }

    async function fetchAINames() {
      const listDiv = document.getElementById('namesList');
      listDiv.innerHTML = "";
      const s = UI_STRINGS[currentLang];

      try {
        const res = await fetch(`/api/ai-names?letter=${encodeURIComponent(currentLetter)}&gender=${encodeURIComponent(selectedGender)}&mode=${encodeURIComponent(namingMode)}`);
        const names = await res.json();

        names.forEach(n => {
          const isBoy = n.gender === 'Boy';
          const genderBadge = isBoy
            ? `<span class="text-[10px] bg-blue-50 text-blue-800 px-2 py-0.5 rounded-full font-bold border border-blue-200">${s.boyTag}</span>`
            : `<span class="text-[10px] bg-rose-50 text-rose-800 px-2 py-0.5 rounded-full font-bold border border-rose-200">${s.girlTag}</span>`;

          listDiv.innerHTML += `
            <div class="p-3.5 bg-white rounded-xl border border-stone-200 shadow-2xs space-y-2">
              <div class="flex justify-between items-center">
                <div>
                  <h3 class="text-base font-extrabold text-stone-900">${n.name_hi} <span class="text-xs font-medium text-stone-500 font-sans">(${n.name_en})</span></h3>
                  <div class="flex gap-1.5 mt-1">${genderBadge}</div>
                </div>
                <button onclick="finalizeName('${n.name_hi}')" class="px-3 py-1.5 rounded-xl border border-amber-400 text-amber-950 bg-amber-100 hover:bg-amber-200 text-xs font-black shadow-xs active:scale-95 transition">
                  ${s.chooseThisNameBtn}
                </button>
              </div>

              <div class="pt-1.5 border-t border-stone-100 text-xs space-y-1">
                <p class="text-stone-700"><span class="font-bold text-stone-900">${s.meaningLabel}</span> ${n.meaning}</p>
                ${n.significance ? `<p class="text-amber-900 font-medium"><span class="font-bold">${s.sigLabel}</span>${n.significance}</p>` : ''}
              </div>
            </div>
          `;
        });
      } catch (e) {
        listDiv.innerHTML = `<p class="text-xs text-red-500 text-center py-2">${currentLang === 'hi' ? 'नाम लोड करने में समस्या आई।' : 'Failed to load names.'}</p>`;
      }
    }

    function useCustomName() {
      const cName = document.getElementById('customNameInput').value.trim();
      if (!cName) return alert(currentLang === 'hi' ? "कृपया नाम दर्ज करें" : "Please enter a name");
      finalizeName(cName);
    }

    function finalizeName(name) {
      finalizedBaby.name = name;
      finalizedBaby.city = document.getElementById('bCity').value.trim();
      finalizedBaby.date = document.getElementById('bDate').value;
      finalizedBaby.time = document.getElementById('bTime').value;

      document.getElementById('cardFinalName').innerText = finalizedBaby.name;
      document.getElementById('cardFinalDate').innerText = finalizedBaby.date;
      document.getElementById('cardFinalTime').innerText = finalizedBaby.time;
      document.getElementById('cardFinalCity').innerText = finalizedBaby.city;

      document.getElementById('profileLockSection').classList.remove('hidden');
      document.getElementById('profileLockSection').scrollIntoView({ behavior: 'smooth' });
    }

    function lockProfileAndOpenVault() {
      const pwd = document.getElementById('masterPasswordInput').value.trim();
      if (!pwd) return alert(currentLang === 'hi' ? "कृपया एक मास्टर पासवर्ड दर्ज करें!" : "Please enter a master password!");
      if (pwd.length < 4) return alert(currentLang === 'hi' ? "पासवर्ड कम से कम 4 अक्षरों का रखें" : "Password must be at least 4 characters");

      finalizedBaby.masterPassword = pwd;

      document.getElementById('vaultBabyNameHeading').innerText = finalizedBaby.name;
      document.getElementById('vaultSection').classList.remove('hidden');
      document.getElementById('vaultSection').scrollIntoView({ behavior: 'smooth' });

      document.getElementById('mEventDate').value = new Date().toISOString().split('T')[0];
      loadSavedMilestones();
    }

    function toggleCustomQuestion() {
      const type = document.getElementById('milestoneType').value;
      if (type === 'CUSTOM') {
        document.getElementById('presetSelectDiv').classList.add('hidden');
        document.getElementById('customQuestionDiv').classList.remove('hidden');
      } else {
        document.getElementById('presetSelectDiv').classList.remove('hidden');
        document.getElementById('customQuestionDiv').classList.add('hidden');
      }
    }

    async function saveNewMilestone() {
      if (!finalizedBaby.masterPassword) return alert("Master password not set");

      const type = document.getElementById('milestoneType').value;
      const eventDate = document.getElementById('mEventDate').value;
      const notes = document.getElementById('mNotes').value.trim();

      let eventTag = "";
      if (type === 'CUSTOM') {
        eventTag = document.getElementById('mCustomQuestion').value.trim();
        if (!eventTag) return alert(currentLang === 'hi' ? "कृपया अपना सवाल / घटना का शीर्षक लिखें" : "Please enter question/title");
      } else {
        const sel = document.getElementById('mPresetTag');
        eventTag = sel.options[sel.selectedIndex].text;
      }

      if (!notes) return alert(currentLang === 'hi' ? "कृपया उस पल की यादें या विवरण लिखें" : "Please record the story/details");

      await fetch('/api/milestones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          baby_id: finalizedBaby.name.toLowerCase().replace(/\\s+/g, '_') || "primary_baby",
          passphrase: finalizedBaby.masterPassword,
          event_tag: eventTag,
          details: { 
            title: eventTag, 
            notes: notes, 
            eventDate: eventDate,
            savedAt: new Date().toLocaleDateString('hi-IN') 
          }
        })
      });

      alert(currentLang === 'hi' ? "🎉 यह अनमोल याद वॉल्ट में AES-256 सुरक्षित सहेज ली गई!" : "🎉 Milestone securely saved to encrypted vault!");
      document.getElementById('mNotes').value = "";
      if (type === 'CUSTOM') document.getElementById('mCustomQuestion').value = "";
      loadSavedMilestones();
    }

    async function loadSavedMilestones() {
      const babyId = finalizedBaby.name.toLowerCase().replace(/\\s+/g, '_') || "primary_baby";
      const pwd = finalizedBaby.masterPassword;

      const res = await fetch(`/api/milestones/get?baby_id=${encodeURIComponent(babyId)}&pass=${encodeURIComponent(pwd)}`);
      const list = await res.json();
      currentSavedMilestones = list;
      const container = document.getElementById('albumView');
      container.innerHTML = "";

      if (list.length === 0) {
        container.innerHTML = `<p class="text-xs text-stone-400 text-center py-2">${currentLang === 'hi' ? 'अभी कोई याद सहेजी नहीं गई है। पहली याद ऊपर जोड़ें!' : 'No memories saved yet. Add your first memory above!'}</p>`;
        return;
      }

      list.forEach(item => {
        const d = item.data;
        container.innerHTML += `
          <div class="p-3 bg-white rounded-xl border border-stone-200 text-xs space-y-1 shadow-2xs">
            <div class="flex justify-between items-center">
              <span class="font-extrabold text-amber-900">${item.event_tag}</span>
              <span class="text-[10px] text-stone-400">${d.eventDate || d.savedAt || ''}</span>
            </div>
            <p class="text-stone-700 whitespace-pre-wrap">${d.notes || ''}</p>
          </div>`;
      });
    }

    function downloadAlbumPDF() {
      if (!finalizedBaby.name) {
        alert(currentLang === 'hi' ? "कृपया पहले एक नाम चुनें और प्रोफ़ाइल लॉक करें!" : "Please select a name and lock profile first!");
        return;
      }

      document.getElementById('pdfBabyName').innerText = finalizedBaby.name;
      document.getElementById('pdfBirthDate').innerText = `Date: ${finalizedBaby.date || document.getElementById('bDate').value}`;
      document.getElementById('pdfBirthTime').innerText = `Time: ${finalizedBaby.time || document.getElementById('bTime').value}`;
      document.getElementById('pdfBirthCity').innerText = `Place: ${finalizedBaby.city || document.getElementById('bCity').value}`;

      document.getElementById('pdfLagna').innerText = document.getElementById('resLagna').innerText || '-';
      document.getElementById('pdfRashi').innerText = document.getElementById('resRashi').innerText || '-';
      document.getElementById('pdfNakshatra').innerText = `${document.getElementById('resNakshatra').innerText || '-'} (${document.getElementById('resPada').innerText || '-'})`;
      document.getElementById('pdfAkshar').innerText = document.getElementById('resAkshar').innerText || '-';

      const chartCloneContainer = document.getElementById('pdfChartClone');
      chartCloneContainer.innerHTML = "";
      const originalBox = document.getElementById('mainKundliBox');
      if (originalBox) {
        const clonedBox = originalBox.cloneNode(true);
        clonedBox.id = "clonedPdfBox";
        chartCloneContainer.appendChild(clonedBox);
      }

      const pdfMilestoneContainer = document.getElementById('pdfMilestoneList');
      pdfMilestoneContainer.innerHTML = "";
      if (currentSavedMilestones.length === 0) {
        pdfMilestoneContainer.innerHTML = "<p style='color: #78716C; font-style: italic;'>No milestones recorded in vault yet.</p>";
      } else {
        currentSavedMilestones.forEach(item => {
          const d = item.data;
          pdfMilestoneContainer.innerHTML += `
            <div style="background: #FBF9F5; border: 1px solid #E7E5E4; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; font-weight: bold; color: #78350F; margin-bottom: 4px;">
                <span>${item.event_tag}</span>
                <span style="font-size: 10px; color: #78716C;">${d.eventDate || d.savedAt || ''}</span>
              </div>
              <p style="margin: 0; color: #44403C; line-height: 1.4; white-space: pre-wrap;">${d.notes || ''}</p>
            </div>
          `;
        });
      }

      const certElement = document.getElementById('pdfCertTemplate');
      const opt = {
        margin: [8, 8, 8, 8],
        filename: `${finalizedBaby.name}_Janmapatri_Album.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };

      html2pdf().set(opt).from(certElement).save();
    }

    // BACKUP & RESTORE JAVASCRIPT FUNCTIONS
    async function downloadBackupFile() {
      try {
        const res = await fetch('/api/backup/export');
        const data = await res.json();
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `NanhiDuniya_Encrypted_Backup_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        alert("बैकअप डाउनलोड करने में समस्या आई: " + err.message);
      }
    }

    async function uploadRestoreFile(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async function(e) {
        try {
          const jsonContent = JSON.parse(e.target.result);
          const res = await fetch('/api/backup/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jsonContent)
          });
          const result = await res.json();
          alert(`🎉 बैकअप सफलतापूर्वक रीस्टोर हो गया! (${result.imported} रिकॉर्ड जुड़े)`);
          loadSavedMilestones();
        } catch (err) {
          alert("अमान्य बैकअप फ़ाइल: " + err.message);
        }
      };
      reader.readAsText(file);
    }
  </script>
</body>
</html>
"""

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(url.query)

        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))

        elif url.path == "/api/kundli":
            y = int(params.get('y', [2026])[0])
            m = int(params.get('m', [9])[0])
            d = int(params.get('d', [22])[0])
            h = int(params.get('h', [11])[0])
            mn = int(params.get('min', [5])[0])
            city = params.get('city', ['Gondia'])[0]
            res = get_kundli_details(y, m, d, h, mn, city)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif url.path == "/api/ai-names":
            letter = params.get('letter', ['तू'])[0]
            gender = params.get('gender', ['All'])[0]
            mode = params.get('mode', ['strict'])[0]
            names = generate_ai_names(letter, gender, mode)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(names).encode('utf-8'))

        elif url.path == "/api/milestones/get":
            baby_id = params.get('baby_id', ['primary_baby'])[0]
            pwd = params.get('pass', [''])[0]
            data = get_milestones(baby_id, pwd)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        elif url.path == "/api/backup/export":
            backup = export_raw_backup()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(backup).encode('utf-8'))

    def do_POST(self):
        if self.path == "/api/milestones/add":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            payload = json.loads(body.decode('utf-8'))
            add_milestone(
                payload['baby_id'],
                payload['passphrase'],
                payload['event_tag'],
                payload['details']
            )
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

        elif self.path == "/api/backup/import":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            payload = json.loads(body.decode('utf-8'))
            count = import_raw_backup(payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "imported": count}).encode('utf-8'))

if __name__ == "__main__":
    print("\n🌸 Nanhi Duniya Live at: http://localhost:8000")
    server = HTTPServer(('0.0.0.0', 8000), SimpleServer)
    server.serve_forever()

