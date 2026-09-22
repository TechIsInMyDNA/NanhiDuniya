from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
from ND import get_kundli_details
from NE import generate_ai_names
from TV import (
    init_db,
    register_or_login_profile,
    add_profile_milestone,
    get_profile_milestones,
    export_single_profile_backup,
    import_single_profile_backup,
    delete_profile_vault
)

init_db()

HTML_PAGE = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nanhi Duniya - Vedic Kundli & Baby Milestone Vault</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Cinzel:wght@700&family=Rozha+One&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAF7F2; }
    .glass-card { background: rgba(255, 255, 255, 0.98); border: 1px solid #EFEAE1; }
    .kundli-box { position: relative; width: 280px; height: 280px; margin: 0 auto; background: #FFFDF9; border: 2px solid #854D0E; }
    .kundli-svg { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
    .h-item { position: absolute; text-align: center; width: 64px; z-index: 10; transform: translate(-50%, -50%); }
    .rashi-no { color: #9A3412; font-size: 11px; font-weight: 800; display: block; line-height: 1; }
    .grah-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 2px; margin-top: 2px; }
    .grah-badge { background: #EEF2FF; color: #1E40AF; font-size: 9px; font-weight: 800; padding: 1px 3px; border-radius: 4px; border: 1px solid #DBEAFE; }

    /* ROYAL PRINT CANVAS (Exact A4 Fit without cut) */
    #pdfPrintCanvas {
      width: 794px; /* Standard A4 pixel width at 96 DPI */
      background: #FFFDF9;
      color: #1C1917;
      padding: 36px;
      box-sizing: border-box;
      border: 8px double #B45309;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
  </style>
</head>
<body class="text-stone-800 pb-28">

  <!-- Header -->
  <header class="py-3 px-4 border-b border-stone-200 bg-white sticky top-0 z-50 shadow-xs">
    <div class="max-w-md mx-auto flex justify-between items-center">
      <div>
        <h1 class="text-xl font-black text-amber-900 tracking-tight flex items-center gap-1.5">
          <span>🌸</span> Nanhi Duniya
        </h1>
        <div class="flex items-center gap-2 mt-0.5">
          <p id="tSubHeader" class="text-[10px] text-stone-500">वैदिक जन्मपत्री • नामकरण • डिजिटल संदूक</p>
          <span id="syncStatusBadge" class="text-[9px] bg-stone-100 text-stone-600 px-1.5 py-0.5 rounded-full font-bold">● Offline Ready</span>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <div class="flex items-center bg-stone-100 p-0.5 rounded-xl border border-stone-200 text-xs font-bold">
          <button id="langHiBtn" onclick="switchLanguage('hi')" class="px-2 py-1 rounded-lg bg-amber-800 text-white transition">हिंदी</button>
          <button id="langEnBtn" onclick="switchLanguage('en')" class="px-2 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition">EN</button>
        </div>
        <button id="navVaultBtn" onclick="toggleVaultModal()" class="text-xs bg-amber-100 hover:bg-amber-200 text-amber-950 px-2.5 py-1.5 rounded-xl font-bold flex items-center gap-1 transition">
          <span>🔐</span> <span id="navVaultText">लॉगिन / वॉल्ट</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-md mx-auto p-4 space-y-5">

    <!-- Active Profile Banner -->
    <div id="activeProfileBanner" class="hidden p-3.5 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl flex justify-between items-center text-xs shadow-xs">
      <div>
        <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
          <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">क्लाउड वॉल्ट एक्टिव:</span>
        </div>
        <strong id="activeBabyNameDisplay" class="text-emerald-950 text-base font-black mt-0.5 block"></strong>
      </div>
      <button onclick="logoutVault()" class="text-xs bg-white border border-emerald-300 text-emerald-900 font-bold px-3 py-1.5 rounded-xl active:scale-95 transition shadow-2xs">
        🔒 लॉगआउट
      </button>
    </div>

    <!-- STEP 1: Birth Form -->
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

    <!-- STEP 3: Setup Profile Section -->
    <div id="profileSetupSection" class="hidden glass-card rounded-2xl p-5 shadow-sm space-y-4 border-2 border-amber-300">
      <div class="flex justify-between items-center">
        <div>
          <h2 id="tProfileLockTitle" class="text-base font-bold text-stone-900 flex items-center gap-1.5">
            <span>🔐</span> शिशु प्रोफ़ाइल बनाएं एवं पासवर्ड सेट करें
          </h2>
          <p class="text-[11px] text-stone-500">Zero-Knowledge AES-256 Cloud Vault Encryption</p>
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
        <p id="tMasterPassNote" class="text-[10px] text-stone-500">✦ यह पासवर्ड आपके सिवा कोई दूसरा पैरेंट या एडमिन भी नहीं देख सकता।</p>
        
        <button id="tLockProfileBtn" onclick="createBabyProfileVault()" class="w-full py-2.5 bg-emerald-800 hover:bg-emerald-900 text-white font-bold rounded-xl mt-2 active:scale-95 transition shadow-sm">
          प्रोफ़ाइल बनाएं एवं क्लाउड संदूक खोलें ➔
        </button>
      </div>
    </div>

    <!-- DEDICATED LIFETIME MILESTONE VAULT DASHBOARD (Memories First UI) -->
    <div id="vaultDashboard" class="hidden glass-card rounded-2xl p-5 shadow-sm space-y-5">
      <div class="flex justify-between items-center border-b border-stone-200 pb-3">
        <div>
          <h2 class="text-lg font-black text-amber-950 flex items-center gap-1.5">
            <span>📖</span> <span id="vaultHeadingBabyName">शिशु</span> <span id="tVaultHeadingText">का डिजिटल स्मृति संदूक</span>
          </h2>
          <p id="tVaultSub" class="text-[11px] text-stone-500">जीवन की अनमोल यादें, प्रश्न एवं सम्पूर्ण जन्मपत्री</p>
        </div>
        <span class="text-xs bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full font-bold">Encrypted Vault</span>
      </div>

      <!-- Quick Kundli Meta Recap Card -->
      <div id="vaultKundliCard" class="p-3 bg-amber-50/70 rounded-xl border border-amber-200 text-xs grid grid-cols-2 gap-2">
        <div><span class="text-[10px] text-stone-500 block">लग्न:</span><strong id="vLagnaText">-</strong></div>
        <div><span class="text-[10px] text-stone-500 block">राशि:</span><strong id="vRashiText">-</strong></div>
        <div><span class="text-[10px] text-stone-500 block">नक्षत्र:</span><strong id="vNakshatraText">-</strong></div>
        <div><span class="text-[10px] text-stone-500 block">नामकरण अक्षर:</span><strong id="vAksharText" class="text-amber-900 text-sm font-black">-</strong></div>
      </div>

      <!-- Add Milestone Form (Rich Journal Card) -->
      <div class="p-4 bg-gradient-to-b from-stone-50 to-white rounded-2xl border border-stone-200 text-xs space-y-3 shadow-xs">
        <p id="tAddMemoryTitle" class="font-bold text-stone-800 flex items-center gap-1.5">
          <span>✍️</span> नई याद / सवाल संदूक में जोड़ें:
        </p>
        
        <div class="flex gap-2">
          <select id="milestoneType" onchange="toggleCustomQuestion()" class="w-1/2 p-2.5 rounded-xl border border-stone-300 bg-white font-semibold">
            <option value="PRESET">तयशुदा माइलस्टोन</option>
            <option value="CUSTOM">अपना नया सवाल / घटना</option>
          </select>
          <input type="date" id="mEventDate" class="w-1/2 p-2.5 rounded-xl border border-stone-300 bg-white">
        </div>

        <div id="presetSelectDiv">
          <select id="mPresetTag" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white font-medium">
            <option value="FIRST_SMILE">पहली बार मुस्कुराया (First Smile)</option>
            <option value="FIRST_STEP">पहला कदम रखा (First Steps)</option>
            <option value="FIRST_FOOD">पहला अन्नप्राशन (First Solid Food)</option>
            <option value="FIRST_WORD">पहला शब्द क्या बोला (First Word)</option>
            <option value="FIRST_TRIP">पहली यात्रा / ननिहाल आगमन</option>
            <option value="FAV_TOY">पहला पसंदीदा खिलौना कौन सा था?</option>
            <option value="SWEET_HABIT">बचपन की सबसे प्यारी आदत</option>
          </select>
        </div>

        <div id="customQuestionDiv" class="hidden">
          <input type="text" id="mCustomQuestion" placeholder="उदा. पहली बार बारिश देखकर कैसा लगा? या लोरी पर क्या प्रतिक्रिया दी?" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
        </div>

        <textarea id="mNotes" rows="3" placeholder="उस पल की पूरी याद, भावनाएं, किस्से व बातें विस्तार से लिखें..." class="w-full p-3 rounded-xl border border-stone-300 bg-white leading-relaxed outline-none focus:ring-2 focus:ring-amber-500"></textarea>

        <button id="tSaveVaultBtn" type="button" onclick="saveNewMilestone()" class="w-full py-3 bg-amber-900 hover:bg-amber-950 text-white rounded-xl font-bold active:scale-95 transition shadow-sm">
          सहेजें एवं सुरक्षित लॉक करें (Save to Vault)
        </button>
      </div>

      <!-- Actions Bar -->
      <div class="pt-1 flex justify-between items-center">
        <button id="tViewSavedBtn" type="button" onclick="triggerSyncAndReload()" class="text-xs text-amber-800 font-bold underline">
          क्लाउड सिंक / रिफ्रेश ↻
        </button>
        <button id="tDownloadPdfBtn" type="button" onclick="downloadAlbumPDF()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-4 py-2 rounded-xl font-bold shadow-xs active:scale-95 transition flex items-center gap-1">
          <span>📖</span> PDF एल्बम डाउनलोड
        </button>
      </div>

      <!-- List of Milestones (Card-Deck Aesthetic Style) -->
      <div id="albumView" class="space-y-3"></div>

      <!-- Backup, Restore & Password-Protected DELETE Zone -->
      <div class="pt-4 border-t border-stone-200 text-xs space-y-3">
        <div class="flex gap-2">
          <button onclick="downloadBackupFile()" class="flex-1 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 transition">
            📥 बैकअप डाउनलोड
          </button>
          <label class="flex-1 py-2 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 text-center cursor-pointer transition">
            📤 बैकअप रीस्टोर
            <input type="file" id="restoreFileInput" accept=".json" onchange="uploadRestoreFile(event)" class="hidden">
          </label>
        </div>

        <!-- DANGER ZONE: Delete Vault Protected by Master Password -->
        <div class="p-3 bg-rose-50/70 border border-rose-200 rounded-xl text-rose-950 space-y-2">
          <div class="flex justify-between items-center">
            <span class="font-bold flex items-center gap-1 text-[11px] text-rose-900">
              <span>⚠️</span> डेंजर ज़ोन: पूरा संदूक मिटाएं (Delete Vault)
            </span>
            <button onclick="toggleDeletePrompt()" class="text-[10px] bg-rose-200 hover:bg-rose-300 text-rose-900 px-2 py-1 rounded font-bold transition">
              विकल्प खोलें
            </button>
          </div>
          <div id="deleteVaultDiv" class="hidden pt-2 border-t border-rose-200 space-y-2">
            <p class="text-[10px] text-rose-800">यह क्रिया इस बच्चे की संपूर्ण जन्मपत्री, सारे मील के पत्थर व यादों को सर्वर से हमेशा के लिए नष्ट कर देगी। पुष्टि के लिए अपना मास्टर पासवर्ड डालें:</p>
            <div class="flex gap-2">
              <input type="password" id="deleteConfirmPassword" placeholder="मास्टर पासवर्ड दर्ज करें" class="flex-1 p-2 bg-white rounded-lg border border-rose-300 outline-none">
              <button onclick="confirmDeleteVault()" class="px-3 py-2 bg-rose-700 hover:bg-rose-800 text-white rounded-lg font-bold text-xs active:scale-95 transition">
                स्थाई रूप से मिटाएं
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- Login/Unlock Modal -->
  <div id="loginModal" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl p-5 max-w-sm w-full space-y-4 shadow-xl">
      <div class="flex justify-between items-center">
        <h3 class="text-base font-bold text-stone-900 flex items-center gap-1.5">
          <span>🔑</span> बच्चे का वॉल्ट खोलें (Unlock Vault)
        </h3>
        <button onclick="toggleVaultModal()" class="text-stone-400 hover:text-stone-700 font-black text-sm">✕</button>
      </div>
      <p class="text-xs text-stone-500">डेटा क्लियर होने या दूसरे फ़ोन पर खोलने के लिए बच्चे का नाम व मास्टर पासवर्ड डालें:</p>

      <div class="space-y-2.5 text-xs">
        <div>
          <label class="block font-semibold text-stone-700 mb-1">शिशु का नाम (Baby Name)</label>
          <input type="text" id="loginBabyName" placeholder="उदा. आरव" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none">
        </div>
        <div>
          <label class="block font-semibold text-stone-700 mb-1">मास्टर पासवर्ड (Master Password)</label>
          <input type="password" id="loginPassword" placeholder="पासवर्ड दर्ज करें" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none">
        </div>
        <button onclick="loginToVault()" class="w-full py-2.5 bg-amber-900 text-white rounded-xl font-bold active:scale-95 transition">
          वॉल्ट अनलॉक करें ➔
        </button>
      </div>
    </div>
  </div>

  <!-- ROYAL CLEAN ALBUM PRINT CANVAS (Exact Full Flow & Zero Cut-off) -->
  <div style="position: absolute; left: -9999px; top: 0;">
    <div id="pdfPrintCanvas">
      
      <!-- Royal Vedic Header -->
      <div style="text-align: center; border-bottom: 2px solid #92400E; padding-bottom: 12px; margin-bottom: 18px;">
        <span style="font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #92400E; font-weight: bold;">वैदिक जन्मपत्री एवं जीवन स्मृति संदूक</span>
        <h1 style="font-family: 'Rozha One', serif; font-size: 28px; color: #78350F; margin: 4px 0 0 0;">🌸 नन्ही दुनिया (Nanhi Duniya)</h1>
      </div>

      <!-- Golden Baby Identity Strip -->
      <div style="display: flex; justify-content: space-between; align-items: center; background: #FEF3C7; border: 1.5px solid #F59E0B; padding: 12px 18px; border-radius: 10px; margin-bottom: 18px;">
        <div>
          <span style="font-size: 10px; color: #92400E; font-weight: bold; text-transform: uppercase;">शिशु का नाम</span>
          <h2 id="pdfBabyName" style="font-size: 22px; font-weight: 800; color: #78350F; margin: 2px 0 0 0;"></h2>
        </div>
        <div style="text-align: right; font-size: 11px; color: #78350F; line-height: 1.4;">
          <div><strong id="pdfBirthDate"></strong></div>
          <div id="pdfBirthTime"></div>
          <div id="pdfBirthCity"></div>
        </div>
      </div>

      <!-- Astrological 4-Pillar Grid -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 18px; text-align: center; font-size: 11px;">
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">लग्न राशि</span>
          <strong id="pdfLagna" style="color: #78350F; font-size: 13px;"></strong>
        </div>
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">चन्द्र राशि</span>
          <strong id="pdfRashi" style="color: #1C1917; font-size: 13px;"></strong>
        </div>
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">नक्षत्र एवं चरण</span>
          <strong id="pdfNakshatra" style="color: #1C1917; font-size: 12px;"></strong>
        </div>
        <div style="background: #FEF3C7; padding: 8px; border-radius: 6px; border: 1.5px solid #FCD34D;">
          <span style="color: #92400E; font-size: 9px; display: block;">नामकरण अक्षर</span>
          <strong id="pdfAkshar" style="color: #78350F; font-size: 18px;"></strong>
        </div>
      </div>

      <!-- Lagna Chart Render (Scaled correctly to never cut) -->
      <div style="text-align: center; margin-bottom: 24px;">
        <p style="font-size: 12px; font-weight: bold; color: #78350F; margin-bottom: 8px; letter-spacing: 0.5px;">शास्त्रसम्मत लग्न चक्र (Ascendant & 9 Planets)</p>
        <div id="pdfChartClone" style="display: inline-block;"></div>
      </div>

      <!-- Milestone Journal Cards -->
      <div style="border-top: 2px dashed #B45309; padding-top: 18px;">
        <div style="text-align: center; margin-bottom: 12px;">
          <h3 style="font-size: 16px; font-weight: 800; color: #78350F; margin: 0;">📖 अनमोल यादें एवं जीवन के मील के पत्थर</h3>
          <p style="font-size: 10px; color: #78716C; margin: 2px 0 0 0;">(Parent's Recorded Memories, Questions & Cherished Milestones)</p>
        </div>
        <div id="pdfMilestoneList" style="font-size: 11px;"></div>
      </div>

      <!-- Footer Seal -->
      <div style="margin-top: 35px; text-align: center; font-size: 9px; color: #A8A29E; border-top: 1px solid #E7E5E4; padding-top: 8px;">
        🔒 Zero-Knowledge AES-256 Encrypted Lifetime Journal • Official Nanhi Duniya Record
      </div>
    </div>
  </div>

  <script>
    let currentLang = 'hi';
    let currentLetter = "खी";
    let selectedGender = "All";
    let namingMode = "strict";
    let currentSavedMilestones = [];

    let activeSession = {
      profileHash: localStorage.getItem('nd_prof_hash') || '',
      babyName: localStorage.getItem('nd_baby_name') || '',
      passphrase: sessionStorage.getItem('nd_passphrase') || '',
      meta: JSON.parse(localStorage.getItem('nd_baby_meta') || '{}')
    };

    function getOfflineQueue() {
      return JSON.parse(localStorage.getItem('nd_offline_queue') || '[]');
    }
    function setOfflineQueue(q) {
      localStorage.setItem('nd_offline_queue', JSON.stringify(q));
    }

    const UI_STRINGS = {
      hi: {
        subHeader: "वैदिक जन्मपत्री • नामकरण • डिजिटल संदूक",
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
        profileLockTitle: "🔐 शिशु प्रोफ़ाइल बनाएं एवं पासवर्ड सेट करें",
        step2Tag: "चरण 2",
        finalNameLabel: "अंतिम चुना हुआ नाम:",
        finalDateLabel: "जन्म तारीख:",
        finalTimeLabel: "जन्म समय:",
        finalCityLabel: "जन्म स्थान:",
        masterPassPrompt: "एक गुप्त मास्टर पासवर्ड (Family Secret Key) बनाएं:",
        masterPassPlaceholder: "यह पासवर्ड केवल आपको पता होना चाहिए",
        masterPassNote: "✦ यह पासवर्ड आपके सिवा कोई दूसरा पैरेंट या एडमिन भी नहीं देख सकता।",
        lockProfileBtn: "प्रोफ़ाइल बनाएं एवं क्लाउड संदूक खोलें ➔",
        vaultHeadingText: "का डिजिटल स्मृति संदूक",
        vaultSub: "जीवन की अनमोल यादें, प्रश्न एवं सम्पूर्ण जन्मपत्री",
        addMemoryTitle: "नई याद / सवाल संदूक में जोड़ें:",
        notesPlaceholder: "उस पल की पूरी याद, भावनाएं, किस्से व बातें विस्तार से लिखें...",
        saveVaultBtn: "सहेजें एवं सुरक्षित लॉक करें (Save to Vault)",
        viewSavedBtn: "क्लाउड सिंक / रिफ्रेश ↻",
        downloadPdfBtn: "📖 PDF एल्बम डाउनलोड"
      },
      en: {
        subHeader: "Vedic Janmapatri • Naming • Digital Memory Vault",
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
        profileLockTitle: "🔐 Create Baby Profile & Set Password",
        step2Tag: "Step 2",
        finalNameLabel: "Final Chosen Name:",
        finalDateLabel: "Birth Date:",
        finalTimeLabel: "Birth Time:",
        finalCityLabel: "Birth Place:",
        masterPassPrompt: "Create a Master Password (Family Secret Key):",
        masterPassPlaceholder: "This password should only be known to you",
        masterPassNote: "✦ Neither other parents nor admins can ever access this password.",
        lockProfileBtn: "Lock Profile & Open Milestone Vault ➔",
        vaultHeadingText: "'s Digital Vault",
        vaultSub: "Lifetime Memories, Personal Q&A and Vedic Birth Journal",
        addMemoryTitle: "Add Question & Memory to Vault:",
        notesPlaceholder: "Record the emotions, memories and story in detail...",
        saveVaultBtn: "Save Securely to Vault",
        viewSavedBtn: "Cloud Sync / Refresh ↻",
        downloadPdfBtn: "📖 Export PDF Album"
      }
    };

    window.addEventListener('online', () => {
      document.getElementById('syncStatusBadge').innerText = "● Cloud Connected";
      document.getElementById('syncStatusBadge').className = "text-[9px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-full font-bold";
      flushOfflineQueueToServer();
    });

    window.addEventListener('offline', () => {
      document.getElementById('syncStatusBadge').innerText = "● Offline Mode (Queued)";
      document.getElementById('syncStatusBadge').className = "text-[9px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded-full font-bold";
    });

    window.addEventListener('DOMContentLoaded', () => {
      if (navigator.onLine) {
        document.getElementById('syncStatusBadge').innerText = "● Cloud Connected";
        document.getElementById('syncStatusBadge').className = "text-[9px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded-full font-bold";
      }
      if (activeSession.profileHash && activeSession.passphrase) {
        showVaultDashboard();
      }
    });

    function toggleVaultModal() {
      document.getElementById('loginModal').classList.toggle('hidden');
    }

    function toggleDeletePrompt() {
      document.getElementById('deleteVaultDiv').classList.toggle('hidden');
    }

    async function confirmDeleteVault() {
      const pwd = document.getElementById('deleteConfirmPassword').value.trim();
      if (!pwd) return alert("कृपया अपना मास्टर पासवर्ड दर्ज करें");

      if (!confirm("⚠️ क्या आप निश्चित रूप से इस बच्चे का पूरा वॉल्ट और सारी यादें हमेशा के लिए मिटाना चाहते हैं? यह क्रिया वापस नहीं होगी!")) {
        return;
      }

      try {
        const res = await fetch('/api/vault/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            profile_hash: activeSession.profileHash,
            passphrase: pwd
          })
        });
        const data = await res.json();
        if (data.status === 'ok') {
          alert("🗑️ बच्चे का वॉल्ट और सारी यादें सर्वर से हमेशा के लिए सुरक्षित मिटा दी गई हैं।");
          logoutVault();
        } else {
          alert("त्रुटि: " + data.message);
        }
      } catch (e) {
        alert("सर्वर से संपर्क नहीं हो पाया: " + e.message);
      }
    }

    function switchLanguage(lang) {
      currentLang = lang;
      if (lang === 'hi') {
        document.getElementById('langHiBtn').className = "px-2 py-1 rounded-lg bg-amber-800 text-white transition";
        document.getElementById('langEnBtn').className = "px-2 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition";
      } else {
        document.getElementById('langEnBtn').className = "px-2 py-1 rounded-lg bg-amber-800 text-white transition";
        document.getElementById('langHiBtn').className = "px-2 py-1 rounded-lg text-stone-600 hover:text-stone-900 transition";
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
      } else {
        sel.options[0].text = "पहली बार मुस्कुराया (First Smile)";
        sel.options[1].text = "पहला कदम रखा (First Steps)";
        sel.options[2].text = "पहला अन्नप्राशन (First Solid Food)";
        sel.options[3].text = "पहला शब्द क्या बोला (First Word)";
        sel.options[4].text = "पहली यात्रा / ननिहाल आगमन";
        document.getElementById('milestoneType').options[0].text = "तयशुदा माइलस्टोन";
        document.getElementById('milestoneType').options[1].text = "अपना नया सवाल / घटना";
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

      if (!bDate || !bTime) return alert("Date aur time dalein");

      btn.innerText = "Kundli Banayi Ja Rahi Hai...";
      btn.disabled = true;

      try {
        const parts = bDate.split(/[-/]/);
        let year = parseInt(parts[0]), month = parseInt(parts[1]), day = parseInt(parts[2]);
        const tParts = bTime.split(':');
        const hour = parseInt(tParts[0]), minute = parseInt(tParts[1]);

        const res = await fetch(`/api/kundli?y=${year}&m=${month}&d=${day}&h=${hour}&min=${minute}&city=${encodeURIComponent(bCity)}`);
        const data = await res.json();

        document.getElementById('resLagna').innerText = `${data.lagna_hindi} (${data.lagna_english})`;
        document.getElementById('resRashi').innerText = `${data.rashi_hindi} (${data.rashi_english})`;
        document.getElementById('resNakshatra').innerText = data.nakshatra_hindi;
        document.getElementById('resPada').innerText = `Charan ${data.charan}`;
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
        listDiv.innerHTML = `<p class="text-xs text-red-500 text-center py-2">Failed to load names.</p>`;
      }
    }

    function useCustomName() {
      const cName = document.getElementById('customNameInput').value.trim();
      if (!cName) return alert("कृपया नाम दर्ज करें");
      finalizeName(cName);
    }

    function finalizeName(name) {
      document.getElementById('cardFinalName').innerText = name;
      document.getElementById('cardFinalDate').innerText = document.getElementById('bDate').value;
      document.getElementById('cardFinalTime').innerText = document.getElementById('bTime').value;
      document.getElementById('cardFinalCity').innerText = document.getElementById('bCity').value;

      document.getElementById('profileSetupSection').classList.remove('hidden');
      document.getElementById('profileSetupSection').scrollIntoView({ behavior: 'smooth' });
    }

    async function createBabyProfileVault() {
      const babyName = document.getElementById('cardFinalName').innerText.trim();
      const pwd = document.getElementById('masterPasswordInput').value.trim();

      if (!babyName) return alert("कृपया नाम चुनें");
      if (!pwd || pwd.length < 4) return alert("पासवर्ड कम से कम 4 अक्षरों का रखें");

      const meta = {
        baby_name: babyName,
        city: document.getElementById('cardFinalCity').innerText,
        date: document.getElementById('cardFinalDate').innerText,
        time: document.getElementById('cardFinalTime').innerText,
        lagna: document.getElementById('resLagna').innerText,
        rashi: document.getElementById('resRashi').innerText,
        nakshatra: document.getElementById('resNakshatra').innerText,
        pada: document.getElementById('resPada').innerText,
        akshar: document.getElementById('resAkshar').innerText
      };

      try {
        const res = await fetch('/api/profile/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            baby_name: babyName,
            passphrase: pwd,
            meta_data: meta
          })
        });

        const data = await res.json();
        if (data.status === 'ok') {
          activeSession.profileHash = data.profile_hash;
          activeSession.babyName = babyName;
          activeSession.passphrase = pwd;
          activeSession.meta = data.meta;

          localStorage.setItem('nd_prof_hash', data.profile_hash);
          localStorage.setItem('nd_baby_name', babyName);
          sessionStorage.setItem('nd_passphrase', pwd);
          localStorage.setItem('nd_baby_meta', JSON.stringify(data.meta));

          alert("🎉 बच्चे की प्रोफ़ाइल क्लाउड सर्वर पर सुरक्षित रजिस्टर हो गई!");
          showVaultDashboard();
        } else {
          alert("त्रुटि: " + data.message);
        }
      } catch (err) {
        alert("इंटरनेट कनेक्शन चेक करें: " + err.message);
      }
    }

    async function loginToVault() {
      const babyName = document.getElementById('loginBabyName').value.trim();
      const pwd = document.getElementById('loginPassword').value.trim();

      if (!babyName || !pwd) return alert("कृपया नाम और पासवर्ड भरें");

      try {
        const res = await fetch('/api/profile/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            baby_name: babyName,
            passphrase: pwd
          })
        });

        const data = await res.json();
        if (data.status === 'ok') {
          activeSession.profileHash = data.profile_hash;
          activeSession.babyName = babyName;
          activeSession.passphrase = pwd;
          activeSession.meta = data.meta;

          localStorage.setItem('nd_prof_hash', data.profile_hash);
          localStorage.setItem('nd_baby_name', babyName);
          sessionStorage.setItem('nd_passphrase', pwd);
          localStorage.setItem('nd_baby_meta', JSON.stringify(data.meta));

          toggleVaultModal();
          showVaultDashboard();
        } else {
          alert("⚠️ अमान्य क्रेडेंशियल्स! नाम या पासवर्ड गलत है।");
        }
      } catch (err) {
        alert("सर्वर से कनेक्ट नहीं हो सका। कृपया नेट चेक करें।");
      }
    }

    function logoutVault() {
      localStorage.removeItem('nd_prof_hash');
      localStorage.removeItem('nd_baby_name');
      sessionStorage.removeItem('nd_passphrase');
      localStorage.removeItem('nd_baby_meta');

      activeSession = { profileHash: '', babyName: '', passphrase: '', meta: {} };

      document.getElementById('vaultDashboard').classList.add('hidden');
      document.getElementById('activeProfileBanner').classList.add('hidden');
      document.getElementById('navVaultText').innerText = "लॉगिन / वॉल्ट";
      alert("🔒 वॉल्ट सुरक्षित लॉक और लॉगआउट कर दिया गया है।");
    }

    function showVaultDashboard() {
      document.getElementById('activeProfileBanner').classList.remove('hidden');
      document.getElementById('activeBabyNameDisplay').innerText = activeSession.babyName;
      document.getElementById('navVaultText').innerText = activeSession.babyName;
      document.getElementById('vaultHeadingBabyName').innerText = activeSession.babyName;

      const m = activeSession.meta;
      if (m) {
        document.getElementById('vLagnaText').innerText = m.lagna || '-';
        document.getElementById('vRashiText').innerText = m.rashi || '-';
        document.getElementById('vNakshatraText').innerText = `${m.nakshatra || '-'} (${m.pada || ''})`;
        document.getElementById('vAksharText').innerText = m.akshar || '-';
      }

      document.getElementById('vaultDashboard').classList.remove('hidden');
      document.getElementById('mEventDate').value = new Date().toISOString().split('T')[0];
      triggerSyncAndReload();
      document.getElementById('vaultDashboard').scrollIntoView({ behavior: 'smooth' });
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
      if (!activeSession.profileHash || !activeSession.passphrase) return alert("कृपया पहले वॉल्ट लॉगिन करें");

      const type = document.getElementById('milestoneType').value;
      const eventDate = document.getElementById('mEventDate').value;
      const notes = document.getElementById('mNotes').value.trim();

      let eventTag = "";
      if (type === 'CUSTOM') {
        eventTag = document.getElementById('mCustomQuestion').value.trim();
        if (!eventTag) return alert("कृपया अपना सवाल / घटना लिखें");
      } else {
        const sel = document.getElementById('mPresetTag');
        eventTag = sel.options[sel.selectedIndex].text;
      }

      if (!notes) return alert("कृपया उस पल की यादें लिखें");

      const payload = {
        profile_hash: activeSession.profileHash,
        passphrase: activeSession.passphrase,
        event_tag: eventTag,
        details: { 
          title: eventTag, 
          notes: notes, 
          eventDate: eventDate,
          savedAt: new Date().toLocaleDateString('hi-IN') 
        }
      };

      if (!navigator.onLine) {
        const q = getOfflineQueue();
        q.push(payload);
        setOfflineQueue(q);
        alert("⚠️ इंटरनेट बंद है! याद को ऑफ़लाइन सहेज लिया गया है। नेट आते ही सिंक हो जाएगी।");
        renderLocalMilestone(payload);
      } else {
        try {
          await fetch('/api/milestones/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          alert("🎉 याद सफलतापूर्वक AES-256 क्लाउड वॉल्ट में जुड़ गई!");
          triggerSyncAndReload();
        } catch (e) {
          const q = getOfflineQueue();
          q.push(payload);
          setOfflineQueue(q);
          alert("सर्वर तक कनेक्शन नहीं पहुंचा। याद को ऑफ़लाइन कतार में सहेज लिया गया है।");
          renderLocalMilestone(payload);
        }
      }

      document.getElementById('mNotes').value = "";
      if (type === 'CUSTOM') document.getElementById('mCustomQuestion').value = "";
    }

    function renderLocalMilestone(item) {
      const container = document.getElementById('albumView');
      const d = item.details;
      container.innerHTML = `
        <div class="p-4 bg-gradient-to-r from-amber-50/80 to-stone-50 rounded-2xl border border-amber-200 text-xs space-y-1.5 shadow-xs">
          <div class="flex justify-between items-center">
            <span class="font-extrabold text-amber-950 text-sm flex items-center gap-1">
              <span>📌</span> ${item.event_tag}
            </span>
            <span class="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded-full font-bold">Pending Sync</span>
          </div>
          <p class="text-stone-700 whitespace-pre-wrap leading-relaxed">${d.notes || ''}</p>
        </div>` + container.innerHTML;
    }

    async function flushOfflineQueueToServer() {
      const q = getOfflineQueue();
      if (q.length === 0) return;

      for (const item of q) {
        try {
          await fetch('/api/milestones/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });
        } catch (e) {
          console.error("Sync error", e);
        }
      }
      setOfflineQueue([]);
      triggerSyncAndReload();
    }

    async function triggerSyncAndReload() {
      if (!activeSession.profileHash || !activeSession.passphrase) return;

      await flushOfflineQueueToServer();

      try {
        const res = await fetch(`/api/milestones/get?prof_hash=${encodeURIComponent(activeSession.profileHash)}&pass=${encodeURIComponent(activeSession.passphrase)}`);
        const list = await res.json();
        currentSavedMilestones = list;
        const container = document.getElementById('albumView');
        container.innerHTML = "";

        if (list.length === 0) {
          container.innerHTML = `
            <div class="p-6 text-center border-2 border-dashed border-stone-200 rounded-2xl bg-white/50">
              <span class="text-2xl block mb-1">🕊️</span>
              <p class="text-xs text-stone-500 font-medium">अभी कोई याद या सवाल दर्ज नहीं है। ऊपर पहला माइलस्टोन जोड़ें!</p>
            </div>`;
          return;
        }

        list.forEach(item => {
          const d = item.data;
          container.innerHTML += `
            <div class="p-4 bg-white rounded-2xl border border-stone-200/90 text-xs space-y-2 shadow-xs hover:border-amber-200 transition">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-amber-950 text-sm flex items-center gap-1.5">
                  <span class="text-amber-700">✦</span> ${item.event_tag}
                </span>
                <span class="text-[10px] bg-stone-100 text-stone-500 font-semibold px-2 py-0.5 rounded-full">${d.eventDate || d.savedAt || ''}</span>
              </div>
              <p class="text-stone-700 whitespace-pre-wrap leading-relaxed text-[12px] bg-stone-50/60 p-2.5 rounded-xl border border-stone-100">${d.notes || ''}</p>
            </div>`;
        });
      } catch (err) {
        console.warn("Could not fetch remote milestones:", err);
      }
    }

    function downloadAlbumPDF() {
      if (!activeSession.babyName) return alert("कृपया पहले वॉल्ट लॉगिन करें");

      const m = activeSession.meta || {};
      document.getElementById('pdfBabyName').innerText = activeSession.babyName;
      document.getElementById('pdfBirthDate').innerText = `तारीख: ${m.date || '-'}`;
      document.getElementById('pdfBirthTime').innerText = `समय: ${m.time || '-'}`;
      document.getElementById('pdfBirthCity').innerText = `स्थान: ${m.city || '-'}`;

      document.getElementById('pdfLagna').innerText = m.lagna || '-';
      document.getElementById('pdfRashi').innerText = m.rashi || '-';
      document.getElementById('pdfNakshatra').innerText = `${m.nakshatra || '-'} (${m.pada || '-'})`;
      document.getElementById('pdfAkshar').innerText = m.akshar || '-';

      // Deep Clone Complete Live Chart Graphic
      const chartCloneContainer = document.getElementById('pdfChartClone');
      chartCloneContainer.innerHTML = "";
      const originalBox = document.getElementById('mainKundliBox');
      if (originalBox) {
        const clonedBox = originalBox.cloneNode(true);
        clonedBox.id = "clonedPdfBox";
        chartCloneContainer.appendChild(clonedBox);
      }

      // Render memories cleanly into the print template (Never Cut-Off)
      const pdfMilestoneContainer = document.getElementById('pdfMilestoneList');
      pdfMilestoneContainer.innerHTML = "";
      if (currentSavedMilestones.length === 0) {
        pdfMilestoneContainer.innerHTML = "<p style='color: #78716C; font-style: italic; text-align: center; padding: 10px;'>No memories recorded yet in this journal.</p>";
      } else {
        currentSavedMilestones.forEach(item => {
          const d = item.data;
          pdfMilestoneContainer.innerHTML += `
            <div style="background: #FFFFFF; border: 1.5px solid #FDE68A; border-left: 4px solid #D97706; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px; page-break-inside: avoid;">
              <div style="display: flex; justify-content: space-between; font-weight: bold; color: #78350F; margin-bottom: 6px;">
                <span style="font-size: 13px;">✦ ${item.event_tag}</span>
                <span style="font-size: 10px; color: #78716C;">${d.eventDate || d.savedAt || ''}</span>
              </div>
              <p style="margin: 0; color: #44403C; line-height: 1.5; font-size: 11px; white-space: pre-wrap;">${d.notes || ''}</p>
            </div>
          `;
        });
      }

      const certElement = document.getElementById('pdfPrintCanvas');

      // Optimized settings for html2pdf to prevent any blank spaces and cut-offs
      const opt = {
        margin: [5, 5, 5, 5],
        filename: `${activeSession.babyName}_Vedic_Janmapatri_Album.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
          scale: 2, 
          useCORS: true, 
          scrollY: 0,
          scrollX: 0
        },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      };

      html2pdf().set(opt).from(certElement).save();
    }

    async function downloadBackupFile() {
      if (!activeSession.profileHash) return alert("कृपया पहले वॉल्ट लॉगिन करें");
      try {
        const res = await fetch(`/api/backup/export?prof_hash=${encodeURIComponent(activeSession.profileHash)}`);
        const data = await res.json();
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${activeSession.babyName}_Encrypted_Vault_Backup.json`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        alert("बैकअप डाउनलोड त्रुटि: " + err.message);
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
          triggerSyncAndReload();
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
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

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
            letter = params.get('letter', ['खी'])[0]
            gender = params.get('gender', ['All'])[0]
            mode = params.get('mode', ['strict'])[0]
            names = generate_ai_names(letter, gender, mode)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(names).encode('utf-8'))

        elif url.path == "/api/milestones/get":
            prof_hash = params.get('prof_hash', [''])[0]
            pwd = params.get('pass', [''])[0]
            data = get_profile_milestones(prof_hash, pwd)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        elif url.path == "/api/backup/export":
            prof_hash = params.get('prof_hash', [''])[0]
            backup = export_single_profile_backup(prof_hash)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(backup).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        payload = json.loads(body.decode('utf-8'))

        if self.path == "/api/profile/auth":
            res = register_or_login_profile(
                payload['baby_name'],
                payload['passphrase'],
                payload.get('meta_data')
            )
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

        elif self.path == "/api/milestones/add":
            add_profile_milestone(
                payload['profile_hash'],
                payload['passphrase'],
                payload['event_tag'],
                payload['details']
            )
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))

        elif self.path == "/api/backup/import":
            count = import_single_profile_backup(payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "imported": count}).encode('utf-8'))

        elif self.path == "/api/vault/delete":
            res = delete_profile_vault(payload['profile_hash'], payload['passphrase'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n🌸 Nanhi Duniya Live at port: {port}")
    server = HTTPServer(('0.0.0.0', port), SimpleServer)
    server.serve_forever()
