## System Overview
FaceSignIn is a web-based biometric authentication system that combines deep learning face recognition with email-based OTP verification for two-factor authentication (2FA). The system was developed by researchers at Brain Station Cyber Hub, Department of Intelligence Computing.

## Core Architecture

### Three-Tier System Architecture:
1. **Client Tier**: HTML5/CSS3/JavaScript interface with real-time webcam access via getUserMedia() API
2. **Server Tier**: Python Flask application handling face detection, embedding computation, similarity matching, OTP generation, and session management
3. **Storage Tier**: File-based storage system with structured directory hierarchy

### Directory Structure:
- `users/` - Per-user folders with images and email data
- `trainer/` - Embeddings and labels
- `models/` - OpenFace model file (nn4.small2.v1.t7)
- `tmp_signup/` - Temporary sign-up data

## Technical Methodology

### Face Detection:
- Uses OpenCV's Haar Cascade Classifier for real-time face detection
- Implements adaptive histogram equalization for varying lighting conditions
- Detects largest face in each frame with scaleFactor=1.1, minNeighbors=4

### Preprocessing:
- Detected faces cropped with 20% margin
- Converted to grayscale and resized to 96×96 pixels
- Uses `cv2.equalizeHist()` for contrast enhancement

### Embedding Extraction:
- Employs OpenFace model (nn4.small2.v1.t7) loaded via OpenCV's DNN module
- Generates 128-dimensional normalized vectors as face "fingerprints"
- Converts images to embeddings using `face_to_embedding()` function

### Similarity Matching:
- Uses cosine similarity: `similarity = (A·B)/(||A|| ||B||)`
- Match threshold: ≥ 0.60
- Backup: LBPH (Local Binary Patterns Histograms) if OpenFace unavailable

### OTP System:
- 4-digit OTP generated randomly
- Valid for 5 minutes
- Sent via Gmail SMTP with TLS encryption
- OTP verification required for both signup and login

## Workflow Processes

### Sign-Up Process:
1. User provides name and email
2. System guides capture of 10 facial images:
   - 4 frontal images (neutral expression)
   - 3 left profile images (~30-45 degrees)
   - 3 right profile images (~30-45 degrees)
3. Images preprocessed and embeddings generated
4. OTP sent to provided email
5. OTP verified within 5 minutes
6. User data stored and model retrained

### Login Process:
1. User presents face via webcam
2. System computes embedding and compares with stored profiles
3. If similarity ≥ 0.60, OTP sent to registered email
4. User enters OTP to complete authentication
5. Successful login triggers automatic retraining

## Model Training & Retraining
- Automatic retraining after each successful sign-up or login
- Training files: `embeddings.npz` (matrix X) and `labels.json` (matrix Y)
- Uses matrix multiplication for identification: `sims = (X @ q)` where q is query vector
- System adapts to user appearance changes over time

## Performance Metrics
- Face Recognition Accuracy: 90-95%
- False Acceptance Rate (FAR): < 2%
- False Rejection Rate (FRR): ~4%
- OTP Delivery Success Rate: 99%
- End-to-End Authentication Success: ~94%

## Security Features
- Two-factor authentication (face + OTP)
- Session management using Flask sessions
- No raw image storage - only embeddings and processed faces
- Secure email communication via TLS
- OTP expiration after 5 minutes

## Limitations
- Lack of liveness detection (vulnerable to photo spoofing)
- Local file storage limits scalability
- Performance depends on lighting and camera quality
- No encryption for stored facial data

## Future Improvements
- Integrate blink detection or challenge-response for liveness detection
- Replace file-based storage with SQL/NoSQL databases
- Migrate to ArcFace or MobileFaceNet for improved accuracy
- Implement homomorphic encryption for secure embedding storage
- Develop cross-platform mobile application
- Cloud deployment on AWS/Azure with load balancing

## Author Contributions
- **Isfaq Evan Dipro**: Full codebase development, face recognition and OTP implementation, front-end/back-end architecture
- **Muhit Ibtisham**: Model training and optimization, research paper writing, project coordination and testing
- **K. A. T. Himantha**: Research data collection and organization, training data preparation
- **Hossain Seyam**: Research data collection support, presentation materials

The system demonstrates a secure, web-based authentication solution combining face recognition with OTP verification, suitable for academic and small-scale organizational deployments.
