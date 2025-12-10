from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cv2, os, numpy as np, base64, smtplib, random, time, json, shutil, math
from email.mime.text import MIMEText
from io import BytesIO
from PIL import Image
from pathlib import Path
import secrets

app = Flask(__name__, static_folder="static", template_folder=".")
app.secret_key = secrets.token_hex(16)

BASE_DIR = Path.cwd()
USERS_DIR = BASE_DIR / "users"
TRAINER_DIR = BASE_DIR / "trainer"
EMB_FILE = TRAINER_DIR / "embeddings.npz"         
LABELS_FILE = TRAINER_DIR / "labels.json"         
TMP_SIGNUP_DIR = BASE_DIR / "tmp_signup"
MODELS_DIR = BASE_DIR / "models"
OPENFACE_T7 = MODELS_DIR / "nn4.small2.v1.t7"      

for d in (USERS_DIR, TRAINER_DIR, TMP_SIGNUP_DIR, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

embedder = None
use_embeddings = False
lbph_recognizer = None

def _try_load_embedder():
    global embedder, use_embeddings, lbph_recognizer
    if OPENFACE_T7.exists():
        try:
            embedder = cv2.dnn.readNetFromTorch(str(OPENFACE_T7))
            use_embeddings = True
            print("OpenFace embedder loaded.")
            return
        except Exception as e:
            print("Could not load OpenFace model:", e)

    try:
        lbph_recognizer = cv2.face.LBPHFaceRecognizer_create()
        trainer_yml = TRAINER_DIR / "trainer.yml"
        if trainer_yml.exists():
            try:
                lbph_recognizer.read(str(trainer_yml))
                print("Using LBPH fallback (model file missing).")
            except Exception:
                pass
    except Exception:
        pass

_try_load_embedder()

signup_otp_store = {}   
login_otp_store  = {}   

SMTP_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'use your gmail',
    'password': 'use your gmail password',
    'from_email': 'use your gmail',
    'from_name': 'DEMO FACE SIGNING'
}

