import sqlite3
import os
import json
import base64
import hashlib
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DB_FILE = "milestones.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Blind hashed profile key and encrypted profile metadata table
    c.execute('''
        CREATE TABLE IF NOT EXISTS baby_profiles (
            profile_hash TEXT PRIMARY KEY,
            enc_profile_meta TEXT,
            meta_nonce TEXT,
            meta_salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Encrypted milestones table
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

def register_or_login_profile(baby_name: str, passphrase: str, meta_data: dict = None):
    init_db()
    prof_hash = generate_profile_hash(baby_name, passphrase)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    row = c.fetchone()

    if row:
        meta = decrypt_payload(passphrase, row[0], row[1], row[2])
        conn.close()
        if meta is None:
            return {"status": "error", "message": "Galat password ya baby name"}
        return {"status": "ok", "profile_hash": prof_hash, "meta": meta, "is_new": False}
    else:
        if not meta_data:
            meta_data = {
                "baby_name": baby_name,
                "created_at": datetime.datetime.now().isoformat()
            }
        c_text, nonce, salt = encrypt_payload(passphrase, meta_data)
        c.execute('''
            INSERT INTO baby_profiles (profile_hash, enc_profile_meta, meta_nonce, meta_salt)
            VALUES (?, ?, ?, ?)
        ''', (prof_hash, c_text, nonce, salt))
        conn.commit()
        conn.close()
        return {"status": "ok", "profile_hash": prof_hash, "meta": meta_data, "is_new": True}

def add_profile_milestone(prof_hash: str, passphrase: str, event_tag: str, details: dict):
    init_db()
    c_text, nonce, salt = encrypt_payload(passphrase, details)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO milestones (profile_hash, event_tag, ciphertext, nonce, salt)
        VALUES (?, ?, ?, ?, ?)
    ''', (prof_hash, event_tag, c_text, nonce, salt))
    conn.commit()
    conn.close()

def get_profile_milestones(prof_hash: str, passphrase: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT event_tag, ciphertext, nonce, salt, created_at 
        FROM milestones 
        WHERE profile_hash = ? 
        ORDER BY id DESC
    ''', (prof_hash,))
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        tag, c_text, nonce, salt, created_at = r
        decrypted = decrypt_payload(passphrase, c_text, nonce, salt)
        if decrypted is not None:
            results.append({
                "event_tag": tag,
                "data": decrypted,
                "created_at": created_at
            })
    return results

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
        "version": "2.0_vault",
        "profile_hash": prof_hash,
        "profile_meta": {"enc": p_row[0], "nonce": p_row[1], "salt": p_row[2]},
        "milestones": [
            {"event_tag": m[0], "ciphertext": m[1], "nonce": m[2], "salt": m[3], "created_at": m[4]}
            for m in m_rows
        ]
    }

def import_single_profile_backup(backup_dict: dict):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    prof_hash = backup_dict['profile_hash']
    pm = backup_dict['profile_meta']

    c.execute('''
        INSERT OR REPLACE INTO baby_profiles (profile_hash, enc_profile_meta, meta_nonce, meta_salt)
        VALUES (?, ?, ?, ?)
    ''', (prof_hash, pm['enc'], pm['nonce'], pm['salt']))

    imported_count = 0
    for m in backup_dict.get('milestones', []):
        c.execute('''
            INSERT INTO milestones (profile_hash, event_tag, ciphertext, nonce, salt, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (prof_hash, m['event_tag'], m['ciphertext'], m['nonce'], m['salt'], m.get('created_at')))
        imported_count += 1

    conn.commit()
    conn.close()
    return imported_count

def delete_profile_vault(prof_hash: str, passphrase: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Pehle Master Password ko decrypt karke verify karein
    c.execute("SELECT enc_profile_meta, meta_nonce, meta_salt FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": "Profile nahi mili"}

    meta = decrypt_payload(passphrase, row[0], row[1], row[2])
    if meta is None:
        conn.close()
        return {"status": "error", "message": "Galat password! Vault delete nahi ho sakta"}

    # 2. Sahi password hone par profile aur uske saare milestones database se wipe karein
    c.execute("DELETE FROM baby_profiles WHERE profile_hash = ?", (prof_hash,))
    c.execute("DELETE FROM milestones WHERE profile_hash = ?", (prof_hash,))
    conn.commit()
    conn.close()
    return {"status": "ok"}
