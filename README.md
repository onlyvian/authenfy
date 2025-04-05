# 🔍 Authenfy

**Authenfy** is an AI-powered system that detects deepfakes in video content and verifies authenticity using blockchain technology. It ensures tamper-proof validation by storing video fingerprints on-chain, empowering users to **trust what they see**.

---

## 🚀 Key Features

- 🧠 **Deepfake Detection** using pretrained AI models (EfficientNet/Xception)
- 🔗 **Blockchain-Backed Verification** via Ethereum smart contracts
- 🧾 **Immutable Video Hashing** using SHA-256
- 🔍 **Visual Explainability** with Grad-CAM (highlight fake regions)
- ⚡ **Fast Flask API** for analyze/verify endpoints
- 💻 **Clean React Frontend** with real-time results

---

## 🏗️ System Architecture

```plaintext
[User Interface: React + Tailwind]
         ↓
[Flask Backend API]
  • /analyze → Run deepfake model + hash video
  • /verify  → Check authenticity on blockchain
[AI Module]
  • Deepfake detection model (EfficientNet/Xception)
  • Grad-CAM visualization
[Blockchain]
  • Solidity Smart Contract
  • Stores hash + timestamp + verdict
