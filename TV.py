import sqlite3
import os
import json
import base64
import hashlib
import urllib.request
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DB_FILE = "milestones.db"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
FILE_PATH = "data.json"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS baby_profiles (
            profile_hash TEXT PRIMARY KEY,
            enc_profile_meta TEXT,
            meta_nonce TEXT,
            meta_salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_hash TEXT,
            event_tag TEXT,
            ciphertext TEXT,
            nonce TEXT,
            salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    pull_from_github()

def generate_profile_hash(baby_name: str, passphrase: str) -> str:
    norm = f"{baby_name.strip().lower()}::{passphrase.strip()}"
    return hashlib.sha256(norm.encode('utf-8')).hexdigest()

def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(passphrase.encode('utf-8'))

def encrypt_payload(passphrase: str, data: dict):
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = json.dumps(data).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return (
        base64.b64encode(ciphertext).decode('utf-8'),
        base64.b64encode(nonce).decode('utf-8'),
        base64.b64encode(salt).decode('utf-8')
    )

def decrypt_payload(passphrase: str, ciphertext_b64: str, nonce_b64: str, salt_b64: str):
    try:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        salt = base64.b64decode(salt_b64)
        key = derive_key(passphrase, salt)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode('utf-8'))
    except Exception:
        return None

# --- GITHUB AUTO SYNC ENGINE ---
def push_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT profile_hash, enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles")
        p_rows = c.fetchall()
        c.execute("SELECT profile_hash, event_tag, ciphertext, nonce, salt, created_at FROM milestones")
        m_rows = c.fetchall()
        conn.close()

        dump = {
            "profiles": [{"h": r[0], "e": r[1], "n": r[2], "s": r[3]} for r in p_rows],
            "milestones": [{"h": r[0], "t": r[1], "c": r[2], "n": r[3], "s": r[4], "d": r[5]} for r in m_rows]
        }
        content_str = json.dumps(dump, indent=2)
        b64_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "NanhiDuniya-CloudSync"
        })

        sha = None
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                sha = data.get("sha")
        except Exception:
            pass

        body = {
            "message": "🔒 Auto-Sync: Encrypted Cloud Vault State",
            "content": b64_content,
            "branch": GITHUB_BRANCH
        }
        if sha:
            body["sha"] = sha

        put_req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method="PUT", headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "NanhiDuniya-CloudSync"
        })
        urllib.request.urlopen(put_req)
    except Exception as err:
        print("GitHub Sync Push Error:", err)

def pull_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}?ref={GITHUB_BRANCH}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "NanhiDuniya-CloudSync"
        })
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            raw_json = base64.b64decode(data["content"]).decode('utf-8')
            dump = json.loads(raw_json)

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            for p in dump.get("profiles", []):
                c.execute("INSERT OR REPLACE INTO baby_profiles VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (p["h"], p["e"], p["n"], p["s"]))
            for m in dump.get("milestones", []):
                c.execute("INSERT OR IGNORE INTO milestones (profile_hash, event_tag, ciphertext, nonce, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)", (m["h"], m["t"], m["c"], m["n"], m["s"], m["d"]))
            conn.commit()
            conn.close()
    except Exception as err:
        print("GitHub Sync Pull Error (fresh repo):", err)

# --- REPOSITORY CORE OPERATIONS ---
def register_profile(baby_name: str, passphrase: str, meta_data: dict):
    init_db()
    prof_hash = generate_profile_hash(baby_name, passphrase)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c_text, nonce, salt = encrypt_payload(passphrase, meta_data)
    c.execute("INSERT OR REPLACE INTO baby_profiles (profile_hash, enc_profile_meta, meta_nonce, meta_salt) VALUES (?, ?, ?, ?)", (prof_hash, c_text, nonce, salt))
    conn.commit()
    conn.close()
    push_to_github()
    return {"status": "ok", "profile_hash": prof_hash, "meta": meta_data}

def login_profile(baby_name: str, passphrase: str):
    init_db()
    prof_hash = generate_profile_hash(baby_name, passphrase)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"status": "error", "message": "No profile found! This profile does not exist or was permanently deleted."}
    meta = decrypt_payload(passphrase, row[0], row[1], row[2])
    if meta is None:
        return {"status": "error", "message": "Incorrect Master Password!"}
    return {"status": "ok", "profile_hash": prof_hash, "meta": meta}

