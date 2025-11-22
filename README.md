🏛️ Taraz: The Macro-Economic Simulator
The Governor's Dilemma — A hardcore economic strategy game where you control the Central Bank, fight inflation, manage the currency, and survive the political pressure.
![alt text](https://img.shields.io/badge/Status-MVP_Complete-green)

![alt text](https://img.shields.io/badge/License-MIT-blue)

![alt text](https://img.shields.io/badge/Language-Persian_(UI)-orange)
🤖 AI-Assisted Development
This project is a testament to Human-AI Collaboration.
This entire software, including the mathematical economic core (DSGE-inspired engine), the FastAPI backend, the React frontend, and the game design logic, was conceptualized and developed through an intensive dialogue between a Human Architect and an AI Model.
Concept & Constraints: Human Direction.
Code Generation & Math Modeling: Artificial Intelligence.
Balancing & Testing: Collaborative Iteration.
📖 Overview
Taraz (Persian for "Balance") is a web-based simulation game that puts you in the chair of the Central Bank Governor. Unlike simple clicker games, Taraz runs on a complex mathematical engine simulating real-world economic relationships (Phillips Curve, Okun's Law, Interest Rate Parity).
Your goal is simple yet difficult: Survive 48 months (4 years) without crashing the economy or getting fired by the government.
Key Features
🧮 Realistic Economic Engine:
Inflation vs. Unemployment: Manage the trade-off.
GDP Growth: Stimulate production or cool down overheating.
Exchange Rate (FX): Watch the currency devalue if you print too much money.
⚙️ Dual Policy Levers:
Interest Rate: Control the cost of borrowing.
Money Supply (QE/QT): Print money to fight recession or sell bonds to curb inflation.
🏛️ Dynamic Political AI:
Face 4 distinct government archetypes: Populist, Austerity, Liberal, and Welfare.
Each government reacts differently to your policies. Keep political tension low, or face dismissal!
🔮 Ghost Chart Projections:
Real-time forecasting system that predicts the future impact of your decisions before you commit to them.
🧠 The Council of Advisors:
Receive conflicting advice from the Hawk (Anti-Inflation), the Dove (Pro-Employment), and the Technocrat (Stability).
⚡ Dynamic Events:
Handle random shocks like Oil Crisis, Tech Booms, and Labor Strikes.
🛠️ Tech Stack
Backend (The Brain):
Python 3.x
FastAPI: High-performance API framework.
NumPy-style Logic: Custom economic simulation classes.
Frontend (The Face):
React.js (Vite)
Recharts: For real-time data visualization.
CSS Modules: Custom dark-mode, RTL (Right-to-Left) design for Persian support.
🚀 Installation & Setup
To run Taraz locally, you need to start both the Backend (Python) and the Frontend (Node.js).
Prerequisites
Python 3.8+
Node.js & npm
1. Setup Backend (Python)
code
Bash
# Navigate to root directory
cd taraz

# Install dependencies
pip install -r requirements.txt

# Start the API Server
uvicorn api:app --reload
The backend will start at http://127.0.0.1:8000
2. Setup Frontend (React)
Open a new terminal window:
code
Bash
# Navigate to web directory
cd taraz/web

# Install dependencies
npm install

# Start the Development Server
npm run dev
The frontend will start at http://localhost:5173 (or similar).
🎮 How to Play
Open your browser and go to the local frontend URL.
Analyze the Dashboard: Look at Inflation, GDP, Unemployment, and the Exchange Rate.
Listen to Advisors: Check the bottom panel to see what the Hawk or Dove suggests.
Adjust Controls:
Interest Rate: Increase to lower inflation (but hurt growth). Decrease to boost growth (but risk inflation).
Money Printer: Positive (+) to inject cash (QE). Negative (-) to absorb cash (QT).
Watch the Ghost Lines: The dashed lines on the chart show you the predicted future.
Execute: Click "Next Month".
Survive: Keep the Political Tension bar low. If it hits 100%, you are fired. If Inflation hits 100%, the economy collapses.
📂 Project Structure
code
Text
taraz/
├── api.py              # FastAPI entry point & endpoints
├── engine.py           # Core economic logic, AI, and Math
├── requirements.txt    # Python dependencies
├── tests/              # Unit tests for balancing and logic
│   ├── test_balancing.py
│   └── test_simulation.py
└── web/                # React Frontend
    ├── src/
    │   ├── App.jsx     # Main UI Logic
    │   ├── App.css     # Styling & Dark Theme
    │   └── main.jsx    # React Entry
    └── package.json    # JS dependencies
🧪 Testing & Balancing
The game engine includes a comprehensive testing suite to ensure the economy behaves realistically (e.g., creating a recession when interest rates are 40%).
Run the balance tests:
code
Bash
python -m unittest tests/test_balancing.py
🤝 Contributing
Since this project is an educational experiment in AI-assisted engineering, feel free to fork it and experiment!
Fork the Project.
Create your Feature Branch (git checkout -b feature/AmazingFeature).
Commit your Changes (git commit -m 'Add some AmazingFeature').
Push to the Branch (git push origin feature/AmazingFeature).
Open a Pull Request.
📄 License
Distributed under the MIT License. See LICENSE for more information.