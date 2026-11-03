import os

root_dir = r'C:\Users\user\.gemini\antigravity\scratch\phishing_detection_system'
dirs = [
    '',
    'backend',
    'backend/app',
    'backend/app/core',
    'backend/app/models',
    'backend/app/schemas',
    'backend/app/routes',
    'backend/app/services',
    'ml',
    'ml/saved_models',
    'ml/data',
    'ml/data/raw',
    'ml/data/processed',
    'ml/saved_models/plots',
    'frontend',
    'frontend/phishing-ui',
    'frontend/phishing-ui/src',
    'frontend/phishing-ui/src/components',
    'frontend/phishing-ui/src/pages',
    'frontend/phishing-ui/src/services',
    'frontend/phishing-ui/src/hooks',
]

for d in dirs:
    os.makedirs(os.path.join(root_dir, d), exist_ok=True)

files = {
    '.gitignore': '__pycache__\n*.pyc\nvenv/\n.env\n*.pkl\nml/data/raw/\nnode_modules/\n',
    'backend/.env.example': 'DB_HOST=localhost\nDB_PORT=3306\nDB_NAME=phishing_detection_db\nDB_USER=root\nDB_PASSWORD=\nSECRET_KEY=secret\n',
    'backend/app/core/config.py': 'from pydantic_settings import BaseSettings\nclass Settings(BaseSettings): pass\n',
    'backend/app/core/security.py': '# Security module\n',
    'backend/app/database.py': '# Database setup\n',
    'backend/app/models/user.py': '# User model\n',
    'backend/app/models/analysis.py': '# Analysis model\n',
    'backend/app/models/features.py': '# Features model\n',
    'backend/app/models/ml_model.py': '# ML model\n',
    'backend/app/schemas/user.py': '# User schemas\n',
    'backend/app/schemas/analysis.py': '# Analysis schemas\n',
    'backend/app/routes/auth.py': '# Auth router\n',
    'backend/app/routes/analysis.py': '# Analysis router\n',
    'backend/app/routes/dashboard.py': '# Dashboard router\n',
    'backend/app/routes/model.py': '# Model router\n',
    'backend/app/routes/admin.py': '# Admin router\n',
    'backend/app/services/feature_extractor.py': '# Feature extractor\n',
    'backend/app/services/risk_engine.py': '# Risk engine\n',
    'backend/app/services/prediction.py': '# Prediction service\n',
    'backend/app/services/explanation.py': '# Explanation service\n',
    'backend/app/main.py': '# Main FastAPI app\n',
    'backend/seed_admin.py': '# Seed admin\n',
    'backend/app/models/__init__.py': '',
    'backend/app/routes/__init__.py': '',
    'backend/app/schemas/__init__.py': '',
    'backend/app/services/__init__.py': '',
    'backend/app/core/__init__.py': '',
    'backend/app/__init__.py': '',
    'ml/__init__.py': '',
    'ml/saved_models/.gitkeep': '',
    'ml/data/raw/.gitkeep': '',
    'ml/data/processed/.gitkeep': '',
    'ml/preprocessing.py': '# Preprocessing\n',
    'ml/train_models.py': '# Train models\n',
    'ml/evaluate_models.py': '# Evaluate models\n',
    'ml/explain_model.py': '# Explain model\n',
    'frontend/phishing-ui/package.json': '{\"name\": \"phishing-ui\"}\n',
    'frontend/phishing-ui/vite.config.js': 'export default {}\n',
    'frontend/phishing-ui/index.html': '<html></html>\n',
    'frontend/phishing-ui/src/main.jsx': 'import React from \"react\"\n',
    'frontend/phishing-ui/src/index.css': '/* CSS */\n',
    'frontend/phishing-ui/src/App.jsx': 'export default function App() { return <div>App</div> }\n',
    'frontend/phishing-ui/src/services/api.js': 'export const api = {}\n',
    'frontend/phishing-ui/src/hooks/useAuth.js': 'export const useAuth = () => ({})\n',
    'frontend/phishing-ui/src/pages/Landing.jsx': 'export default function Landing() { return <div>Landing</div> }\n',
    'frontend/phishing-ui/src/pages/Login.jsx': 'export default function Login() { return <div>Login</div> }\n',
    'frontend/phishing-ui/src/pages/Register.jsx': 'export default function Register() { return <div>Register</div> }\n',
    'frontend/phishing-ui/src/pages/Analyze.jsx': 'export default function Analyze() { return <div>Analyze</div> }\n',
    'frontend/phishing-ui/src/pages/Result.jsx': 'export default function Result() { return <div>Result</div> }\n',
    'frontend/phishing-ui/src/pages/Dashboard.jsx': 'export default function Dashboard() { return <div>Dashboard</div> }\n',
    'frontend/phishing-ui/src/pages/History.jsx': 'export default function History() { return <div>History</div> }\n',
    'frontend/phishing-ui/src/pages/ModelPerformance.jsx': 'export default function ModelPerformance() { return <div>Model Performance</div> }\n',
    'frontend/phishing-ui/src/pages/Admin.jsx': 'export default function Admin() { return <div>Admin</div> }\n',
    'frontend/phishing-ui/src/components/Navbar.jsx': 'export default function Navbar() { return <nav>Navbar</nav> }\n',
    'frontend/phishing-ui/src/components/RiskMeter.jsx': 'export default function RiskMeter() { return <div>Meter</div> }\n',
    'frontend/phishing-ui/src/components/FeatureChart.jsx': 'export default function FeatureChart() { return <div>Chart</div> }\n'
}

for path, content in files.items():
    full_path = os.path.join(root_dir, path)
    if not os.path.exists(full_path):
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('All project skeleton files have been generated.')
