import os, json, time, hmac, hashlib, threading
from datetime import datetime, timezone
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
WA_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID", "")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
ALLOWED = {n.strip() for n in os.environ.get("ALLOWED_NUMBERS", "").split(",") if n.strip()}
APP_SECRET = os.environ.get("META_APP_SECRET", "")  # optional, enables signature check

SYSTEM = (
    "You are Amar's personal WhatsApp assistant. Amar is a B.Tech AI/ML student in Hyderabad. "
    "He writes in Hinglish; reply in the same Hinglish style, short and clear, like WhatsApp chat. "
    "Help him with questions, studying, coding (Python, Java, JS), and tracking internships, "
    "hackathons and scholarships. If he asks you to save a task or deadline, use the tracker "
    "commands and tell him about them: /add <text>, /list, /done <number>, /clear (clears chat memory). "
    "Never claim you did something you cannot do. You cannot browse or fill forms."
)

HISTORY = {}   # number -> list of {role, parts}
MAX_TURNS = 20
TASK_FILE = "tasks.json"  # note: Render free disk is wiped on restart/redeploy
LOCK = threading.Lock()
SEEN = set()


def load_tasks():
    try:
        with open(TASK_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_tasks(t):
    with open(TASK_FILE, "w") as f:
        json.dump(t, f)


def send(to, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WA_TOKEN}"}
    for i in range(0, len(text), 3500):
        r = requests.post(url, headers=headers, timeout=20, json={
            "messaging_product": "whatsapp", "to": to, "type": "text",
            "text": {"body": text[i:i + 3500]}})
        if r.status_code >= 300:
            print("send error", r.status_code, r.text, flush=True)


def ask_gemini(number, text):
    hist = HISTORY.setdefault(number, [])
    hist.append({"role": "user", "parts": [{"text": text}]})
    del hist[:-MAX_TURNS * 2]
    today = datetime.now(timezone.utc).strftime("%A %d %B %Y (UTC)")
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM + f" Today is {today}."}]},
        "contents": hist,
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    for attempt in range(3):
        r = requests.post(url, params={"key": GEMINI_KEY}, json=body, timeout=40)
        if r.status_code == 429:
            time.sleep(3 * (attempt + 1))
            continue
        break
    if r.status_code != 200:
        print("gemini error", r.status_code, r.text[:300], flush=True)
        hist.pop()
        return "Abhi AI busy hai (limit ya error). Thodi der baad try kar."
    try:
        reply = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        hist.pop()
        return "Jawab nahi mil paya, dobara bhej."
    hist.append({"role": "model", "parts": [{"text": reply}]})
    return reply


def handle_command(number, text):
    t = text.strip()
    low = t.lower()
    with LOCK:
        tasks = load_tasks()
        mine = tasks.setdefault(number, [])
        if low.startswith("/add"):
            item = t[4:].strip()
            if not item:
                return "Aise likh: /add Amazon internship form 5 Oct"
            mine.append({"text": item, "done": False})
            save_tasks(tasks)
            return f"Add ho gaya (#{len(mine)}): {item}"
        if low == "/list":
            if not mine:
                return "List khali hai. /add se kuch daal."
            return "\n".join(f"{i+1}. {'✅' if x['done'] else '⬜'} {x['text']}" for i, x in enumerate(mine))
        if low.startswith("/done"):
            try:
                n = int(t[5:].strip())
                mine[n - 1]["done"] = True
                save_tasks(tasks)
                return f"Done: {mine[n-1]['text']}"
            except Exception:
                return "Aise likh: /done 2"
    if low == "/clear":
        HISTORY.pop(number, None)
        return "Chat memory clear kar di."
    if low in ("/help", "help"):
        return "Commands: /add <text>, /list, /done <no>, /clear. Baaki kuch bhi pooch, AI jawab dega."
    return None


def process(msg):
    number = msg.get("from", "")
    if ALLOWED and number not in ALLOWED:
        print("ignored number", number, flush=True)
        return
    if msg.get("type") != "text":
        send(number, "Abhi sirf text samajh sakta hoon.")
        return
    text = msg["text"]["body"]
    out = handle_command(number, text) if text.strip().startswith("/") or text.strip().lower() == "help" else None
    if out is None:
        out = ask_gemini(number, text)
    send(number, out)


@app.get("/")
def health():
    return "ok"


@app.get("/webhook")
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN and VERIFY_TOKEN:
        return request.args.get("hub.challenge", ""), 200
    return "forbidden", 403


@app.post("/webhook")
def webhook():
    if APP_SECRET:
        sig = request.headers.get("X-Hub-Signature-256", "")
        exp = "sha256=" + hmac.new(APP_SECRET.encode(), request.get_data(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, exp):
            return "bad signature", 403
    data = request.get_json(silent=True) or {}
    for entry in data.get("entry", []):
        for ch in entry.get("changes", []):
            for msg in ch.get("value", {}).get("messages", []) or []:
                mid = msg.get("id")
                if mid in SEEN:
                    continue
                SEEN.add(mid)
                threading.Thread(target=process, args=(msg,), daemon=True).start()
    return jsonify(ok=True), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
