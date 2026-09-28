from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
from ND import get_kundli_details
from NE import generate_ai_names
from TV import (
    init_db,
    register_profile,
    login_profile,
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
    "icons": [{"src": "https://api.iconify.design/twemoji:cherry-blossom.svg", "sizes": "192x192 512x512", "type": "image/svg+xml"}]
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
  <title>Nanhi Duniya - Vedic Janmapatri & Health Vault</title>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#78350F">
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
    #pdfPrintCanvas { width: 794px; background: #FFFDF9; color: #1C1917; padding: 36px; box-sizing: border-box; border: 8px double #B45309; }
  </style>
</head>
<body class="text-stone-800 pb-28 min-h-screen">

  <header class="py-3.5 px-4 md:px-8 border-b border-stone-200 bg-white sticky top-0 z-50 shadow-xs">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-xl shadow-2xs">🌸</div>
        <div>
          <h1 class="text-lg md:text-xl font-black text-amber-950 tracking-tight leading-tight">Nanhi Duniya</h1>
          <div class="flex items-center gap-2 mt-0.5">
            <p class="text-[10px] md:text-xs text-stone-500 font-medium hidden sm:block">Vedic Janmapatri • Medical & Health Journal • Cloud Sync</p>
            <span id="syncStatusBadge" class="text-[9px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">● Cloud Connected</span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2.5">
        <button id="navVaultBtn" onclick="toggleVaultModal()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-3.5 py-1.5 rounded-xl font-bold flex items-center gap-1.5 transition shadow-2xs">
          <span>🔐</span> <span id="navVaultText">Login / Open Vault</span>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-4 md:p-8 space-y-6">

    <div id="activeProfileBanner" class="hidden p-4 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 border border-emerald-200 rounded-2xl flex justify-between items-center text-xs shadow-xs">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-emerald-600 animate-pulse"></div>
        <div>
          <span class="text-[10px] text-emerald-800 font-bold uppercase tracking-wider block">Live Cloud Vault Active:</span>
          <strong id="activeBabyNameDisplay" class="text-emerald-950 text-base md:text-lg font-black block"></strong>
        </div>
      </div>
      <button onclick="logoutVault()" class="text-xs bg-white border border-emerald-300 hover:bg-emerald-50 text-emerald-900 font-bold px-3 py-1.5 rounded-xl">🔒 Lock & Logout</button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- LEFT: Kundli -->
      <div class="lg:col-span-5 space-y-6">
        <div id="stepBirthForm" class="glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <h2 class="text-base font-bold text-stone-800 flex items-center gap-2"><span>✨</span> Birth Details (Janm Vivaran)</h2>
            <span class="text-[11px] bg-amber-100 text-amber-900 font-bold px-2.5 py-0.5 rounded-full">Step 1</span>
          </div>
          <div class="space-y-3 text-xs">
            <div>
              <label class="block font-semibold text-stone-600 mb-1">Place of Birth (City / District)</label>
              <input type="text" id="bCity" value="Gondia" placeholder="Enter City" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none">
            </div>
            <div class="grid grid-cols-2 gap-2.5">
              <div>
                <label class="block font-semibold text-stone-600 mb-1">Birth Date</label>
                <input type="date" id="bDate" value="2026-09-22" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none">
              </div>
              <div>
                <label class="block font-semibold text-stone-600 mb-1">Birth Time</label>
                <input type="time" id="bTime" value="11:05" class="w-full p-2.5 rounded-xl border border-stone-300 outline-none">
              </div>
            </div>
            <button id="calcBtn" type="button" onclick="calculateKundli()" class="w-full py-3 bg-amber-800 hover:bg-amber-900 text-white font-bold rounded-xl active:scale-95 transition">
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
              <p class="text-xs font-bold text-stone-700 mb-2.5">Live Vedic Lagna Chart (Lahiri Ayanamsha)</p>
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

      <!-- RIGHT: Naming & Triple Journal Vault -->
      <div class="lg:col-span-7 space-y-6">
        <div id="namesSection" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-base font-bold text-stone-800 flex items-center gap-1.5"><span>👶</span> Vedic Name Selection</h2>
              <p class="text-[11px] text-stone-500">Names for Syllable '<span id="currentLetterBadge" class="font-bold text-amber-900"></span>'</p>
            </div>
            <button type="button" onclick="fetchAINames()" class="text-xs bg-amber-100 hover:bg-amber-200 text-amber-900 px-3 py-1.5 rounded-xl font-bold transition">Refresh Names ↻</button>
          </div>
          <div class="grid grid-cols-2 gap-2 bg-stone-100 p-1.5 rounded-xl text-xs font-bold text-center">
            <button id="modeStrict" onclick="setNamingMode('strict')" class="py-2 rounded-lg bg-white text-amber-950 shadow-xs">🎯 Strict Syllable (<span id="strictLetterText"></span>)</button>
            <button id="modeAnumati" onclick="setNamingMode('anumati')" class="py-2 rounded-lg text-stone-500">📜 Permitted Class (<span id="anumatiLetterText"></span>)</button>
          </div>
          <div class="flex gap-2">
            <button id="btnAll" onclick="setGenderFilter('All')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-amber-800 text-white">All Names</button>
            <button id="btnBoy" onclick="setGenderFilter('Boy')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600">👦 Boys</button>
            <button id="btnGirl" onclick="setGenderFilter('Girl')" class="flex-1 py-1.5 rounded-xl text-xs font-bold bg-stone-100 text-stone-600">👧 Girls</button>
          </div>
          <div id="namesList" class="space-y-3"></div>
          <div class="pt-3 border-t border-stone-200 text-xs flex gap-2">
            <input type="text" id="customNameInput" placeholder="Or enter pre-decided name..." class="flex-1 p-2.5 rounded-xl border border-stone-300">
            <button onclick="useCustomName()" class="px-4 py-2.5 bg-stone-900 text-white font-bold rounded-xl">Select</button>
          </div>
        </div>

        <div id="profileSetupSection" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-4 border-2 border-amber-300">
          <h2 class="text-base font-bold text-stone-900 flex items-center gap-1.5"><span>🔐</span> Create Baby Profile & Master Password</h2>
          <div class="p-3 bg-amber-50 rounded-xl text-xs space-y-1">
            <p><strong>Baby Name:</strong> <span id="cardFinalName" class="text-amber-900 font-bold"></span></p>
            <p><strong>Birth Date & Time:</strong> <span id="cardFinalDate"></span>, <span id="cardFinalTime"></span></p>
          </div>
          <div class="space-y-2 text-xs">
            <label class="block font-bold text-stone-700">Set Secret Master Password (Family Key):</label>
            <input type="password" id="masterPasswordInput" placeholder="Keep this password safe" class="w-full p-2.5 rounded-xl border border-stone-300">
            <button onclick="createBabyProfileVault()" class="w-full py-3 bg-emerald-800 hover:bg-emerald-900 text-white font-bold rounded-xl">Lock Profile & Open Vault ➔</button>
          </div>
        </div>

        <!-- VAULT DASHBOARD -->
        <div id="vaultDashboard" class="hidden glass-card rounded-2xl p-5 md:p-6 shadow-sm space-y-5">
          <div class="flex justify-between items-center border-b border-stone-200 pb-3">
            <div>
              <h2 class="text-lg font-black text-amber-950 flex items-center gap-1.5"><span>📖</span> <span id="vaultHeadingBabyName">Baby</span>'s Lifetime Health & Memory Vault</h2>
              <p class="text-[11px] text-stone-500">Janmapatri, Memories, Vaccinations & Medical Prescriptions</p>
            </div>
            <span class="text-xs bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full font-bold">Encrypted Vault</span>
          </div>

          <!-- Triple Switch: Memory / Vaccine / Medication -->
          <div class="p-4 bg-stone-50 rounded-2xl border border-stone-200 text-xs space-y-3">
            <div class="flex justify-between items-center flex-wrap gap-2">
              <span class="font-bold text-stone-800">Record Entry:</span>
              <div class="flex gap-1 bg-stone-200 p-0.5 rounded-xl font-bold text-[11px]">
                <button id="tabMemoryBtn" onclick="switchEntryTab('memory')" class="px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs">🌟 Memory</button>
                <button id="tabVaccineBtn" onclick="switchEntryTab('vaccine')" class="px-2.5 py-1 rounded-lg text-stone-600">💉 Vaccine</button>
                <button id="tabMedBtn" onclick="switchEntryTab('med')" class="px-2.5 py-1 rounded-lg text-stone-600">🩺 Medication & Illness</button>
              </div>
            </div>

            <!-- Form 1: Memory -->
            <div id="formMemorySection" class="space-y-3">
              <div class="grid grid-cols-2 gap-2">
                <select id="mPresetTag" class="p-2.5 rounded-xl border border-stone-300 bg-white">
                  <option value="First Smile">First Sweet Smile (पहली मुस्कान)</option>
                  <option value="First Steps">First Steps (पहला कदम)</option>
                  <option value="First Food">First Solid Food (अन्नप्राशन)</option>
                  <option value="First Word">First Word Spoken (पहला शब्द)</option>
                </select>
                <input type="date" id="mEventDate" class="p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>
              <textarea id="mNotes" rows="2" placeholder="Record family emotions, story and memories in detail..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white"></textarea>
              <button onclick="saveNewMilestone()" class="w-full py-2.5 bg-amber-900 text-white font-bold rounded-xl">Save Memory to Vault</button>
            </div>

            <!-- Form 2: Vaccine -->
            <div id="formVaccineSection" class="hidden space-y-3">
              <div class="grid grid-cols-2 gap-2">
                <input type="text" id="vName" placeholder="Vaccine (e.g. Infanrix Hexa, Synflorix)" class="p-2.5 rounded-xl border border-stone-300 bg-white">
                <input type="text" id="vClinic" placeholder="Doctor / Clinic Name" class="p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div><label class="block text-[10px] text-stone-500 mb-0.5">Date Given</label><input type="date" id="vDateGiven" class="w-full p-2 rounded-xl border border-stone-300 bg-white"></div>
                <div><label class="block text-[10px] text-stone-500 mb-0.5">Next Due Date</label><input type="date" id="vNextDue" class="w-full p-2 rounded-xl border border-stone-300 bg-white"></div>
              </div>
              <textarea id="vExperience" rows="2" placeholder="Reaction, fever, soothing experience..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white"></textarea>
              <button onclick="saveVaccinationRecord()" class="w-full py-2.5 bg-blue-900 text-white font-bold rounded-xl">💉 Save Vaccination to Vault</button>
            </div>

            <!-- Form 3: Medication & Doctor Visit -->
            <div id="formMedSection" class="hidden space-y-3">
              <div class="grid grid-cols-2 gap-2">
                <input type="text" id="medDoctor" placeholder="Doctor / Clinic Name" class="p-2.5 rounded-xl border border-stone-300 bg-white">
                <input type="date" id="medDate" class="p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>
              <div>
                <input type="text" id="medProblem" placeholder="Symptoms / Problem (उदा. तेज बुखार, पेट दर्द, खांसी...)" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white">
              </div>
              <textarea id="medPrescription" rows="2" placeholder="Prescribed Medicines & Doses (दवाइयों के नाम, खुराक, सिरप...)" class="w-full p-2.5 rounded-xl border border-stone-300 bg-white"></textarea>
              <textarea id="medExperience" rows="2" placeholder="Baby recovery experience, parent feelings and care tips..." class="w-full p-2.5 rounded-xl border border-stone-300 bg-white"></textarea>
              <button onclick="saveMedicationRecord()" class="w-full py-2.5 bg-teal-800 text-white font-bold rounded-xl">🩺 Save Medical Journal to Vault</button>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-between items-center pt-2">
            <button onclick="triggerSyncAndReload(true)" class="text-xs text-amber-800 font-bold underline">Cloud Sync / Refresh ↻</button>
            <button onclick="openExportModal()" class="text-xs bg-amber-900 hover:bg-amber-950 text-white px-4 py-2 rounded-xl font-bold shadow-xs">📖 Export PDF Album</button>
          </div>

          <!-- Live Feed -->
          <div id="albumView" class="space-y-3"></div>

          <!-- Wipe Zone -->
          <div class="pt-4 border-t border-stone-200 text-xs">
            <button onclick="toggleDeletePrompt()" class="text-[11px] text-rose-800 font-bold underline">⚠️ Complete Profile & Record Wipe</button>
            <div id="deleteVaultDiv" class="hidden mt-2 p-3 bg-rose-50 border border-rose-200 rounded-xl space-y-2">
              <p class="text-[10px] text-rose-800">This permanently wipes this baby's profile and memories from cloud and local cache. Enter Master Password:</p>
              <div class="flex gap-2">
                <input type="password" id="deleteConfirmPassword" placeholder="Master Password" class="flex-1 p-2 border border-rose-300 rounded-lg">
                <button onclick="confirmDeleteVault()" class="px-3 py-2 bg-rose-700 text-white font-bold rounded-lg text-xs">Wipe Completely</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- SELECTIVE PDF EXPORT MODAL -->
  <div id="pdfExportModal" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl">
      <div class="flex justify-between items-center">
        <h3 class="text-base font-bold text-stone-900">📖 Select Album Export Mode</h3>
        <button onclick="toggleExportModal()" class="text-stone-400 font-black">✕</button>
      </div>
      <p class="text-xs text-stone-500">Choose which section you wish to print into the clean official PDF journal:</p>
      <div class="space-y-2 text-xs font-bold">
        <button onclick="executePDFExport('ALL')" class="w-full py-2.5 bg-amber-900 text-white rounded-xl shadow-xs">👑 Complete Grand Album (All Sections)</button>
        <button onclick="executePDFExport('MEMORIES')" class="w-full py-2.5 bg-stone-100 text-stone-800 border border-stone-200 rounded-xl">🌟 Vedic Kundli & Memories Only</button>
        <button onclick="executePDFExport('VACCINES')" class="w-full py-2.5 bg-blue-50 text-blue-900 border border-blue-200 rounded-xl">💉 Immunization Record Only</button>
        <button onclick="executePDFExport('MEDS')" class="w-full py-2.5 bg-teal-50 text-teal-900 border border-teal-200 rounded-xl">🩺 Medical & Prescription Log Only</button>
      </div>
    </div>
  </div>

  <!-- LOGIN MODAL -->
  <div id="loginModal" class="hidden fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl">
      <h3 class="text-base font-bold text-stone-900">🔑 Unlock Baby Vault</h3>
      <p class="text-xs text-stone-500">Enter baby name and family master password:</p>
      <div class="space-y-2.5 text-xs">
        <input type="text" id="loginBabyName" placeholder="Baby Name (e.g. Shivansh)" class="w-full p-2.5 rounded-xl border border-stone-300">
        <input type="password" id="loginPassword" placeholder="Master Password" class="w-full p-2.5 rounded-xl border border-stone-300">
        <button onclick="loginToVault()" class="w-full py-2.5 bg-amber-900 text-white rounded-xl font-bold">Unlock Vault ➔</button>
      </div>
    </div>
  </div>

  <!-- PDF CANVAS TEMPLATE -->
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

      <div id="pdfKundliSectionBlock">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 18px; text-align: center; font-size: 11px;">
          <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;"><span style="color: #78716C; font-size: 9px; display: block;">Ascendant (Lagna)</span><strong id="pdfLagna" style="color: #78350F; font-size: 13px;"></strong></div>
          <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;"><span style="color: #78716C; font-size: 9px; display: block;">Moon Sign (Rashi)</span><strong id="pdfRashi" style="color: #1C1917; font-size: 13px;"></strong></div>
          <div style="background: #F5F5F4; padding: 8px; border-radius: 6px; border: 1px solid #E7E5E4;"><span style="color: #78716C; font-size: 9px; display: block;">Nakshatra & Pada</span><strong id="pdfNakshatra" style="color: #1C1917; font-size: 12px;"></strong></div>
          <div style="background: #FEF3C7; padding: 8px; border-radius: 6px; border: 1.5px solid #FCD34D;"><span style="color: #92400E; font-size: 9px; display: block;">Naming Syllable</span><strong id="pdfAkshar" style="color: #78350F; font-size: 18px;"></strong></div>
        </div>
        <div style="text-align: center; margin-bottom: 24px;">
          <p style="font-size: 12px; font-weight: bold; color: #78350F; margin-bottom: 8px;">Scriptural Vedic Lagna Chakra (Lahiri Ayanamsha)</p>
          <div id="pdfChartClone" style="display: inline-block;"></div>
        </div>
      </div>

      <div style="border-top: 2px dashed #B45309; padding-top: 18px;">
        <h3 id="pdfSectionHeading" style="font-size: 16px; font-weight: 800; color: #78350F; margin: 0 0 12px 0; text-align: center;"></h3>
        <div id="pdfEntriesList" style="font-size: 11px;"></div>
      </div>
    </div>
  </div>

  <script>
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

    window.addEventListener('DOMContentLoaded', () => {
      if (activeSession.profileHash && activeSession.passphrase) {
        showVaultDashboard();
      }
    });

    function toggleVaultModal() { document.getElementById('loginModal').classList.toggle('hidden'); }
    function toggleExportModal() { document.getElementById('pdfExportModal').classList.toggle('hidden'); }
    function openExportModal() { document.getElementById('pdfExportModal').classList.remove('hidden'); }
    function toggleDeletePrompt() { document.getElementById('deleteVaultDiv').classList.toggle('hidden'); }

    function switchEntryTab(tab) {
      document.getElementById('formMemorySection').classList.add('hidden');
      document.getElementById('formVaccineSection').classList.add('hidden');
      document.getElementById('formMedSection').classList.add('hidden');
      
      document.getElementById('tabMemoryBtn').className = "px-2.5 py-1 rounded-lg text-stone-600";
      document.getElementById('tabVaccineBtn').className = "px-2.5 py-1 rounded-lg text-stone-600";
      document.getElementById('tabMedBtn').className = "px-2.5 py-1 rounded-lg text-stone-600";

      if (tab === 'memory') {
        document.getElementById('formMemorySection').classList.remove('hidden');
        document.getElementById('tabMemoryBtn').className = "px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs";
      } else if (tab === 'vaccine') {
        document.getElementById('formVaccineSection').classList.remove('hidden');
        document.getElementById('tabVaccineBtn').className = "px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs";
        document.getElementById('vDateGiven').value = new Date().toISOString().split('T')[0];
      } else {
        document.getElementById('formMedSection').classList.remove('hidden');
        document.getElementById('tabMedBtn').className = "px-2.5 py-1 rounded-lg bg-white text-stone-900 shadow-2xs";
        document.getElementById('medDate').value = new Date().toISOString().split('T')[0];
      }
    }

    async function calculateKundli() {
      const bCity = document.getElementById('bCity').value.trim() || "Gondia";
      const bDate = document.getElementById('bDate').value;
      const bTime = document.getElementById('bTime').value;
      if (!bDate || !bTime) return alert("Please fill date and time");

      const parts = bDate.split(/[-/]/);
      const tParts = bTime.split(':');
      const res = await fetch(`/api/kundli?y=${parts[0]}&m=${parts[1]}&d=${parts[2]}&h=${tParts[0]}&min=${tParts[1]}&city=${encodeURIComponent(bCity)}`);
      const data = await res.json();

      document.getElementById('resLagna').innerText = `${data.lagna_english} (${data.lagna_hindi})`;
      document.getElementById('resRashi').innerText = `${data.rashi_english} (${data.rashi_hindi})`;
      document.getElementById('resNakshatra').innerText = data.nakshatra_hindi;
      document.getElementById('resPada').innerText = `Pada ${data.charan}`;
      document.getElementById('resAkshar').innerText = data.naam_akshar_hindi;

      currentLetter = data.naam_akshar_hindi;
      document.getElementById('currentLetterBadge').innerText = currentLetter;
      document.getElementById('strictLetterText').innerText = currentLetter;
      document.getElementById('anumatiLetterText').innerText = currentLetter.replace(/[ािीुूृेैोौंः]/g, '');

      const lagnaNum = Number(data.lagna_rashi_num) || 1;
      const housesMap = data.houses_planets || {};

      for (let h = 1; h <= 12; h++) {
        let rashi = (lagnaNum + h - 2) % 12 + 1;
        let pList = housesMap[String(h)] || housesMap[h] || [];
        let grahHtml = pList.length > 0 ? `<div class="grah-container">${pList.map(p => `<span class="grah-badge">${p}</span>`).join('')}</div>` : '';
        const box = document.getElementById(`box${h}`);
        if (box) box.innerHTML = `<span class="rashi-no">${rashi}</span>${grahHtml}`;
      }

      document.getElementById('kundliResult').classList.remove('hidden');
      document.getElementById('namesSection').classList.remove('hidden');
      fetchAINames();
    }

    async function fetchAINames() {
      const listDiv = document.getElementById('namesList');
      listDiv.innerHTML = "";
      const res = await fetch(`/api/ai-names?letter=${encodeURIComponent(currentLetter)}&gender=${encodeURIComponent(selectedGender)}&mode=${encodeURIComponent(namingMode)}`);
      const names = await res.json();
      names.forEach(n => {
        listDiv.innerHTML += `
          <div class="p-3.5 bg-white rounded-xl border border-stone-200 shadow-2xs space-y-1">
            <div class="flex justify-between items-center">
              <h3 class="text-base font-extrabold text-stone-900">${n.name_hi} <span class="text-xs text-stone-500 font-sans">(${n.name_en})</span></h3>
              <button onclick="finalizeName('${n.name_hi}')" class="px-3 py-1 bg-amber-100 text-amber-950 rounded-xl text-xs font-black">👑 Select</button>
            </div>
            <p class="text-xs text-stone-700"><strong>Meaning:</strong> ${n.meaning}</p>
          </div>
        `;
      });
    }

    function finalizeName(name) {
      document.getElementById('cardFinalName').innerText = name;
      document.getElementById('cardFinalDate').innerText = document.getElementById('bDate').value;
      document.getElementById('cardFinalTime').innerText = document.getElementById('bTime').value;
      document.getElementById('profileSetupSection').classList.remove('hidden');
      document.getElementById('profileSetupSection').scrollIntoView({ behavior: 'smooth' });
    }

    function useCustomName() {
      const v = document.getElementById('customNameInput').value.trim();
      if (v) finalizeName(v);
    }

    async function createBabyProfileVault() {
      const name = document.getElementById('cardFinalName').innerText.trim();
      const pwd = document.getElementById('masterPasswordInput').value.trim();
      if (!name || pwd.length < 4) return alert("Name & 4+ char password required");

      const meta = {
        baby_name: name,
        city: document.getElementById('bCity').value,
        date: document.getElementById('bDate').value,
        time: document.getElementById('bTime').value,
        lagna: document.getElementById('resLagna').innerText,
        rashi: document.getElementById('resRashi').innerText,
        nakshatra: document.getElementById('resNakshatra').innerText,
        pada: document.getElementById('resPada').innerText,
        akshar: document.getElementById('resAkshar').innerText
      };

      const res = await fetch('/api/profile/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ baby_name: name, passphrase: pwd, meta_data: meta })
      });
      const data = await res.json();
      if (data.status === "ok") {
        activeSession = { profileHash: data.profile_hash, babyName: name, passphrase: pwd, meta: meta };
        localStorage.setItem('nd_prof_hash', data.profile_hash);
        localStorage.setItem('nd_baby_name', name);
        sessionStorage.setItem('nd_passphrase', pwd);
        localStorage.setItem('nd_baby_meta', JSON.stringify(meta));
        alert("🎉 Profile registered & cloud synced!");
        showVaultDashboard();
      }
    }

    async function loginToVault() {
      const name = document.getElementById('loginBabyName').value.trim();
      const pwd = document.getElementById('loginPassword').value.trim();
      if (!name || !pwd) return alert("Provide name & password");

      const res = await fetch('/api/profile/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ baby_name: name, passphrase: pwd })
      });
      const data = await res.json();
      if (data.status === "ok") {
        activeSession = { profileHash: data.profile_hash, babyName: name, passphrase: pwd, meta: data.meta };
        localStorage.setItem('nd_prof_hash', data.profile_hash);
        localStorage.setItem('nd_baby_name', name);
        sessionStorage.setItem('nd_passphrase', pwd);
        localStorage.setItem('nd_baby_meta', JSON.stringify(data.meta));
        toggleVaultModal();
        showVaultDashboard();
      } else {
        alert("⚠️ " + data.message);
      }
    }

    function logoutVault() {
      localStorage.clear();
      sessionStorage.clear();
      activeSession = { profileHash: '', babyName: '', passphrase: '', meta: {} };
      document.getElementById('vaultDashboard').classList.add('hidden');
      document.getElementById('activeProfileBanner').classList.add('hidden');
      alert("🔒 Vault locked.");
      window.location.reload();
    }

    function showVaultDashboard() {
      document.getElementById('activeProfileBanner').classList.remove('hidden');
      document.getElementById('activeBabyNameDisplay').innerText = activeSession.babyName;
      document.getElementById('vaultHeadingBabyName').innerText = activeSession.babyName;
      document.getElementById('vaultDashboard').classList.remove('hidden');
      triggerSyncAndReload(true);
    }

    async function saveNewMilestone() {
      const notes = document.getElementById('mNotes').value.trim();
      if (!notes) return alert("Write memory story");
      const tag = document.getElementById('mPresetTag').value;
      const dt = document.getElementById('mEventDate').value || new Date().toISOString().split('T')[0];

      await fetch('/api/milestones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_hash: activeSession.profileHash,
          passphrase: activeSession.passphrase,
          event_tag: tag,
          details: { category: "MEMORY", title: tag, notes: notes, eventDate: dt }
        })
      });
      document.getElementById('mNotes').value = "";
      triggerSyncAndReload(true);
    }

    async function saveVaccinationRecord() {
      const vName = document.getElementById('vName').value.trim();
      const vClinic = document.getElementById('vClinic').value.trim();
      const vDate = document.getElementById('vDateGiven').value;
      const vDue = document.getElementById('vNextDue').value;
      const exp = document.getElementById('vExperience').value.trim();
      if (!vName) return alert("Enter vaccine name");

      await fetch('/api/milestones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_hash: activeSession.profileHash,
          passphrase: activeSession.passphrase,
          event_tag: `💉 Vaccine: ${vName}`,
          details: { category: "VACCINE", vaccineName: vName, clinic: vClinic, dateGiven: vDate, nextDue: vDue, experience: exp, eventDate: vDate }
        })
      });
      document.getElementById('vName').value = "";
      document.getElementById('vExperience').value = "";
      triggerSyncAndReload(true);
    }

    async function saveMedicationRecord() {
      const doc = document.getElementById('medDoctor').value.trim();
      const dt = document.getElementById('medDate').value;
      const prob = document.getElementById('medProblem').value.trim();
      const presc = document.getElementById('medPrescription').value.trim();
      const exp = document.getElementById('medExperience').value.trim();
      if (!prob) return alert("Enter problem/symptoms");

      await fetch('/api/milestones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_hash: activeSession.profileHash,
          passphrase: activeSession.passphrase,
          event_tag: `🩺 Medical: ${prob}`,
          details: { category: "MEDICATION", doctor: doc, dateVisit: dt, problem: prob, prescription: presc, experience: exp, eventDate: dt }
        })
      });
      document.getElementById('medProblem').value = "";
      document.getElementById('medPrescription').value = "";
      document.getElementById('medExperience').value = "";
      triggerSyncAndReload(true);
    }

    async function triggerSyncAndReload() {
      const res = await fetch(`/api/milestones/get?prof_hash=${encodeURIComponent(activeSession.profileHash)}&pass=${encodeURIComponent(activeSession.passphrase)}&t=${Date.now()}`);
      const list = await res.json();
      currentSavedMilestones = list;
      renderFeed(list);
    }

    function renderFeed(list) {
      const box = document.getElementById('albumView');
      box.innerHTML = "";
      list.forEach(item => {
        const d = item.data;
        if (d.category === "MEDICATION") {
          box.innerHTML += `
            <div class="p-4 bg-teal-50/60 rounded-2xl border border-teal-200 text-xs space-y-1.5 shadow-2xs">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-teal-950 text-sm">🩺 Medical Visit: ${d.problem}</span>
                <span class="text-[10px] bg-teal-100 text-teal-900 font-bold px-2 py-0.5 rounded-full">${d.dateVisit || d.eventDate}</span>
              </div>
              <p class="text-stone-700"><strong>Doctor/Clinic:</strong> ${d.doctor || 'Clinic'}</p>
              <div class="bg-white p-2 rounded-xl border border-teal-100"><strong>Prescription:</strong> ${d.prescription}</div>
              ${d.experience ? `<p class="text-stone-600 bg-white/70 p-2 rounded-xl"><strong>Care Notes:</strong> ${d.experience}</p>` : ''}
            </div>`;
        } else if (d.category === "VACCINE") {
          box.innerHTML += `
            <div class="p-4 bg-blue-50/60 rounded-2xl border border-blue-200 text-xs space-y-1.5 shadow-2xs">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-blue-950 text-sm">💉 ${d.vaccineName}</span>
                <span class="text-[10px] bg-blue-100 text-blue-900 font-bold px-2 py-0.5 rounded-full">${d.dateGiven}</span>
              </div>
              <p class="text-stone-700"><strong>Clinic:</strong> ${d.clinic} ${d.nextDue ? `| <span class="text-rose-700 font-bold">Next Due: ${d.nextDue}</span>` : ''}</p>
              ${d.experience ? `<p class="bg-white p-2 rounded-xl border border-blue-100"><strong>Reaction & Story:</strong> ${d.experience}</p>` : ''}
            </div>`;
        } else {
          box.innerHTML += `
            <div class="p-4 bg-white rounded-2xl border border-stone-200 text-xs space-y-1.5 shadow-2xs">
              <div class="flex justify-between items-center">
                <span class="font-extrabold text-amber-950 text-sm">🌟 ${item.event_tag}</span>
                <span class="text-[10px] bg-stone-100 text-stone-500 font-bold px-2 py-0.5 rounded-full">${d.eventDate}</span>
              </div>
              <p class="text-stone-700 bg-stone-50 p-2.5 rounded-xl whitespace-pre-wrap">${d.notes}</p>
            </div>`;
        }
      });
    }

    async function confirmDeleteVault() {
      const pwd = document.getElementById('deleteConfirmPassword').value.trim();
      if (!pwd) return alert("Enter password");
      const res = await fetch('/api/vault/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_hash: activeSession.profileHash, passphrase: pwd })
      });
      const data = await res.json();
      if (data.status === "ok") {
        logoutVault();
      } else {
        alert("Error: " + data.message);
      }
    }

    // SELECTIVE PDF EXPORT
    function executePDFExport(mode) {
      toggleExportModal();
      const m = activeSession.meta || {};
      document.getElementById('pdfBabyName').innerText = activeSession.babyName;
      document.getElementById('pdfBirthDate').innerText = `Date: ${m.date || '-'}`;
      document.getElementById('pdfBirthTime').innerText = `Time: ${m.time || '-'}`;
      document.getElementById('pdfBirthCity').innerText = `Place: ${m.city || '-'}`;
      document.getElementById('pdfLagna').innerText = m.lagna || '-';
      document.getElementById('pdfRashi').innerText = m.rashi || '-';
      document.getElementById('pdfNakshatra').innerText = `${m.nakshatra || '-'} (${m.pada || '-'})`;
      document.getElementById('pdfAkshar').innerText = m.akshar || '-';

      // Clone Chart
      const chartClone = document.getElementById('pdfChartClone');
      chartClone.innerHTML = "";
      const originalBox = document.getElementById('mainKundliBox');
      if (originalBox) chartClone.appendChild(originalBox.cloneNode(true));

      // Filter list
      let filtered = currentSavedMilestones;
      if (mode === "MEMORIES") filtered = currentSavedMilestones.filter(x => x.data.category === "MEMORY");
      if (mode === "VACCINES") filtered = currentSavedMilestones.filter(x => x.data.category === "VACCINE");
      if (mode === "MEDS") filtered = currentSavedMilestones.filter(x => x.data.category === "MEDICATION");

      document.getElementById('pdfKundliSectionBlock').style.display = (mode === "VACCINES" || mode === "MEDS") ? "none" : "block";

      const titles = {
        "ALL": "📖 Complete Lifetime Vedic, Health & Memory Journal",
        "MEMORIES": "🌟 Vedic Janmapatri & Milestone Memories",
        "VACCINES": "💉 Official Immunization & Vaccination Record",
        "MEDS": "🩺 Pediatric Medical Visits & Prescription Log"
      };
      document.getElementById('pdfSectionHeading').innerText = titles[mode];

      const out = document.getElementById('pdfEntriesList');
      out.innerHTML = "";
      filtered.forEach(item => {
        const d = item.data;
        if (d.category === "MEDICATION") {
          out.innerHTML += `
            <div style="background: #F0FDFA; border-left: 4px solid #0D9488; padding: 10px; margin-bottom: 8px; border-radius: 6px;">
              <strong>🩺 ${d.problem}</strong> | Date: ${d.dateVisit} | Doctor: ${d.doctor}
              <div style="margin-top: 4px;"><strong>Medicines:</strong> ${d.prescription}</div>
              ${d.experience ? `<div style="color: #4B5563; margin-top: 2px;">Care: ${d.experience}</div>` : ''}
            </div>`;
        } else if (d.category === "VACCINE") {
          out.innerHTML += `
            <div style="background: #EFF6FF; border-left: 4px solid #2563EB; padding: 10px; margin-bottom: 8px; border-radius: 6px;">
              <strong>💉 ${d.vaccineName}</strong> | Given: ${d.dateGiven} ${d.nextDue ? `| Due: ${d.nextDue}` : ''}
              <div>Clinic: ${d.clinic}</div>
              ${d.experience ? `<div>Reaction: ${d.experience}</div>` : ''}
            </div>`;
        } else {
          out.innerHTML += `
            <div style="background: #FFFDF9; border-left: 4px solid #D97706; padding: 10px; margin-bottom: 8px; border-radius: 6px;">
              <strong>🌟 ${item.event_tag}</strong> | Date: ${d.eventDate}
              <div style="margin-top: 4px;">${d.notes}</div>
            </div>`;
        }
      });

      const opt = {
        margin: [6, 6, 6, 6],
        filename: `${activeSession.babyName}_${mode}_Album.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      html2pdf().set(opt).from(document.getElementById('pdfPrintCanvas')).save();
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

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        payload = json.loads(body.decode('utf-8'))

        if self.path == "/api/profile/register":
            res = register_profile(payload['baby_name'], payload['passphrase'], payload['meta_data'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        elif self.path == "/api/profile/login":
            res = login_profile(payload['baby_name'], payload['passphrase'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        elif self.path == "/api/milestones/add":
            add_profile_milestone(payload['profile_hash'], payload['passphrase'], payload['event_tag'], payload['details'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
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