def add_profile_milestone(prof_hash: str, passphrase: str, event_tag: str, details: dict):
    init_db()
    c_text, nonce, salt = encrypt_payload(passphrase, details)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO milestones (profile_hash, event_tag, ciphertext, nonce, salt) VALUES (?, ?, ?, ?, ?)", (prof_hash, event_tag, c_text, nonce, salt))
    conn.commit()
    conn.close()
    push_to_github()

def get_profile_milestones(prof_hash: str, passphrase: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, event_tag, ciphertext, nonce, salt, created_at FROM milestones WHERE profile_hash = ? ORDER BY id DESC", (prof_hash,))
    rows = c.fetchall()
    conn.close()
    results = []
    for r in rows:
        dec = decrypt_payload(passphrase, r[2], r[3], r[4])
        if dec is not None:
            results.append({"id": r[0], "event_tag": r[1], "data": dec, "created_at": r[5]})
    return results

def edit_profile_milestone(prof_hash: str, passphrase: str, milestone_id: int, new_details: dict):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ciphertext, nonce, salt FROM milestones WHERE id = ? AND profile_hash = ?", (milestone_id, prof_hash))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": "Record not found"}
    if decrypt_payload(passphrase, row[0], row[1], row[2]) is None:
        conn.close()
        return {"status": "error", "message": "Incorrect Master Password!"}
    c_text, nonce, salt = encrypt_payload(passphrase, new_details)
    c.execute("UPDATE milestones SET ciphertext = ?, nonce = ?, salt = ? WHERE id = ? AND profile_hash = ?", (c_text, nonce, salt, milestone_id, prof_hash))
    conn.commit()
    conn.close()
    push_to_github()
    return {"status": "ok"}

def delete_profile_vault(prof_hash: str, passphrase: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": "Profile not found"}
    if decrypt_payload(passphrase, row[0], row[1], row[2]) is None:
        conn.close()
        return {"status": "error", "message": "Incorrect Master Password!"}
    c.execute("DELETE FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    c.execute("DELETE FROM milestones WHERE profile_hash = ?", (prof_hash,))
    conn.commit()
    conn.close()
    push_to_github()
    return {"status": "ok"}

def export_single_profile_backup(prof_hash: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    p_row = c.fetchone()
    if not p_row:
        conn.close()
        return None
    c.execute("SELECT event_tag, ciphertext, nonce, salt, created_at FROM milestones WHERE profile_hash = ?", (prof_hash,))
    m_rows = c.fetchall()
    conn.close()
    return {
        "version": "3.0_vault",
        "profile_hash": prof_hash,
        "profile_meta": {"enc": p_row[0], "nonce": p_row[1], "salt": p_row[2]},
        "milestones": [{"event_tag": m[0], "ciphertext": m[1], "nonce": m[2], "salt": m[3], "created_at": m[4]} for m in m_rows]
    }

def import_single_profile_backup(backup_dict: dict):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    prof_hash = backup_dict['profile_hash']
    pm = backup_dict['profile_meta']
    c.execute("INSERT OR REPLACE INTO baby_profiles VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (prof_hash, pm['enc'], pm['nonce'], pm['salt']))
    imported_count = 0
    for m in backup_dict.get('milestones', []):
        c.execute("INSERT INTO milestones (profile_hash, event_tag, ciphertext, nonce, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)", (prof_hash, m['event_tag'], m['ciphertext'], m['nonce'], m['salt'], m.get('created_at')))
        imported_count += 1
    conn.commit()
    conn.close()
    push_to_github()
    return imported_count