def send_email(to_email, subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SMTP_CONFIG['from_email']
        msg['To'] = to_email
        server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['from_email'], to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False
    
def decode_image(data_url):
    header, encoded = data_url.split(",", 1)
    return Image.open(BytesIO(base64.b64decode(encoded)))

def id_for_name(name: str) -> int:
    return int(abs(hash(name)) % 10000)

def _l2_normalize(v):
    n = np.linalg.norm(v) + 1e-10
    return v / n

def face_to_embedding(gray_img, box):
    """Return 128-D embedding using OpenFace; box=(x,y,w,h)."""
    (x, y, w, h) = box
    face = gray_img[y:y+h, x:x+w]
    if face.size == 0:
        return None
    face_rgb = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
    face_resized = cv2.resize(face_rgb, (96, 96))
    blob = cv2.dnn.blobFromImage(face_resized, 1.0/255.0, (96, 96), (0,0,0), swapRB=True, crop=False)
    embedder.setInput(blob)
    vec = embedder.forward()
    vec = vec.flatten().astype("float32")
    return _l2_normalize(vec)

def _detect_one(gray_img):
    
    if gray_img is None or gray_img.size == 0:
        return None
    try:
        if len(gray_img.shape) == 2:
            eq = cv2.equalizeHist(gray_img)
        else:
            eq = gray_img
    except Exception:
        eq = gray_img
    faces = face_cascade.detectMultiScale(eq, scaleFactor=1.1, minNeighbors=4)
    if len(faces) == 0:
        return None
    faces = sorted(faces, key=lambda b: b[2]*b[3], reverse=True)
    return faces[0]
def train_embeddings():
    """Build an embedding index for all users: saves EMB_FILE + LABELS_FILE."""
    if not use_embeddings:
        if lbph_recognizer is None:
            print("No embedder and no LBPH. Training skipped.")
            return False
        faces, ids = [], []
        for user_folder in USERS_DIR.iterdir():
            if not user_folder.is_dir(): continue
            user_id = id_for_name(user_folder.name)
            for img_file in user_folder.glob("*.jpg"):
                img = Image.open(img_file).convert("L")
                np_img = np.array(img, "uint8")
                box = _detect_one(np_img)
                if box is not None:
                    (x,y,w,h) = box
                    faces.append(np_img[y:y+h, x:x+w])
                    ids.append(user_id)
        if faces:
            lbph_recognizer.train(faces, np.array(ids))
            (TRAINER_DIR / "trainer.yml").parent.mkdir(parents=True, exist_ok=True)
            lbph_recognizer.save(str(TRAINER_DIR / "trainer.yml"))
            print("LBPH training complete (fallback).")
            return True
        print("No faces for LBPH fallback training.")
        return False
    X = []
    Y = []
    names = []
    name_to_idx = {}

    for user_folder in USERS_DIR.iterdir():
        if not user_folder.is_dir(): 
            continue
        user_name = user_folder.name
        for img_file in user_folder.glob("*.jpg"):
            try:
                img = Image.open(img_file).convert("L")
                np_img = np.array(img, "uint8")
                box = _detect_one(np_img)
                if box is None: 
                    continue
                emb = face_to_embedding(np_img, box)
                if emb is None: 
                    continue
                X.append(emb)
                if user_name not in name_to_idx:
                    name_to_idx[user_name] = len(names)
                    names.append(user_name)
                Y.append(name_to_idx[user_name])
            except Exception:
                continue

    if len(X) == 0:
        print("No faces found for embedding training.")
        return False

    X = np.vstack(X).astype("float32")
    Y = np.array(Y, dtype="int32")
    np.savez_compressed(str(EMB_FILE), X=X, Y=Y)
    with open(LABELS_FILE, "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)
    print(f"Embedding index built: {X.shape[0]} samples, {len(names)} users.")
    return True

def _load_index():
    if EMB_FILE.exists() and LABELS_FILE.exists() and use_embeddings:
        data = np.load(str(EMB_FILE))
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            names = json.load(f)
        return data["X"].astype("float32"), data["Y"].astype("int32"), names
    return None, None, None
def identify_face(gray_img):
    box = _detect_one(gray_img)
    if box is None:
        return ("no_face", None, None)
    if use_embeddings and embedder is not None:
        X, Y, names = _load_index()
        if X is None:
            return ("not_trained", None, None)
        q = face_to_embedding(gray_img, box)
        if q is None:
            return ("no_face", None, None)
        sims = (X @ q)
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])
        label = int(Y[best_idx])
        candidate = names[label]
        if best_sim >= 0.60:
            return ("match", candidate, best_sim)
        else:
            return ("not_found", None, best_sim)
    else:
        try:
            (x,y,w,h) = box
            face_id, confidence = lbph_recognizer.predict(gray_img[y:y+h, x:x+w])
            matched_user = None
            for user in USERS_DIR.iterdir():
                if not user.is_dir(): continue
                if id_for_name(user.name) == face_id:
                    matched_user = user.name
                    break
            if matched_user and confidence < 60:
                score = float(100 - confidence)
                return ("match", matched_user, score)
            return ("not_found", None, float(100 - confidence))
        except Exception as e:
            return ("recognizer_error", str(e), None)
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/api/signup", methods=["POST"])
def signup():
    
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    images = data.get("images", [])
    if not name or not email or not images or len(images) < 10:
        return jsonify({"success": False, "error": "Provide name, email and at least 10 images."})
    name_key = name.lower()

    tmp_folder = TMP_SIGNUP_DIR / f"{name}_{int(time.time())}_{secrets.token_hex(4)}"
    tmp_folder.mkdir(parents=True, exist_ok=True)
    for i, img_data in enumerate(images):
        try:
            pil_img = decode_image(img_data).convert("L")
            gray = np.array(pil_img, dtype="uint8")
            try:
                box = _detect_one(gray)
            except Exception:
                box = None
            if box is not None:
                x, y, w, h = box
                margin = int(max(w, h) * 0.2)
                x0 = max(0, x - margin)
                y0 = max(0, y - margin)
                x1 = min(gray.shape[1], x + w + margin)
                y1 = min(gray.shape[0], y + h + margin)
                face_crop = pil_img.crop((x0, y0, x1, y1))
            else:
                face_crop = pil_img
            face_crop = face_crop.resize((96, 96))
            face_crop.save(tmp_folder / f"{i+1}.jpg")
        except Exception as e:
            shutil.rmtree(tmp_folder, ignore_errors=True)
            return jsonify({"success": False, "error": f"Could not process image {i+1}: {e}"})

    otp = f"{random.randint(1000,9999)}"
    signup_otp_store[name_key] = {"otp": otp, "timestamp": time.time(), "tmp_folder": str(tmp_folder), "email": email}
    ok = send_email(email, "Confirm your Signup OTP", f"Your signup OTP is: {otp}\n(Valid for 5 minutes)")
    if not ok:
        return jsonify({"success": False, "error": "Failed to send OTP email. Check SMTP settings."})
    return jsonify({"success": True, "message": "OTP sent for signup confirmation."})

