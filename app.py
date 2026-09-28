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
    edit_profile_milestone,
    export_single_profile_backup,
    import_single_profile_backup,
    delete_profile_vault
)

init_db()

PWA_MANIFEST = {
    "name": "Nanhi Duniya - Vedic Janmapatri & Memory Vault",
    "short_name": "NanhiDuniya",
    "description": "Vedic Kundli, Scriptural Naming & Encrypted Lifetime Milestone Journal",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#FAF7F2",
    "theme_color": "#78350F",
    "icons": [
        {
            "src": "https://api.iconify.design/twemoji:cherry-blossom.svg",
            "sizes": "192x192 512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}

SERVICE_WORKER_JS = """
self.addEventListener('install', (e) => { self.skipWaiting(); });
self.addEventListener('activate', (e) => { e.waitUntil(clients.claim()); });
self.addEventListener('fetch', (e) => {});
"""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nanhi Duniya - Vedic Janmapatri & Lifetime Memory Vault</title>
  
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#78350F">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Nanhi Duniya">

  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Rozha+One&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAF7F2; }
    .glass-card { background: rgba(255, 255, 255, 0.98); border: 1px solid #EFEAE1; }
    .kundli-box { position: relative; width: 280px; height: 280px; margin: 0 auto; background: #FFFDF9; border: 2px solid #854D0E; }
    .kundli-svg { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
    .h-item { position: absolute; text-align: center; width: 64px; z-index: 10; transform: translate(-50%, -50%); }
    .rashi-no { color: #9A3412; font-size: 11px; font-weight: 800; display: block; line-height: 1; }
    .grah-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 2px; margin-top: 2px; }
    .grah-badge { background: #EEF2FF; color: #1E40AF; font-size: 9px; font-weight: 800; padding: 1px 3px; border-radius: 4px; border: 1px solid #DBEAFE; }

    #pdfPrintCanvas {
      width: 794px;
      background: #FFFDF9;
      color: #1C1917;
      padding: 36px;
      box-sizing: border-box;
      border: 8px double #B45309;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
  </style>
</head>
<body class="text-stone-800 pb-28 min-h-screen">

  <!-- Header -->
  <header class="py-3.5 px-4 md:px-8 border-b border-stone-200 bg-white sticky top-0 z-50 shadow-xs">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-xl shadow-2xs">
          🌸
        </div>
        <div>
          <h1 class="text-lg md:text-xl font-black text-amber-950 tracking-tight leading-tight">
            Nanhi Duniya
          </h1>
          <div class="flex items-center gap-2 mt-0.5">
            <p class="text-[10px] md:text-xs text-stone-500 font-medium hidden sm:block">Vedic Janmapatri • Scriptural Naming • Digital Health & Memory Vault</p>
            <span id="syncStatusBadge" class="text-[9px] bg-stone-100 text-stone-600 px-2 py-0.5 rounded-full font-bold">● Connecting...</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2.5">
        <button id="pwaInstallBtn" onclick="installPWA()" class="hidden text-xs bg-amber-50 hover:bg-amber-100 border border-amber-300 text-amber-900 px-3 py-1.5 rounded-xl font-bold items-center gap-1.5 transition">
          <span>📲</span> <span class="hidden sm:inline">Install App</span>
        </button>

        <button id="navVaultBtn" onclick="toggleVaultModal()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-3.5 py-1.5 rounded-xl font-bold flex items-center gap-1.5 transition shadow-2xs active:scale-95">
          <span>🔐</span> <span id="navVaultText">Login / Open Vault</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-4 md:p-8 space-y-6">

    <!-- Active Vault Profile Banner -->
    <div id="activeProfileBanner" class="hidden p-4 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 border border-emerald-200 rounded-2xl flex justify-between items-center text-xs shadow-xs">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-emerald-600 animate-pulse"></div>
        <div>
          <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider block">Live Cloud Vault Active:</span>
          <strong id="activeBabyNameDisplay" class="text-emerald-950 text-base md:text-lg font-black block"></strong>
        </div>
      </div>
      <button onclick="logoutVault()" class="text-xs bg-white border border-emerald-300 hover:bg-emerald-50 text-emerald-900 font-bold px-3 py-1.5 rounded-xl active:scale-95 transition shadow-2xs">
        🔒 Lock & Logout
      </button>
    </div>

    <!-- MAIN TWO-COLUMN RESPONSIVE GRID -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

      <!-- LEFT COLUMN: Kundli & Birth Form -->
      <div class="lg:col-span-5 space-y-6">
        
        <div id="stepBirthForm" class="glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <h2 class="text-base font-bold text-stone-800 flex items-center gap-2">
              <span>✨</span> Birth Details (Janm Vivaran)
            </h2>
            <span class="text-[11px] bg-amber-100 text-amber-900 font-bold px-2.5 py-0.5 rounded-full">Step 1</span>
          </div>

          <div class="space-y-3 text-xs">
            <div>
              <label class="block font-semibold text-stone-600 mb-1">Place of Birth (City / District)</label>
              <input type="text" id="bCity" value="Gondia" placeholder="Enter City" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none font-medium">
            </div>
            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="block font-semibold text-stone-600 mb-1">Birth Date</label>
                <input type="date" id="bDate" value="2026-09-22" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none font-medium">
              </div>
              <div>
                <label class="block font-semibold text-stone-600 mb-1">Birth Time</label>
                <input type="time" id="bTime" value="11:05" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none font-medium">
              </div>
            </div>

            <button id="calcBtn" type="button" onclick="calculateKundli()" class="w-full py-3 bg-amber-800 hover:bg-amber-900 text-white font-bold rounded-xl mt-2 active:scale-95 transition shadow-sm">
              Generate Lagna Chart & Vedic Syllable
            </button>
          </div>

          <div id="kundliResult" class="hidden mt-4 pt-4 border-t border-stone-200 space-y-4">
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200">
                <span class="text-[10px] text-stone-500 block uppercase font-bold tracking-wider">Ascendant (Lagna)</span>
                <span id="resLagna" class="font-extrabold text-amber-950 text-sm"></span>
              </div>
              <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200">
                <span class="text-[10px] text-stone-500 block uppercase font-bold tracking-wider">Moon Sign (Rashi)</span>
                <span id="resRashi" class="font-extrabold text-stone-800 text-sm"></span>
              </div>
            </div>

            <div class="p-3 bg-stone-50 rounded-xl border border-stone-200 text-xs space-y-1.5">
              <div class="flex justify-between"><span class="text-stone-500 font-medium">Nakshatra:</span><span id="resNakshatra" class="font-bold text-stone-900"></span></div>
              <div class="flex justify-between"><span class="text-stone-500 font-medium">Quarter (Pada):</span><span id="resPada" class="font-bold text-stone-900"></span></div>
              <div class="flex justify-between items-center pt-2 border-t border-stone-200">
                <span class="text-stone-700 font-bold">Vedic Naming Syllable:</span>
                <span id="resAkshar" class="text-3xl font-black text-amber-800 font-serif"></span>
              </div>
            </div>

            <div class="text-center pt-2">
              <p class="text-xs font-bold text-stone-700 mb-2.5">Live Vedic Lagna Chart (Ascendant & 9 Planets)</p>
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

      </div>

      <!-- RIGHT COLUMN: Naming & Vault -->
      <div class="lg:col-span-7 space-y-6">

        <!-- STEP 2: Naming Engine -->
        <div id="namesSection" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-base font-bold text-stone-800 flex items-center gap-1.5">
                <span>👶</span> Vedic Name Selection
              </h2>
              <p class="text-[11px] text-stone-500">Suggested Names for Syllable '<span id="currentLetterBadge" class="font-bold text-amber-900"></span>'</p>
            </div>
            <button type="button" onclick="fetchAINames()" class="text-xs bg-amber-100 hover:bg-amber-200 text-amber-900 px-3 py-1.5 rounded-xl font-bold transition">
              Refresh Names ↻
            </button>
          </div>

          <div class="grid grid-cols-2 gap-2 bg-stone-100 p-1.5 rounded-xl text-xs font-bold text-center">
            <button id="modeStrict" onclick="setNamingMode('strict')" class="py-2 rounded-lg bg-white text-amber-950 shadow-xs transition">
              🎯 Strict Syllable (<span id="strictLetterText"></span>)
            </button>
            <button id="modeAnumati" onclick="setNamingMode('anumati')" class="py-2 rounded-lg text-stone-500 hover:text-stone-800 transition">
              📜 Permitted Class (<span id="anumatiLetterText"></span>)
            </button>
          </div>

          <div class="flex gap-2">
            <button id="btnAll" onclick="setGenderFilter('All')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-amber-800 text-white transition">All Names</button>
            <button id="btnBoy" onclick="setGenderFilter('Boy')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600 hover:bg-stone-200 transition">👦 Boys</button>
            <button id="btnGirl" onclick="setGenderFilter('Girl')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600 hover:bg-stone-200 transition">👧 Girls</button>
          </div>

          <div id="namesList" class="space-y-3"></div>

          <div class="pt-3 border-t border-stone-200 text-xs space-y-2">
            <p class="font-bold text-stone-700">Or type your own pre-decided name:</p>
            <div class="flex gap-2">
              <input type="text" id="customNameInput" placeholder="e.g., Shivansh, Aarav, Anika..." class="flex-1 p-2.5 rounded-xl border border-stone-300">
              <button onclick="useCustomName()" class="px-4 py-2.5 bg-stone-900 hover:bg-black text-white font-bold rounded-xl active:scale-95 transition">
                Select
              </button>
            </div>
          </div>
        </div>

        <!-- STEP 3: Setup Profile -->
        <div id="profileSetupSection" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4 border-2 border-amber-300">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-base font-bold text-stone-900 flex items-center gap-1.5">
                <span>🔐</span> Create Baby Profile & Master Password
              </h2>
              <p class="text-[11px] text-stone-500">Zero-Knowledge AES-256 Vault Encryption</p>
            </div>
            <span class="text-xs bg-emerald-100 text-emerald-900 font-bold px-2.5 py-0.5 rounded-md">Step 2</span>
          </div>

          <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200 text-xs space-y-1.5">
            <div class="flex justify-between"><span class="text-stone-600">Chosen Baby Name:</span><span id="cardFinalName" class="font-black text-amber-900 text-sm"></span></div>
            <div class="flex justify-between"><span class="text-stone-600">Birth Date:</span><span id="cardFinalDate" class="font-bold text-stone-800"></span></div>
            <div class="flex justify-between"><span class="text-stone-600">Birth Time:</span><span id="cardFinalTime" class="font-bold text-stone-800"></span></div>
            <div class="flex justify-between"><span class="text-stone-600">Birth Place:</span><span id="cardFinalCity" class="font-bold text-stone-800"></span></div>
          </div>

          <div class="space-y-2 text-xs">
            <label class="block font-bold text-stone-700">Create a Secret Master Password (Family Key):</label>
            <input type="password" id="masterPasswordInput" placeholder="Keep this password safe with your family" class="w-full p-2.5 rounded-xl border border-stone-300 focus:ring-2 focus:ring-amber-500 outline-none font-medium">
            <p class="text-[10px] text-stone-500">✦ This password secures both Janmapatri and lifetime memories directly on the cloud.</p>
            
            <button onclick="createBabyProfileVault()" class="w-full py-3 bg-emerald-800 hover:bg-emerald-900 text-white font-bold rounded-xl mt-2 active:scale-95 transition shadow-sm">
              Lock Profile & Open Milestone Vault ➔
            </button>
          </div>
        </div>

        <!-- DEDICATED LIFETIME MILESTONE & VACCINATION VAULT -->
        <div id="vaultDashboard" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-5">
          <div class="flex justify-between items-center border-b border-stone-200 pb-3">
            <div>
              <h2 class="text-lg font-black text-amber-950 flex items-center gap-1.5">
                <span>📖</span> <span id="vaultHeadingBabyName">Baby</span>'s Lifetime Memory & Health Vault
              </h2>
              <p class="text-[11px] text-stone-500">Janmapatri, Memories, Questions & Vaccination Schedule</p>
            </div>
            <span class="text-xs bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full font-bold">Encrypted Vault</span>
          </div>

          <div class="p-3 bg-amber-50/70 rounded-xl border border-amber-200 text-xs grid grid-cols-2 md:grid-cols-4 gap-2">
            <div><span class="text-[10px] text-stone-500 block">Lagna</span><strong id="vLagnaText">-</strong></div>
            <div><span class="text-[10px] text-stone-500 block">Rashi</span><strong id="vRashiText">-</strong></div>
            <div><span class="text-[10px] text-stone-500 block">Nakshatra</span><strong id="vNakshatraText">-</strong></div>
            <div><span class="text-[10px] text-stone-500 block">Syllable</span><strong id="vAksharText" class="text-amber-900 text-sm font-black">-</strong></div>
          </div>

          <!-- DUAL ENTRY -->
          <div class="p-4 bg-gradient-to-b from-stone-50 to-white rounded-2xl border border-stone-200 text-xs space-y-3 shadow-xs">
            <div class="flex justify-between items-center">
              <span class="font-bold text-stone-800 flex items-center gap-1.5">
                <span>✍️</span> Record New Entry in Vault:
              </span>
              <div class="flex gap-1 bg-stone-200 p-0.5 rounded-xl font-bold text-[11px]">
                <button id="tabMemoryBtn" onclick="switchEntryTab('memory')" class="px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs">🌟 Memory / Question</button>
                <button id="tabVaccineBtn" onclick="switchEntryTab('vaccine')" class="px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900">💉 Vaccination Record</button>
              </div>
            </div>

            <!-- TAB 1: Memory -->
            <div id="formMemorySection" class="space-y-3">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <select id="milestoneType" onchange="toggleCustomQuestion()" class="p-2.5 rounded-xl border border-stone-300 bg-white font-semibold">
                  <option value="PRESET">Standard Milestone</option>
                  <option value="CUSTOM">Custom Question / Special Moment</option>
                </select>
                <input type="date" id="mEventDate" class="p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>

              <div id="presetSelectDiv">
                <select id="mPresetTag" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white font-medium">
                  <option value="FIRST_SMILE">First Sweet Smile (पहली मुस्कान)</option>
                  <option value="FIRST_STEP">First Steps Taken (पहला कदम)</option>
                  <option value="FIRST_FOOD">First Solid Food / Annaprashan (अन्नप्राशन)</option>
                  <option value="FIRST_WORD">First Words Spoken (पहला शब्द)</option>
                  <option value="FIRST_TRIP">First Family Vacation / Grandparents Home</option>
                  <option value="FAV_TOY">First Favorite Toy & Games</option>
                  <option value="SWEET_HABIT">Cutest Sleeping & Smiling Habit</option>
                </select>
              </div>

              <div id="customQuestionDiv" class="hidden">
                <input type="text" id="mCustomQuestion" placeholder="e.g., How did baby react to first rain? Or first lullaby reaction?" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>

              <textarea id="mNotes" rows="2" placeholder="Describe the emotions, stories, family reactions and details of this moment..." class="w-full p-3 rounded-xl border border-stone-300 bg-white leading-relaxed outline-none focus:ring-2 focus:ring-amber-500"></textarea>

              <button type="button" onclick="saveNewMilestone()" class="w-full py-2.5 bg-amber-900 hover:bg-amber-950 text-white rounded-xl font-bold active:scale-95 transition shadow-sm">
                Save Memory to Vault (AES-256)
              </button>
            </div>

            <!-- TAB 2: Vaccination -->
            <div id="formVaccineSection" class="hidden space-y-3">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label class="block font-semibold text-stone-600 mb-1">Vaccine Name</label>
                  <input type="text" id="vName" list="vaccinePresets" placeholder="e.g., Infanrix Hexa, Synflorix, Rotasil..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
                  <datalist id="vaccinePresets">
                    <option value="Infanrix Hexa (HIB + Hep B + IPV + DTP)">
                    <option value="Synflorix (PCV 2)">
                    <option value="Rotasil (Rotavirus)">
                    <option value="BCG + OPV 0 + Hep B">
                    <option value="MMR 1">
                    <option value="Typhoid Conjugate Vaccine">
                  </datalist>
                </div>
                <div>
                  <label class="block font-semibold text-stone-600 mb-1">Clinic / Hospital / Doctor</label>
                  <input type="text" id="vClinic" placeholder="e.g., Dr. Ajay Agrawal / City Child Clinic" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label class="block font-semibold text-stone-600 mb-1">Date Given (दिनांक)</label>
                  <input type="date" id="vDateGiven" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
                </div>
                <div>
                  <label class="block font-semibold text-stone-600 mb-1">Next Vaccine Due Date (अगली तारीख)</label>
                  <input type="date" id="vNextDue" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
                </div>
              </div>

              <div>
                <label class="block font-semibold text-stone-600 mb-1">Baby's Experience & Memory</label>
                <textarea id="vExperience" rows="2" placeholder="Kitna roya, fever aaya kya, kiske godi me chup hua, doctor ne kya bola..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white leading-relaxed outline-none focus:ring-2 focus:ring-amber-500"></textarea>
              </div>

              <button type="button" onclick="saveVaccinationRecord()" class="w-full py-2.5 bg-blue-900 hover:bg-blue-950 text-white rounded-xl font-bold active:scale-95 transition shadow-sm">
                💉 Save Vaccination & Memory to Vault
              </button>
            </div>

          </div>

          <!-- Actions Bar -->
          <div class="pt-1 flex justify-between items-center">
            <button type="button" onclick="triggerSyncAndReload(true)" class="text-xs text-amber-800 font-bold underline">
              Cloud Sync / Refresh Feed ↻
            </button>
            <button type="button" onclick="downloadAlbumPDF()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-4 py-2 rounded-xl font-bold shadow-xs active:scale-95 transition flex items-center gap-1.5">
              <span>📖</span> Export Royal Album PDF
            </button>
          </div>

          <!-- Feed of Milestones & Vaccinations with Edit Options -->
          <div id="albumView" class="space-y-3"></div>

          <!-- Utility & Danger Zone -->
          <div class="pt-4 border-t border-stone-200 text-xs space-y-3">
            <div class="flex gap-2">
              <button onclick="downloadBackupFile()" class="flex-1 py-2.5 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 transition">
                📥 Download Encrypted Backup (.json)
              </button>
              <label class="flex-1 py-2.5 bg-stone-100 hover:bg-stone-200 text-stone-800 rounded-xl font-bold border border-stone-300 text-center cursor-pointer transition">
                📤 Restore Backup (.json)
                <input type="file" id="restoreFileInput" accept=".json" onchange="uploadRestoreFile(event)" class="hidden">
              </label>
            </div>

            <div class="p-3 bg-rose-50/70 border border-rose-200 rounded-xl text-rose-950 space-y-2">
              <div class="flex justify-between items-center">
                <span class="font-bold flex items-center gap-1.5 text-[11px] text-rose-900">
                  <span>⚠️</span> Danger Zone: Complete Profile & Janmapatri Wipe
                </span>
                <button onclick="toggleDeletePrompt()" class="text-[10px] bg-rose-200 hover:bg-rose-300 text-rose-900 px-2.5 py-1 rounded-lg font-bold transition">
                  Toggle Options
                </button>
              </div>
              <div id="deleteVaultDiv" class="hidden pt-2 border-t border-rose-200 space-y-2">
                <p class="text-[10px] text-rose-800 leading-relaxed">This action permanently wipes the baby's entire profile, Lagna Kundli, health records, and memories from the server and this device. Enter Master Password to proceed:</p>
                <div class="flex gap-2">
                  <input type="password" id="deleteConfirmPassword" placeholder="Enter Master Password" class="flex-1 p-2 bg-white rounded-lg border border-rose-300 outline-none">
                  <button onclick="confirmDeleteVault()" class="px-3.5 py-2 bg-rose-700 hover:bg-rose-800 text-white rounded-lg font-bold text-xs active:scale-95 transition">
                    Wipe Completely
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>

  </main>

  <!-- Login/Unlock Modal -->
  <div id="loginModal" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
    <div class="bg-white rounded-3xl p-6 max-w-sm w-full space-y-4 shadow-2xl border border-stone-200">
      <div class="flex justify-between items-center">
        <h3 class="text-base font-bold text-stone-900 flex items-center gap-1.5">
          <span>🔑</span> Unlock Baby Vault
        </h3>
        <button onclick="toggleVaultModal()" class="text-stone-400 hover:text-stone-700 font-black text-sm">✕</button>
      </div>
      <p class="text-xs text-stone-500 leading-relaxed">Enter your baby's exact name and family master password to unlock and sync all encrypted records from cloud:</p>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-stone-700 mb-1">Baby Name</label>
          <input type="text" id="loginBabyName" placeholder="e.g., Shivansh" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none focus:ring-2 focus:ring-amber-500 font-medium">
        </div>
        <div>
          <label class="block font-semibold text-stone-700 mb-1">Master Password</label>
          <input type="password" id="loginPassword" placeholder="Enter password" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none focus:ring-2 focus:ring-amber-500 font-medium">
        </div>
        <button onclick="loginToVault()" class="w-full py-3 bg-amber-900 hover:bg-amber-950 text-white rounded-xl font-bold active:scale-95 transition shadow-sm">
          Unlock Vault ➔
        </button>
      </div>
    </div>
  </div>

  <!-- ROYAL CLEAN ALBUM PRINT CANVAS -->
  <div style="position: absolute; left: -9999px; top: 0;">
    <div id="pdfPrintCanvas">
      <div style="text-align: center; border-bottom: 2px solid #92400E; padding-bottom: 12px; margin-bottom: 18px;">
        <span style="font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #92400E; font-weight: bold;">Official Vedic Janmapatri, Health & Lifetime Journal</span>
        <h1 style="font-family: 'Rozha One', serif; font-size: 28px; color: #78350F; margin: 4px 0 0 0;">🌸 Nanhi Duniya</h1>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; background: #FEF3C7; border: 1.5px solid #F59E0B; padding: 12px 18px; border-radius: 10px; margin-bottom: 18px;">
        <div>
          <span style="font-size: 10px; color: #92400E; font-weight: bold; text-transform: uppercase;">Baby Name</span>
          <h2 id="pdfBabyName" style="font-size: 22px; font-weight: 800; color: #78350F; margin: 2px 0 0 0;"></h2>
        </div>
        <div style="text-align: right; font-size: 11px; color: #78350F; line-height: 1.4;">
          <div><strong id="pdfBirthDate"></strong></div>
          <div id="pdfBirthTime"></div>
          <div id="pdfBirthCity"></div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 18px; text-align: center; font-size: 11px;">
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">Ascendant (Lagna)</span>
          <strong id="pdfLagna" style="color: #78350F; font-size: 13px;"></strong>
        </div>
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">Moon Sign (Rashi)</span>
          <strong id="pdfRashi" style="color: #1C1917; font-size: 13px;"></strong>
        </div>
        <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;">
          <span style="color: #78716C; font-size: 9px; display: block;">Nakshatra & Pada</span>
          <strong id="pdfNakshatra" style="color: #1C1917; font-size: 12px;"></strong>
        </div>
        <div style="background: #FEF3C7; padding: 8px; border-radius: 6px; border: 1.5px solid #FCD34D;">
          <span style="color: #92400E; font-size: 9px; display: block;">Naming Syllable</span>
          <strong id="pdfAkshar" style="color: #78350F; font-size: 18px;"></strong>
        </div>
      </div>

      <div style="text-align: center; margin-bottom: 24px;">
        <p style="font-size: 12px; font-weight: bold; color: #78350F; margin-bottom: 8px; letter-spacing: 0.5px;">Scriptural Vedic Lagna Chakra (9 Planetary Glyphs)</p>
        <div id="pdfChartClone" style="display: inline-block;"></div>
      </div>

      <div style="border-top: 2px dashed #B45309; padding-top: 18px;">
        <div style="text-align: center; margin-bottom: 12px;">
          <h3 style="font-size: 16px; font-weight: 800; color: #78350F; margin: 0;">📖 Lifetime Milestones, Memories & Immunization Journal</h3>
          <p style="font-size: 10px; color: #78716C; margin: 2px 0 0 0;">(Parent's Recorded Stories, Vaccinations & Cherished Moments)</p>
        </div>
        <div id="pdfMilestoneList" style="font-size: 11px;"></div>
      </div>

      <div style="margin-top: 35px; text-align: center; font-size: 9px; color: #A8A29E; border-top: 1px solid #E7E5E4; padding-top: 8px;">
        🔒 Zero-Knowledge AES-256 Encrypted Lifetime Journal • Official Nanhi Duniya Record
      </div>
    </div>
  </div>

  <script>
    let currentLetter = "खी";
    let selectedGender = "All";
    let namingMode = "strict";
    let currentSavedMilestones = [];
    let deferredPrompt = null;

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

    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW error:', err));
      });
    }

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      const btn = document.getElementById('pwaInstallBtn');
      if (btn) btn.classList.remove('hidden');
    });

    function installPWA() {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          document.getElementById('pwaInstallBtn').classList.add('hidden');
        }
        deferredPrompt = null;
      });
    }

    function updateNetworkStatus() {
      const badge = document.getElementById('syncStatusBadge');
      if (navigator.onLine) {
        badge.innerText = "● Cloud Connected (Live)";
        badge.className = "text-[9px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold";
        flushOfflineQueueToServer();
      } else {
        badge.innerText = "● Offline Mode (Local Queue)";
        badge.className = "text-[9px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-bold";
      }
    }

    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);

    window.addEventListener('DOMContentLoaded', () => {
      updateNetworkStatus();
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

    function switchEntryTab(tab) {
      if (tab === 'memory') {
        document.getElementById('formMemorySection').classList.remove('hidden');
        document.getElementById('formVaccineSection').classList.add('hidden');
        document.getElementById('tabMemoryBtn').className = "px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs";
        document.getElementById('tabVaccineBtn').className = "px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900";
      } else {
        document.getElementById('formVaccineSection').classList.remove('hidden');
        document.getElementById('formMemorySection').classList.add('hidden');
        document.getElementById('tabVaccineBtn').className = "px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs";
        document.getElementById('tabMemoryBtn').className = "px-2.5 py-1 rounded-lg text-stone-600 hover:text-stone-900";
        document.getElementById('vDateGiven').value = new Date().toISOString().split('T')[0];
      }
    }

    // COMPLETE WIPE FUNCTION (Server + LocalStorage + Session)
    async function confirmDeleteVault() {
      const pwd = document.getElementById('deleteConfirmPassword').value.trim();
      if (!pwd) return alert("Please enter master password to proceed");

      if (!confirm("⚠️ This will permanently delete this baby's entire profile, Kundli, and all memories from the cloud and this device. Continue?")) {
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
          // Clear all client cache completely
          localStorage.clear();
          sessionStorage.clear();
          activeSession = { profileHash: '', babyName: '', passphrase: '', meta: {} };
          alert("🗑️ Entire profile, Janmapatri and records permanently wiped!");
          window.location.reload();
        } else {
          alert("Error: " + data.message);
        }
      } catch (e) {
        alert("Server connection failed: " + e.message);
      }
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

      if (!bDate || !bTime) return alert("Please enter birth date and time");

      btn.innerText = "Calculating Kundli...";
      btn.disabled = true;

      try {
        const parts = bDate.split(/[-/]/);
        let year = parseInt(parts[0]), month = parseInt(parts[1]), day = parseInt(parts[2]);
        const tParts = bTime.split(':');
        const hour = parseInt(tParts[0]), minute = parseInt(tParts[1]);

        const res = await fetch(`/api/kundli?y=${year}&m=${month}&d=${day}&h=${hour}&min=${minute}&city=${encodeURIComponent(bCity)}`);
        const data = await res.json();

        document.getElementById('resLagna').innerText = `${data.lagna_english} (${data.lagna_hindi})`;
        document.getElementById('resRashi').innerText = `${data.rashi_english} (${data.rashi_hindi})`;
        document.getElementById('resNakshatra').innerText = data.nakshatra_hindi;
        document.getElementById('resPada').innerText = `Pada ${data.charan}`;
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
        btn.innerText = "Generate Lagna Chart & Vedic Syllable";
        btn.disabled = false;
      }
    }

    async function fetchAINames() {
      const listDiv = document.getElementById('namesList');
      listDiv.innerHTML = "";

      try {
        const res = await fetch(`/api/ai-names?letter=${encodeURIComponent(currentLetter)}&gender=${encodeURIComponent(selectedGender)}&mode=${encodeURIComponent(namingMode)}`);
        const names = await res.json();

        names.forEach(n => {
          const isBoy = n.gender === 'Boy';
          const genderBadge = isBoy
            ? `<span class="text-[10px] bg-blue-50 text-blue-800 px-2 py-0.5 rounded-full font-bold border border-blue-200">👦 Boy</span>`
            : `<span class="text-[10px] bg-rose-50 text-rose-800 px-2 py-0.5 rounded-full font-bold border border-rose-200">👧 Girl</span>`;

          listDiv.innerHTML += `
            <div class="p-4 bg-white rounded-2xl border border-stone-200 shadow-2xs space-y-2 hover:border-amber-300 transition">
              <div class="flex justify-between items-center">
                <div>
                  <h3 class="text-base font-extrabold text-stone-900">${n.name_hi} <span class="text-xs font-semibold text-stone-500 font-sans">(${n.name_en})</span></h3>
                  <div class="flex gap-1.5 mt-1">${genderBadge}</div>
                </div>
                <button onclick="finalizeName('${n.name_hi}')" class="px-3 py-1.5 rounded-xl border border-amber-400 text-amber-950 bg-amber-100 hover:bg-amber-200 text-xs font-black shadow-xs active:scale-95 transition">
                  👑 Select Name
                </button>
              </div>

              <div class="pt-2 border-t border-stone-100 text-xs space-y-1">
                <p class="text-stone-700"><span class="font-bold text-stone-900">Meaning:</span> ${n.meaning}</p>
                ${n.significance ? `<p class="text-amber-900 font-medium"><span class="font-bold">Significance:</span> ${n.significance}</p>` : ''}
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
      if (!cName) return alert("Please enter a name");
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

      if (!babyName) return alert("Please select or type a name first");
      if (!pwd || pwd.length < 4) return alert("Password must be at least 4 characters");

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

          alert("🎉 Baby profile created and cloud vault locked successfully!");
          showVaultDashboard();
        } else {
          alert("Error: " + data.message);
        }
      } catch (err) {
        alert("Check connection: " + err.message);
      }
    }

    async function loginToVault() {
      const babyName = document.getElementById('loginBabyName').value.trim();
      const pwd = document.getElementById('loginPassword').value.trim();

      if (!babyName || !pwd) return alert("Please provide both name and master password");

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
          alert("⚠️ Invalid credentials! Please check the baby name and password.");
        }
      } catch (err) {
        alert("Failed to connect to cloud server. Check internet.");
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
      document.getElementById('navVaultText').innerText = "Login / Open Vault";
      alert("🔒 Vault locked and session ended.");
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
      triggerSyncAndReload(true);
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
      if (!activeSession.profileHash || !activeSession.passphrase) return alert("Please login to vault first");

      const type = document.getElementById('milestoneType').value;
      const eventDate = document.getElementById('mEventDate').value;
      const notes = document.getElementById('mNotes').value.trim();

      let eventTag = "";
      if (type === 'CUSTOM') {
        eventTag = document.getElementById('mCustomQuestion').value.trim();
        if (!eventTag) return alert("Please specify question/title");
      } else {
        const sel = document.getElementById('mPresetTag');
        eventTag = sel.options[sel.selectedIndex].text;
      }

      if (!notes) return alert("Please write details/notes for this memory");

      const payload = {
        profile_hash: activeSession.profileHash,
        passphrase: activeSession.passphrase,
        event_tag: eventTag,
        details: { 
          category: "MEMORY",
          title: eventTag, 
          notes: notes, 
          eventDate: eventDate,
          savedAt: new Date().toLocaleDateString('en-IN') 
        }
      };

      await dispatchVaultSave(payload, "Memory saved to cloud vault!");
      document.getElementById('mNotes').value = "";
      if (type === 'CUSTOM') document.getElementById('mCustomQuestion').value = "";
    }

    async function saveVaccinationRecord() {
      if (!activeSession.profileHash || !activeSession.passphrase) return alert("Please login to vault first");

      const vName = document.getElementById('vName').value.trim();
      const vClinic = document.getElementById('vClinic').value.trim() || "Local Pediatric Clinic";
      const vDateGiven = document.getElementById('vDateGiven').value;
      const vNextDue = document.getElementById('vNextDue').value;
      const vExp = document.getElementById('vExperience').value.trim();

      if (!vName) return alert("Please enter vaccine name");
      if (!vDateGiven) return alert("Please specify date given");

      const eventTag = `💉 Vaccine: ${vName}`;
      const payload = {
        profile_hash: activeSession.profileHash,
        passphrase: activeSession.passphrase,
        event_tag: eventTag,
        details: {
          category: "VACCINE",
          vaccineName: vName,
          clinic: vClinic,
          dateGiven: vDateGiven,
          nextDue: vNextDue,
          experience: vExp,
          eventDate: vDateGiven,
          savedAt: new Date().toLocaleDateString('en-IN')
        }
      };

      await dispatchVaultSave(payload, "Vaccination record saved to cloud vault!");
      document.getElementById('vName').value = "";
      document.getElementById('vClinic').value = "";
      document.getElementById('vExperience').value = "";
      document.getElementById('vNextDue').value = "";
    }

    async function dispatchVaultSave(payload, successMsg) {
      if (!navigator.onLine) {
        const q = getOfflineQueue();
        q.push(payload);
        setOfflineQueue(q);
        alert("⚠️ Offline! Saved locally and queued for cloud sync.");
        renderLocalEntry(payload);
      } else {
        try {
          const res = await fetch('/api/milestones/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.status === "ok") {
            alert(`🎉 ${successMsg}`);
            triggerSyncAndReload(true);
          } else {
            throw new Error("Save error");
          }
        } catch (e) {
          const q = getOfflineQueue();
          q.push(payload);
          setOfflineQueue(q);
          alert("Server unreachable. Queued in offline storage.");
          renderLocalEntry(payload);
        }
      }
    }

    function renderLocalEntry(item) {
      const container = document.getElementById('albumView');
      const d = item.details;
      container.innerHTML = `
        <div class="p-4 bg-gradient-to-r from-amber-50/80 to-stone-50 rounded-2xl border border-amber-200 text-xs space-y-1.5 shadow-xs">
          <div class="flex justify-between items-center">
            <span class="font-extrabold text-amber-950 text-sm flex items-center gap-1">
              <span>📌</span> ${item.event_tag}
            </span>
            <span class="text-[10px] bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full font-bold">Pending Cloud Sync</span>
          </div>
          <p class="text-stone-700 whitespace-pre-wrap leading-relaxed">${d.notes || d.experience || ''}</p>
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
    }

    // CLOUD-FIRST RELOAD
    async function triggerSyncAndReload(forceCloud = false) {
      if (!activeSession.profileHash || !activeSession.passphrase) return;

      if (navigator.onLine) {
        await flushOfflineQueueToServer();
      }

      try {
        const res = await fetch(`/api/milestones/get?prof_hash=${encodeURIComponent(activeSession.profileHash)}&pass=${encodeURIComponent(activeSession.passphrase)}&t=${Date.now()}`);
        const list = await res.json();
        currentSavedMilestones = list;
        renderFeedList(list);
      } catch (err) {
        console.warn("Could not fetch remote milestones:", err);
      }
    }

    function renderFeedList(list) {
      const container = document.getElementById('albumView');
      container.innerHTML = "";

      if (list.length === 0) {
        container.innerHTML = `
          <div class="p-6 text-center border-2 border-dashed border-stone-200 rounded-2xl bg-white/50">
            <span class="text-2xl block mb-1">🕊️</span>
            <p class="text-xs text-stone-500 font-medium">No memories or vaccination records saved yet. Record your first moment above!</p>
          </div>`;
        return;
      }

      list.forEach(item => {
        const d = item.data;
        const isVaccine = d.category === "VACCINE" || item.event_tag.includes("Vaccine");

        if (isVaccine) {
          container.innerHTML += `
            <div class="p-4 bg-blue-50/60 rounded-2xl border border-blue-200 text-xs space-y-2 shadow-xs hover:border-blue-400 transition">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-blue-950 text-sm flex items-center gap-1.5">
                  <span>💉</span> ${d.vaccineName || item.event_tag}
                </span>
                <div class="flex items-center gap-2">
                  <span class="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded-full">Date: ${d.dateGiven || d.eventDate}</span>
                  <button onclick="editEntryPrompt(${item.id})" class="text-[10px] bg-white border border-blue-300 text-blue-900 px-2 py-0.5 rounded-lg font-bold hover:bg-blue-50 transition">✏️ Edit</button>
                </div>
              </div>
              <div class="flex justify-between text-[11px] text-stone-600 bg-white/70 p-2 rounded-xl border border-blue-100">
                <span><strong>Place/Doctor:</strong> ${d.clinic || 'Clinic'}</span>
                ${d.nextDue ? `<span class="text-rose-700 font-bold">Next Due: ${d.nextDue}</span>` : ''}
              </div>
              ${d.experience ? `<p class="text-stone-700 leading-relaxed text-[12px] bg-white p-2.5 rounded-xl border border-stone-200"><strong>Baby's Reaction & Memory:</strong> ${d.experience}</p>` : ''}
            </div>`;
        } else {
          container.innerHTML += `
            <div class="p-4 bg-white rounded-2xl border border-stone-200/90 text-xs space-y-2 shadow-xs hover:border-amber-200 transition">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-amber-950 text-sm flex items-center gap-1.5">
                  <span class="text-amber-700">✦</span> ${item.event_tag}
                </span>
                <div class="flex items-center gap-2">
                  <span class="text-[10px] bg-stone-100 text-stone-500 font-semibold px-2 py-0.5 rounded-full">${d.eventDate || d.savedAt || ''}</span>
                  <button onclick="editEntryPrompt(${item.id})" class="text-[10px] bg-stone-50 border border-stone-300 text-stone-700 px-2 py-0.5 rounded-lg font-bold hover:bg-stone-100 transition">✏️ Edit</button>
                </div>
              </div>
              <p class="text-stone-700 whitespace-pre-wrap leading-relaxed text-[12px] bg-stone-50/60 p-3 rounded-xl border border-stone-100">${d.notes || ''}</p>
            </div>`;
        }
      });
    }

    // EDIT RECORD WITH MASTER PASSWORD
    async function editEntryPrompt(id) {
      const item = currentSavedMilestones.find(x => x.id === id);
      if (!item) return;

      const d = item.data;
      const isVaccine = d.category === "VACCINE" || item.event_tag.includes("Vaccine");

      const pwd = prompt("Enter Master Password to authorize edit:");
      if (!pwd) return;

      if (isVaccine) {
        const newExp = prompt("Update Baby's Reaction & Memory:", d.experience || "");
        if (newExp === null) return;
        const newClinic = prompt("Update Clinic / Doctor Name:", d.clinic || "");
        if (newClinic === null) return;
        const newDue = prompt("Update Next Due Date (YYYY-MM-DD):", d.nextDue || "");
        if (newDue === null) return;

        d.experience = newExp;
        d.clinic = newClinic;
        d.nextDue = newDue;
      } else {
        const newNotes = prompt("Update Memory Details / Story:", d.notes || "");
        if (newNotes === null) return;
        d.notes = newNotes;
      }

      try {
        const res = await fetch('/api/milestones/edit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            profile_hash: activeSession.profileHash,
            passphrase: pwd,
            id: id,
            details: d
          })
        });
        const resp = await res.json();
        if (resp.status === "ok") {
          alert("🎉 Record updated and re-encrypted successfully!");
          triggerSyncAndReload(true);
        } else {
          alert("Unauthorized: " + resp.message);
        }
      } catch (err) {
        alert("Failed to update: " + err.message);
      }
    }

    function downloadAlbumPDF() {
      if (!activeSession.babyName) return alert("Please login to vault first");

      const m = activeSession.meta || {};
      document.getElementById('pdfBabyName').innerText = activeSession.babyName;
      document.getElementById('pdfBirthDate').innerText = `Date: ${m.date || '-'}`;
      document.getElementById('pdfBirthTime').innerText = `Time: ${m.time || '-'}`;
      document.getElementById('pdfBirthCity').innerText = `Place: ${m.city || '-'}`;

      document.getElementById('pdfLagna').innerText = m.lagna || '-';
      document.getElementById('pdfRashi').innerText = m.rashi || '-';
      document.getElementById('pdfNakshatra').innerText = `${m.nakshatra || '-'} (${m.pada || '-'})`;
      document.getElementById('pdfAkshar').innerText = m.akshar || '-';

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
        pdfMilestoneContainer.innerHTML = "<p style='color: #78716C; font-style: italic; text-align: center; padding: 10px;'>No memories or health records in vault yet.</p>";
      } else {
        currentSavedMilestones.forEach(item => {
          const d = item.data;
          const isVaccine = d.category === "VACCINE" || item.event_tag.includes("Vaccine");

          if (isVaccine) {
            pdfMilestoneContainer.innerHTML += `
              <div style="background: #F0F9FF; border: 1.5px solid #BAE6FD; border-left: 4px solid #0284C7; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; page-break-inside: avoid;">
                <div style="display: flex; justify-content: space-between; font-weight: bold; color: #0369A1; margin-bottom: 4px;">
                  <span style="font-size: 13px;">💉 ${d.vaccineName || item.event_tag}</span>
                  <span style="font-size: 10px; color: #0284C7;">Date: ${d.dateGiven || d.eventDate}</span>
                </div>
                <div style="font-size: 10px; color: #334155; margin-bottom: 4px;">
                  <strong>Administered at:</strong> ${d.clinic || 'Clinic'} ${d.nextDue ? ` | <span style="color: #BE123C; font-weight: bold;">Next Due: ${d.nextDue}</span>` : ''}
                </div>
                ${d.experience ? `<p style="margin: 0; color: #1E293B; line-height: 1.4; font-size: 11px;"><strong>Reaction & Story:</strong> ${d.experience}</p>` : ''}
              </div>
            `;
          } else {
            pdfMilestoneContainer.innerHTML += `
              <div style="background: #FFFFFF; border: 1.5px solid #FDE68A; border-left: 4px solid #D97706; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; page-break-inside: avoid;">
                <div style="display: flex; justify-content: space-between; font-weight: bold; color: #78350F; margin-bottom: 6px;">
                  <span style="font-size: 13px;">✦ ${item.event_tag}</span>
                  <span style="font-size: 10px; color: #78716C;">${d.eventDate || d.savedAt || ''}</span>
                </div>
                <p style="margin: 0; color: #44403C; line-height: 1.5; font-size: 11px; white-space: pre-wrap;">${d.notes || ''}</p>
              </div>
            `;
          }
        });
      }

      const certElement = document.getElementById('pdfPrintCanvas');
      const opt = {
        margin: [6, 6, 6, 6],
        filename: `${activeSession.babyName}_Vedic_Janmapatri_Health_Album.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, scrollY: 0, scrollX: 0 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
      };

      html2pdf().set(opt).from(certElement).save();
    }

    async function downloadBackupFile() {
      if (!activeSession.profileHash) return alert("Please login to vault first");
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
        alert("Backup download failed: " + err.message);
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
          alert(`🎉 Backup restored successfully! (${result.imported} records synced)`);
          triggerSyncAndReload(true);
        } catch (err) {
          alert("Invalid backup file: " + err.message);
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

        elif url.path == "/manifest.json":
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json')
            self.end_headers()
            self.wfile.write(json.dumps(PWA_MANIFEST).encode('utf-8'))

        elif url.path == "/sw.js":
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            self.wfile.write(SERVICE_WORKER_JS.encode('utf-8'))

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

        elif self.path == "/api/milestones/edit":
            res = edit_profile_milestone(
                payload['profile_hash'],
                payload['passphrase'],
                payload['id'],
                payload['details']
            )
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

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
