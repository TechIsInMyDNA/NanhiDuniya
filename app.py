from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
DATA_FILE = "profiles.json"

def load_profiles():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_profiles(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/create-profile", methods=["POST"])
def create_profile():
    payload = request.json or {}
    baby_name = payload.get("baby_name", "").strip()
    password = payload.get("password", "").strip()
    dob = payload.get("dob")
    tob = payload.get("tob")
    pob = payload.get("pob")

    if not baby_name or not password:
        return jsonify({"status": "error", "message": "Baby name aur Password zaroori hai!"}), 400

    profiles = load_profiles()
    profile_id = baby_name.lower().replace(" ", "_")

    profiles[profile_id] = {
        "profile_id": profile_id,
        "baby_name": baby_name,
        "password": password,
        "dob": dob,
        "tob": tob,
        "pob": pob,
        "memories": [],
        "medical_logs": []
    }
    save_profiles(profiles)
    return jsonify({"status": "success", "profile": profiles[profile_id]})

@app.route("/api/unlock-profile", methods=["POST"])
def unlock_profile():
    payload = request.json or {}
    profile_id = payload.get("profile_id", "").strip().lower().replace(" ", "_")
    password = payload.get("password", "").strip()

    profiles = load_profiles()
    profile = profiles.get(profile_id)

    if not profile or profile.get("password") != password:
        return jsonify({"status": "error", "message": "Galat naam ya password!"}), 401

    return jsonify({"status": "success", "profile": profile})

@app.route("/api/add-record", methods=["POST"])
def add_record():
    payload = request.json or {}
    profile_id = payload.get("profile_id")
    record_type = payload.get("type") # 'medical_logs' ya 'memories'
    entry = payload.get("entry")

    profiles = load_profiles()
    if profile_id in profiles and record_type in profiles[profile_id]:
        profiles[profile_id][record_type].append(entry)
        save_profiles(profiles)
        return jsonify({"status": "success", "profile": profiles[profile_id]})

    return jsonify({"status": "error", "message": "Update fail hua"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
