# 🩺 A Data-Driven Machine Learning Model for Early Diagnosis of Chronic Kidney Disease

> **Final Year AI/ML Project** — Research-grade early CKD detection system with explainable AI, probability-based risk scoring, and clinical stage estimation.

---

## 🎯 Project Overview

This project goes beyond simple CKD classification. It is a **clinical decision-support system** that:

| Basic CKD Model | This System |
|---|---|
| Predicts CKD — Yes / No | Outputs probability-based risk score (0–100%) |
| Binary classifier only | Categorises risk: Low / Moderate / High |
| No staging | Estimates CKD Stage 1–5 |
| Black-box prediction | Explainable AI via SHAP values |
| No clinical guidance | Generates personalised medical recommendations |
| No prevention focus | Designed for **early detection and prevention** |

---

## 🏗️ Architecture

```
CKD_Early_Diagnosis/
│
├── data/
│   └── ckd_dataset_with_id.csv       ← UCI CKD dataset (400 patients, 25 features)
│
├── src/
│   ├── preprocessing.py               ← Data loading, imputation, encoding, scaling
│   ├── eda.py                         ← EDA plots (distributions, heatmap, feature importance)
│   ├── train.py                       ← Model training, tuning, evaluation, saving
│   └── inference.py                   ← Prediction engine + SHAP explanations
│
├── models/
│   └── ckd_artefacts.pkl              ← Saved models, scaler, encoders (generated)
│
├── notebooks/
│   └── eda_plots/                     ← Saved EDA visualisations (generated)
│
├── app.py                             ← Streamlit web application
├── requirements.txt
└── README.md
```

---

## 🤖 Models Trained & Compared

| Model | Description |
|---|---|
| Logistic Regression | Baseline linear classifier with L2 regularisation |
| Random Forest | Ensemble of decision trees with feature importance |
| XGBoost | Gradient boosting — typically highest performance |
| SVM (RBF Kernel) | Support Vector Machine with probabilistic output |

### Hyperparameter Tuning
GridSearchCV with **Stratified 5-Fold Cross-Validation**, optimising for **Recall** (critical in medical diagnosis).

---

## 📊 Evaluation Metrics

| Metric | Why It Matters |
|---|---|
| Accuracy | Overall correctness |
| Precision | How many predicted CKD cases are truly CKD |
| **Recall** ⭐ | **Most important** — how many true CKD cases are caught |
| F1 Score | Harmonic mean of Precision and Recall |
| ROC-AUC | Discrimination ability across all thresholds |

> **Why Recall?** In CKD detection, a *false negative* (missing a CKD patient) is far more dangerous than a false positive. A missed case means no treatment until irreversible damage occurs.

---

## 🔬 Early Diagnosis Logic

```
Patient Data → ML Model → Probability Score (e.g., 72%)
                                ↓
                    ┌─────────────────────┐
                    │   Risk Categoriser  │
                    │  0–30%  → Low       │
                    │  30–60% → Moderate  │
                    │  60–100%→ High      │
                    └─────────────────────┘
                                ↓
                    CKD Stage Estimator (1–5)
                                ↓
                    SHAP Feature Explanation
                                ↓
                    Clinical Recommendation
```

---

## 🧠 Explainable AI (SHAP)

SHAP (SHapley Additive exPlanations) decomposes each prediction into feature contributions:

- **Red bars** → features increasing CKD risk
- **Blue bars** → features decreasing CKD risk
- Human-readable explanation: _"High Serum Creatinine and Low Hemoglobin significantly increased CKD risk."_

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/CKD_Early_Diagnosis.git
cd CKD_Early_Diagnosis

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

### Step 1 — Generate EDA Plots
```bash
python src/eda.py
```

### Step 2 — Train Models
```bash
python src/train.py
```
This trains all 4 models, runs GridSearchCV, evaluates on test set, and saves `models/ckd_artefacts.pkl`.

### Step 3 — Launch the Web App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📱 Web Application Features

- **Patient Input Form** — all 24 clinical parameters
- **Risk Gauge** — animated probability dial (0–100%)
- **Risk Category** — colour-coded Low / Moderate / High card
- **CKD Stage** — Stage 1–5 estimation with clinical description
- **SHAP Feature Bar Chart** — top contributing factors
- **AI Explanation Text** — human-readable summary
- **Clinical Recommendation** — personalised medical advice
- **Model Selection Dropdown** — switch between 4 trained models
- **Model Comparison Dashboard** — side-by-side metric comparison
- **EDA Viewer** — browse all exploratory analysis plots

---

## 📚 Dataset

UCI Machine Learning Repository — Chronic Kidney Disease dataset  
400 patients × 25 features (11 numerical, 14 categorical)  
Target: CKD (250) vs Not CKD (150)

Key features: Age, Blood Pressure, Specific Gravity, Albumin, Blood Glucose, Blood Urea, Serum Creatinine, Sodium, Potassium, Hemoglobin, Packed Cell Volume, WBC Count, RBC Count, Hypertension, Diabetes Mellitus, Anemia, Appetite, Pedal Edema, Coronary Artery Disease.

---

## 👨‍💻 Author

Final Year B.Tech / M.Tech AI/ML Project  
Department of Computer Science / Artificial Intelligence  
Academic Year 2024–25

---

## 📄 License

This project is for academic and research purposes.