@app.route("/api/verify_signup_otp", methods=["POST"])
def verify_signup_otp():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    otp = (data.get("otp", "") or "").strip()
    if not name or not otp:
        return jsonify({"success": False, "error": "Missing name or OTP."})
    name_key = name.lower()

    if name_key not in signup_otp_store:
        return jsonify({"success": False, "error": "No pending signup found. Try signing up again."})

    record = signup_otp_store[name_key]
    if time.time() - record["timestamp"] > 300:
        shutil.rmtree(record.get("tmp_folder", ""), ignore_errors=True)
        del signup_otp_store[name_key]
        return jsonify({"success": False, "error": "OTP expired. Please sign up again."})

    if record["otp"] != otp:
        return jsonify({"success": False, "error": "Invalid OTP. Please check and try again."})

    user_folder = USERS_DIR / name
    user_folder.mkdir(parents=True, exist_ok=True)
    for f in Path(record["tmp_folder"]).glob("*.jpg"):
        dest = user_folder / f"{int(time.time())}_{f.name}"
        f.rename(dest)

    (user_folder / "email.txt").write_text(record["email"], encoding="utf-8")

    shutil.rmtree(record["tmp_folder"], ignore_errors=True)
    del signup_otp_store[name_key]
    trained = train_embeddings()
    return jsonify({"success": True, "message": "Signup confirmed and user registered.", "trained": bool(trained)})

@app.route("/api/identify", methods=["POST"])
def identify():
    data = request.get_json(silent=True) or {}
    image_data = data.get("image")
    if not image_data:
        return jsonify({"status": "no_image"})

    img = decode_image(image_data).convert("L")
    np_img = np.array(img, "uint8")
    status, user, score = identify_face(np_img)

    if status == "match":
        return jsonify({"status": "match", "user": user, "confidence": float(score)})
    elif status == "not_found":
        return jsonify({"status": "not_found", "confidence": float(score) if score is not None else None})
    elif status == "not_trained":
        return jsonify({"status": "not_trained"})
    elif status == "recognizer_error":
        return jsonify({"status": "recognizer_error"})
    elif status == "no_face":
        return jsonify({"status": "no_face"})
    else:
        return jsonify({"status": "unknown"})

@app.route("/api/send_login_otp", methods=["POST"])
def send_login_otp():
    data = request.get_json(silent=True) or {}
    user = data.get("user", "").strip()
    if not user:
        return jsonify({"success": False, "error": "No user provided."})
    email_path = USERS_DIR / user / "email.txt"
    if not email_path.exists():
        return jsonify({"success": False, "error": "User has no registered email."})
    user_email = email_path.read_text().strip()
    otp = f"{random.randint(1000,9999)}"
    login_otp_store[user.lower()] = {"otp": otp, "timestamp": time.time()}
    if send_email(user_email, "Your Login OTP", f"Your login OTP is: {otp}\n(Valid for 5 minutes)"):
        return jsonify({"success": True, "message": "OTP sent."})
    return jsonify({"success": False, "error": "Sending OTP failed."})

@app.route("/api/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True) or {}
    user = (data.get("user") or "").strip()
    otp = (data.get("otp") or "").strip()
    image_data = data.get("image")
    if not user or not otp:
        return jsonify({"success": False, "error": "Missing user or otp."})
    key = user.lower()
    record = login_otp_store.get(key)
    if not record:
        return jsonify({"success": False, "error": "OTP not found or expired."})
    if time.time() - record["timestamp"] > 300:
        del login_otp_store[key]
        return jsonify({"success": False, "error": "OTP expired."})
    if record["otp"] != otp:
        return jsonify({"success": False, "error": "Invalid OTP."})
    session["logged_in"] = True
    session["user"] = user
    del login_otp_store[key]
    if image_data:
        try:
            pil_img = decode_image(image_data).convert("L")
            gray = np.array(pil_img, dtype="uint8")
            try:
                box = _detect_one(gray)
            except Exception:
                box = None
            if box is not None:
                x, y, w, h = box
                margin = int(max(w, h) * 0.2)
                x0 = max(0, x - margin)
                y0 = max(0, y - margin)
                x1 = min(gray.shape[1], x + w + margin)
                y1 = min(gray.shape[0], y + h + margin)
                face_crop = pil_img.crop((x0, y0, x1, y1))
            else:
                face_crop = pil_img
            face_crop = face_crop.resize((96, 96))
            user_folder = USERS_DIR / user
            user_folder.mkdir(parents=True, exist_ok=True)
            filename = f"{int(time.time()*1000)}_login.jpg"
            face_crop.save(user_folder / filename)
            train_embeddings()
        except Exception as e:
            print("Could not process login image for training:", e)

    return jsonify({"success": True})

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("home"))
    return render_template("dashboard.html", user=session.get("user"))

@app.route("/api/health")
def health():
    mode = "embeddings" if use_embeddings else ("lbph" if lbph_recognizer is not None else "none")
    trained = EMB_FILE.exists() if use_embeddings else (TRAINER_DIR / "trainer.yml").exists()
    return jsonify({"mode": mode, "trained": bool(trained)})

if __name__ == "__main__":
    if use_embeddings and not EMB_FILE.exists():
        train_embeddings()
    elif (not use_embeddings) and (lbph_recognizer is not None):
        trainer_yml = TRAINER_DIR / "trainer.yml"
        if not trainer_yml.exists():
            train_embeddings()
    app.run(debug=True)
