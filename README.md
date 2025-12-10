# FaceSignIn  
### Web-Based Biometric Authentication System Using Face Recognition & OTP Verification

A secure, research-backed authentication system combining **deep-learning face recognition** with **email-based One-Time Password (OTP)** to offer multi-factor authentication (MFA) directly through a web browser.

Developed by **Isfaq Evan Dipro**, **Muhit Ibtisham**, **K. A. T. Himantha**  
Affiliation: **Brain Station Cyber Hub — Department of Intelligence Computing**

---

# 📌 Overview

FaceSignIn integrates:
- **Face Recognition** using 128-D OpenFace embeddings  
- **OTP Verification** via secure email  
- Real-time browser-based webcam interface  
- Multi-pose capture for higher accuracy  
- Automatic embedding retraining after registration  

The system is lightweight, scalable, and suitable for academic and small-organization deployments.

---

# 🧠 System Architecture

```
+---------------------+       +------------------------+       +---------------------------+
|    Client Side      | <-->  |     Flask Backend      | <-->  |       Storage Layer       |
| (HTML, JS, Webcam)  |       | (Face Rec + OTP APIs)  |       | (Users, Models, Embeds)   |
+---------------------+       +------------------------+       +---------------------------+

1. Capture face
2. Generate embeddings
3. Compare with stored profiles
4. If match → send OTP
5. Verify OTP → grant access
```

Directory structure:
```
project/
├── users/         # Per-user data
├── trainer/       # Embeddings and label files
├── models/        # OpenFace deep model
└── tmp_signup/    # Temporary sign-up frames
```

---

# 🔄 Workflow

## 🆕 Sign-Up Process
1. User enters **name & email**
2. System guides the user through capturing **10 facial poses**  
   - 4 frontal  
   - 3 left profile  
   - 3 right profile  
3. Images → preprocessing → **128-D embeddings**
4. System sends a **4-digit OTP** to the provided email
5. OTP verified → user stored → model retrained

## 🔑 Login Process
1. User shows face via webcam
2. Embedding generated & matched via **cosine similarity**
3. If similarity **≥ 0.60**, OTP sent to registered email
4. User enters OTP → access granted

---

# 🧬 Technical Methodology

### Face Detection
- OpenCV Haar Cascade  
- Histogram equalization for lighting conditions

### Preprocessing
- Crop with margin  
- Grayscale  
- Resize to **96×96**

### Embedding Extraction
- Model: `nn4.small2.v1.t7` (OpenFace)  
- Output: **128-dimensional vector**

### Similarity Matching
```
similarity = (A · B) / (||A|| ||B||)
```

### OTP System
- 4-digit random OTP  
- Sent using Gmail SMTP (TLS)  
- Valid for **5 minutes**

### Model Retraining
- Runs after every successful sign-up or login  
- Keeps user embeddings updated for accuracy

---

# 📊 Results & Evaluation

| Metric | Result |
|--------|--------|
| Face Recognition Accuracy | 90–95% |
| False Acceptance Rate (FAR) | < 2% |
| False Rejection Rate (FRR) | ~4% |
| OTP Delivery Success | 99% |
| End-to-End Success | ~94% |

**Testing conditions:**
- Lighting: bright, indoor, dim  
- Devices: laptop webcam (720p), USB webcam (1080p)  
- Users tested: 20 over 3 sessions  

---

# ⚙️ Installation

## Prerequisites
- Python **3.8+**
- Webcam
- Gmail account (for SMTP OTP)

## Steps
```bash
# Clone repository
git clone https://github.com/brainstationcyberhub-coder/facesignin.git
cd facesignin

# Install dependencies
pip install -r requirements.txt

# Download OpenFace model
wget https://github.com/cmusatyalab/openface/raw/master/models/openface/nn4.small2.v1.t7 -P models/

# Configure your email credentials in config.py
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-app-password"

# Run Flask app
python app.py
```

---

# 🔒 Security Features
- OTP expires in 5 minutes  
- TLS-secured email transport  
- No raw images stored (embeddings only)  
- Flask session security  
- Cosine similarity threshold-based matching  

---

# 🧱 Limitations
- No liveness detection  
- Local storage (not ideal for large deployments)  
- Lighting conditions affect accuracy  
- Embedding encryption not implemented  

---

# 🔮 Future Improvements
- Add **liveness detection** (blink test, motion prompts)  
- Migrate to **ArcFace/MobileFaceNet**  
- Move to SQL/NoSQL database  
- Implement encrypted embedding storage  
- Cloud deployment (AWS/Azure)  
- Mobile app development  

---

# 👨‍💻 Authors & Contributions

| Author | Contribution |
|--------|-------------|
| **Isfaq Evan Dipro** | Full development, face recognition, OTP, frontend/backend, documentation |
| **Muhit Ibtisham** | Model optimization, research writing, testing, presentation |
| **K. A. T. Himantha** | Dataset support, pre-processing, documentation assistance |
| **Hossain Seyam** | Supporting data collection and presentation |

---

# 📚 References
- Schroff et al., *FaceNet: A Unified Embedding for Face Recognition*  
- Viola & Jones, *Real-Time Object Detection*  
- Jain et al., *Biometric Recognition*  
- NIST SP 800-63-3  
- Amos et al., *OpenFace Technical Report*  

