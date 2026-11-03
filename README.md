# Phishing Website Detection & Risk Analysis System
## MCA Final Year Project

> **An Explainable Machine Learning-Based Framework for Phishing Website Detection and Risk Analysis**

A full-stack cybersecurity web application that uses trained ML models to classify URLs as phishing or legitimate, generates a transparent risk score (0–100), and provides SHAP-based explainability.

---

## 🛡️ Project Overview

| Property | Detail |
|----------|--------|
| **Project Type** | MCA Final Year Major Project |
| **Domain** | Cybersecurity / Machine Learning |
| **Stack** | Python, FastAPI, React.js, MySQL, XGBoost, SHAP |
| **Backend Port** | 8000 |
| **Frontend Port** | 5173 |
| **API Docs** | http://localhost:8000/docs |

---

## 🏗️ Architecture

```
React.js Frontend (Vite)
        │
        │ REST API / JWT
        ▼
FastAPI Backend (Uvicorn)
        │
    ┌───┴────────────────┐
    │                    │
    ▼                    ▼
MySQL Database    ML Inference Engine
(SQLAlchemy)     ┌──────────────────┐
                 │ Feature Extractor│
                 │ Risk Engine      │
                 │ SHAP Explainer   │
                 └──────────────────┘
```

---

## 📦 Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Backend | FastAPI + Uvicorn |
| ML Core | Scikit-learn + XGBoost |
| Explainability | SHAP |
| Database | MySQL 8.x + SQLAlchemy |
| Frontend | React.js + Vite |
| Charts | Recharts |
| Auth | JWT + bcrypt |

---

## 📂 Project Structure

```
phishing_detection_system/
├── backend/
│   ├── app/
│   │   ├── core/         ← Config, Security
│   │   ├── models/       ← SQLAlchemy ORM
│   │   ├── schemas/      ← Pydantic schemas
│   │   ├── routes/       ← API endpoints
│   │   ├── services/     ← Business logic
│   │   ├── main.py       ← FastAPI entry point
│   │   └── database.py   ← DB session/engine
│   ├── seed_admin.py
│   ├── requirements.txt
│   └── .env.example
│
├── ml/
│   ├── data/raw/         ← Dataset (gitignored)
│   ├── data/processed/
│   ├── saved_models/     ← Trained .pkl files
│   ├── preprocessing.py
│   ├── train_models.py
│   ├── evaluate_models.py
│   └── explain_model.py
│
├── frontend/phishing-ui/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── services/
│       └── hooks/
│
└── README.md
```

---

## ⚙️ Prerequisites

| Software | Version | Download |
|----------|---------|---------|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| MySQL Server | 8.x | https://mysql.com |
| Git | Latest | https://git-scm.com |

---

## 🚀 Setup Instructions

### Step 1 — Create MySQL Database

Open MySQL Workbench or MySQL CLI and run:

```sql
CREATE DATABASE phishing_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2 — Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# IMPORTANT: Edit .env and fill in your MySQL password and secret key
```

### Step 3 — Configure Environment

Edit `backend/.env`:
```
DB_PASSWORD=your_actual_mysql_password
SECRET_KEY=generate-a-random-32-char-string-here
```

### Step 4 — Create Admin Account

```powershell
# Still inside backend/ with venv activated
python seed_admin.py
```

### Step 5 — Train ML Models

```powershell
# Navigate to ml/ folder
cd ..\ml

# Download UCI dataset first (instructions below)
# Then run training
python train_models.py
```

#### Dataset Download Instructions
1. Visit: https://archive.ics.uci.edu/dataset/327/phishing+websites
2. Download the dataset
3. Place the file in: `ml/data/raw/phishing_dataset.csv`

### Step 6 — Start Backend

```powershell
cd ..\backend

# With venv activated:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs (Swagger API documentation)

### Step 7 — Frontend Setup

```powershell
cd ..\frontend\phishing-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: http://localhost:5173

---

## 🔬 Research Questions

| ID | Question |
|----|---------|
| RQ1 | How effectively can ML algorithms distinguish phishing URLs from legitimate URLs? |
| RQ2 | Which URL/domain characteristics contribute most to phishing detection? |
| RQ3 | Does combining multiple feature categories improve detection performance? |
| RQ4 | Can SHAP provide understandable interpretations of phishing predictions? |
| RQ5 | Can risk scoring provide more informative results than binary classification? |

---

## 🔐 API Documentation

Full interactive API docs available at: **http://localhost:8000/docs**

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login, returns JWT |
| POST | /analysis/predict | Analyze a URL |
| GET | /analysis/history | User's analysis history |
| GET | /dashboard/statistics | Dashboard stats |
| GET | /model/performance | ML model metrics |

---

## 📊 ML Models Compared

| Model | Notes |
|-------|-------|
| Logistic Regression | Linear baseline |
| Decision Tree | Interpretable |
| Random Forest | Ensemble |
| SVM | Traditional ML |
| XGBoost | Primary model (SHAP-compatible) |

---

## ⚠️ Safety Notice

This is a **defensive** cybersecurity tool. It detects phishing — it does not create phishing sites.
All URLs submitted are treated as untrusted input. Deep scan (optional) uses safe read-only HTTP fetching with timeout controls.

---

## 📄 License

MIT License — For academic/educational use.

---

*MCA Final Year Project | Department of Computer Applications*
