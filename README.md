```markdown
# 🔐 Web-Based Biometric Authentication System  
### Face Recognition + OTP Verification  

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey) ![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green) ![License](https://img.shields.io/badge/License-MIT-yellow)  

A secure, user-friendly **two-factor authentication (2FA) system** that combines **deep learning-based face recognition** with **time-based OTP verification** via email. Built for web deployment with real-time webcam access and modular architecture.

---

## 📖 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Workflow](#workflow)
- [Installation](#installation)
- [Usage](#usage)
- [Performance Metrics](#performance-metrics)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)
- [Citation](#citation)
- [License](#license)

---

## 🎯 Overview

Traditional password systems are vulnerable to phishing, reuse, and brute-force attacks. This project implements a **dual-factor authentication system** using:
- **Face Recognition** via OpenFace embeddings
- **OTP Verification** delivered via email

The system is built with **Flask** (backend), **OpenCV** (face processing), and a modern **JavaScript frontend**, ensuring accessibility through standard webcams.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📸 **Multi-Pose Face Capture** | Guided capture of 10 images (front, left, right) during sign-up |
| 🧠 **Deep Face Embeddings** | Uses OpenFace model for 128-D facial feature extraction |
| 🔐 **Cosine Similarity Matching** | Threshold-based face matching (≥0.60 similarity) |
| 📧 **Email OTP Verification** | 4-digit OTP sent via SMTP (Gmail), valid for 5 minutes |
| 🔄 **Auto-Retraining** | Model updates after each successful login/sign-up |
| 🎤 **Voice & Visual Guidance** | Interactive UI with real-time feedback |
| 📁 **File-Based Storage** | Organized user data, embeddings, and model files |

---

## 🏗️ System Architecture

### Three-Tier Design

```
Client Tier (Frontend) → Server Tier (Flask Backend) → Storage Tier (File System)
```

#### **Client Tier**
- HTML5/CSS3/JavaScript
- Real-time webcam via `getUserMedia()`
- Responsive & interactive UI

#### **Server Tier**
- Flask API endpoints
- OpenCV for face detection & embedding
- OTP generation & email dispatch
- Session management

#### **Storage Tier**
```
project/
├── users/           # Per-user folders (images, email)
├── trainer/         # Embeddings & labels
├── models/          # OpenFace model file
└── tmp_signup/      # Temporary registration data
```

---

## 🔄 Workflow

### 🆕 Sign-Up Process
1. User enters name & email
2. System guides to capture **10 facial poses**
3. Images preprocessed → embeddings generated
4. OTP sent to email
5. OTP verified → user registered

### 🔑 Login Process
1. User shows face via webcam
2. Face matched via cosine similarity
3. If match ≥ 0.60 → OTP sent to registered email
4. User enters OTP → access granted

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- Webcam
- Gmail account (for SMTP)

### Steps
```bash
# Clone repository
git clone https://github.com/username/face-otp-auth.git
cd face-otp-auth

# Install dependencies
pip install -r requirements.txt

# Download OpenFace model
wget https://github.com/cmusatyalab/openface/raw/master/models/openface/nn4.small2.v1.t7 -P models/

# Configure email credentials in config.py
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASS = "your-app-password"

# Run Flask app
python app.py
```

---

## 🚀 Usage

1. Open `http://localhost:5000` in browser
2. **Sign Up**: Follow on-screen prompts to capture face & verify OTP
3. **Log In**: Show face → receive OTP → enter to authenticate
4. Access secured dashboard upon success

---

## 📊 Performance Metrics

| Metric | Result |
|--------|--------|
| Face Recognition Accuracy | 90–95% |
| False Acceptance Rate (FAR) | < 2% |
| False Rejection Rate (FRR) | ~4% |
| OTP Delivery Success Rate | 99% |
| End-to-End Auth Success | ~94% |

---

## 📂 Project Structure

```
face-otp-auth/
├── app.py                      # Flask application
├── config.py                   # Configuration (email, paths)
├── requirements.txt            # Python dependencies
├── static/
│   ├── css/                   # Stylesheets
│   ├── js/                    # Frontend logic
│   └── images/                # UI assets
├── templates/                  # HTML templates
├── models/
│   └── nn4.small2.v1.t7       # OpenFace model
├── users/                      # User data
├── trainer/                    # Embeddings & labels
├── tmp_signup/                 # Temporary sign-up data
└── README.md                   # This file
```

---

## 🔮 Future Enhancements

- [ ] **Liveness Detection** – Blink/motion analysis to prevent spoofing
- [ ] **Database Integration** – Replace file storage with PostgreSQL/MongoDB
- [ ] **Advanced Models** – ArcFace or MobileFaceNet for better accuracy
- [ ] **Encrypted Embeddings** – Homomorphic encryption for privacy
- [ ] **Mobile App** – Cross-platform app (React Native/Flutter)
- [ ] **Cloud Deployment** – AWS/Azure with load balancing

---

## 👥 Contributors

| Name | Role |
|------|------|
| **Isfaq Evan Dipro** | Full-stack development, face recognition, OTP system |
| **Muhit Ibtisham** | Model training, paper writing, testing coordination |
| **K. A. T. Himantha** | Data collection, training preparation |
| **Hossain Seyam** | Research support, presentation materials |

---

## 📚 Citation

If you use this project in your research, please cite:

```bibtex
@article{face_otp_2025,
  title={Web-Based Biometric Authentication System Using Face Recognition and OTP Verification},
  author={Dipro, Isfaq Evan and Ibtisham, Muhit and Himantha, K.A.T. and Seyam, Hossain},
  year={2025},
  publisher={Brain Station Cyber Hub}
}
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🌐 Connect

For questions or collaborations, contact:  
📧 **Isfaq Evan Dipro** – evandipro2004@gmail.com  
🏢 **Brain Station Cyber Hub** – Department of Intelligence Computing  

---

**⭐ Star this repo if you found it useful!**  
**🔁 Fork and contribute to future enhancements.**
```
