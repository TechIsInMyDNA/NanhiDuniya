import sqlite3
import os
import json
import base64
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DB_FILE = "milestones.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id TEXT,
            event_tag TEXT,
            ciphertext TEXT,
            nonce TEXT,
            salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(passphrase.encode())

def encrypt_data(passphrase: str, data: dict):
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

def decrypt_data(passphrase: str, ciphertext_b64: str, nonce_b64: str, salt_b64: str):
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

def add_milestone(baby_id: str, passphrase: str, event_tag: str, details: dict):
    init_db()
    c_text, nonce, salt = encrypt_data(passphrase, details)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO milestones (baby_id, event_tag, ciphertext, nonce, salt)
        VALUES (?, ?, ?, ?, ?)
    ''', (baby_id, event_tag, c_text, nonce, salt))
    conn.commit()
    conn.close()

def get_milestones(baby_id: str, passphrase: str):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT event_tag, ciphertext, nonce, salt, created_at 
        FROM milestones 
        WHERE baby_id = ? 
        ORDER BY id DESC
    ''', (baby_id,))
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        tag, c_text, nonce, salt, created_at = r
        decrypted = decrypt_data(passphrase, c_text, nonce, salt)
        if decrypted is not None:
            results.append({
                "event_tag": tag,
                "data": decrypted,
                "created_at": created_at
            })
    return results

def export_raw_backup():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT baby_id, event_tag, ciphertext, nonce, salt, created_at FROM milestones")
    rows = c.fetchall()
    conn.close()
    
    backup_data = []
    for r in rows:
        backup_data.append({
            "baby_id": r[0],
            "event_tag": r[1],
            "ciphertext": r[2],
            "nonce": r[3],
            "salt": r[4],
            "created_at": r[5]
        })
    return backup_data

def import_raw_backup(backup_list):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    imported_count = 0
    for item in backup_list:
        try:
            c.execute('''
                INSERT INTO milestones (baby_id, event_tag, ciphertext, nonce, salt, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['baby_id'],
                item['event_tag'],
                item['ciphertext'],
                item['nonce'],
                item['salt'],
                item.get('created_at', datetime.datetime.now().isoformat())
            ))
            imported_count += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return imported_count

