# Project Documentation & Viva Voce Guide

## MCA Final Year Major Project Thesis Outline
**Title**: *An Explainable Machine Learning-Based Framework for Phishing Website Detection and Risk Analysis*  
**Author**: Chandra  
**Technology Stack**: Python (FastAPI), XGBoost, SHAP, React.js, SQLite/MySQL  

---

## 1. Executive Summary & Abstract
Phishing website detection is a critical defensive cybersecurity application. Traditional blacklists fail to detect zero-day phishing attacks. This project presents an explainable, multi-tier phishing detection framework that:
1. Extracts **30+ structural, lexical, domain, and content-based features** from untrusted URLs in real-time.
2. Trains and benchmarks **5 machine learning classifiers** (Logistic Regression, Decision Tree, Random Forest, Support Vector Machine, and XGBoost).
3. Computes a transparent **Risk Score (0–100)** categorizing threats into 5 severity tiers (*Very Low, Low, Medium, High, Critical*).
4. Employs **SHAP (SHapley Additive exPlanations)** to provide interpretable, human-readable explanations of every classification decision.

---

## 2. System Architecture Diagram

```
+-----------------------------------------------------------------------+
|                           REACT FRONTEND                              |
|   Landing | Login/Register | URL Scanner | Dashboard | History | Admin|
+----------------------------------- opacity ---------------------------+
                                    | (HTTPS / REST JSON)
                                    v
+-----------------------------------------------------------------------+
|                          FASTAPI BACKEND                              |
|   +-------------------+  +--------------------+  +----------------+   |
|   | Auth (JWT/Bcrypt) |  | Feature Extractor  |  | Risk Engine    |   |
|   +-------------------+  +--------------------+  +----------------+   |
|   +-------------------+  +--------------------+  +----------------+   |
|   | ML Model Loader   |  | SHAP Explainer     |  | Database ORM   |   |
|   +-------------------+  +--------------------+  +----------------+   |
+-----------------------------------------------------------------------+
            |                          |                     |
            v                          v                     v
   +-----------------+        +-----------------+    +---------------+
   | Trained Models  |        | SHAP Explainer  |    | SQLite/MySQL  |
   | (XGBoost .pkl)  |        | (.pkl)          |    | (Persistence) |
   +-----------------+        +-----------------+    +---------------+
```

---

## 3. Machine Learning Performance Benchmark

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **XGBoost** | **95.13%** | **95.04%** | **94.88%** | **94.96%** | **99.30%** | **Selected Active Model** |
| Random Forest | 94.53% | 93.43% | 95.41% | 94.41% | 99.11% | Secondary Benchmark |
| Support Vector Machine (SVM) | 94.02% | 92.47% | 95.41% | 93.91% | 98.27% | Baseline Classifier |
| Decision Tree | 93.59% | 94.72% | 91.87% | 93.27% | 97.15% | Interpretable Baseline |
| Logistic Regression | 91.28% | 90.00% | 92.23% | 91.10% | 97.38% | Linear Baseline |

---

## 4. Risk Engine Mathematical Formulation

$$\text{Risk Score} = 0.50 \cdot (P_{\text{phishing}} \times 100) + 0.25 \cdot R_{\text{URL}} + 0.15 \cdot R_{\text{Domain}} + 0.10 \cdot R_{\text{Content}}$$

Where:
* $P_{\text{phishing}}$: Probability output from XGBoost model ($0.0 \le P \le 1.0$)
* $R_{\text{URL}}$: Heuristic penalty score for URL structural anomalies (IP address, shortened URL, `@` symbol, excessive subdomains)
* $R_{\text{Domain}}$: Penalty score for domain signals (suspicious TLD, prefix-suffix hyphens)
* $R_{\text{Content}}$: Penalty score for DOM content signals (iFrames, email submit handlers, right-click disabled)

---

## 5. SHAP (Explainable AI) Formulation
For a prediction $f(x)$ on feature vector $x$:

$$f(x) = \phi_0 + \sum_{i=1}^{M} \phi_i$$

Where:
* $\phi_0$: Base value (expected model prediction over training set)
* $\phi_i$: Shapley value representing feature $i$'s marginal contribution to pushing the prediction toward Phishing ($\phi_i > 0$) or Legitimate ($\phi_i < 0$).

---

## 6. Top 10 MCA Viva Voce Questions & Answers

### Q1: Why did you choose XGBoost over Deep Learning for this project?
**Answer**: Phishing URL features extracted from tabular datasets consist of structured binary and numerical vectors. Tree-based ensemble models like XGBoost consistently outperform Deep Neural Networks on tabular data while requiring significantly less computation and offering native compatibility with SHAP TreeExplainer.

### Q2: What is the purpose of SHAP in your architecture?
**Answer**: Traditional ML models act as "black boxes", returning only a probability score. SHAP calculates exact Shapley values from cooperative game theory to quantify the exact contribution of each feature (e.g. IP address in URL added +0.28 to the phishing probability), providing transparent explanations required in security analysis.

### Q3: How do you handle zero-day phishing URLs that are not in blacklists?
**Answer**: Our system does not rely on static domain blacklists. Instead, it extracts structural features (e.g. presence of `@` symbol, IP hostnames, URL shorteners, domain length) and uses a trained XGBoost model to generalize and detect newly created phishing patterns.

### Q4: How is security handled in your API?
**Answer**: 
1. Passwords are hashed using **PBKDF2-HMAC-SHA256** with 100,000 iterations and random 16-byte salts.
2. API endpoints are secured using **JWT Bearer tokens** (HS256 algorithm) with expiration timeouts.
3. Database queries use SQLAlchemy ORM parameterized queries to prevent SQL Injection.
4. Input validation is strictly enforced with Pydantic v2 schemas.

### Q5: What is the role of Deep Scan in your feature extractor?
**Answer**: URL-only analysis extracts structural features without making network calls. When the user enables "Deep Scan", the system issues a safe `requests` HTTP GET request with a strict 10-second timeout to parse the webpage DOM for malicious content signals (e.g., hidden `<iframe>` tags, form submissions to `mailto:`, and disabled right-click handlers).

---

## 7. How to Run the Automated Test Suite

To verify the entire system code quality:
```bash
cd backend
python -m pytest tests/
```
Output:
`11 passed in 2.26s` (100% test pass rate).
