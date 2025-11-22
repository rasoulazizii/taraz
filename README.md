# 🏛️ Taraz: The Macro-Economic Simulator

### The Governor's Dilemma
**A hardcore economic strategy game where you control the Central Bank, fight inflation, manage the currency, and survive political pressure.**

---

## 🤖 AI-Assisted Development
This project is a testament to **Human-AI Collaboration**. This entire software, including the mathematical economic core (DSGE-inspired engine), the FastAPI backend, the React frontend, and the game design logic, was conceptualized and developed through an intensive dialogue between a Human Architect and an AI Model.

*   **Concept & Constraints:** Human Direction.
*   **Code Generation & Math Modeling:** Artificial Intelligence.
*   **Balancing & Testing:** Collaborative Iteration.

---

## 📖 Overview
**Taraz** (Persian for "Balance") is a web-based simulation game that puts you in the chair of the Central Bank Governor. Unlike simple clicker games, Taraz runs on a complex mathematical engine simulating real-world economic relationships (Phillips Curve, Okun's Law, Interest Rate Parity).

Your goal is simple yet difficult: **Survive 48 months (4 years) without crashing the economy or getting fired by the government.**

---

## Key Features

### 🧮 Realistic Economic Engine
*   **Inflation vs. Unemployment:** Manage the trade-off.
*   **GDP Growth:** Stimulate production or cool down overheating.
*   **Exchange Rate (FX):** Watch the currency devalue if you print too much money.

### ⚙️ Dual Policy Levers
*   **Interest Rate:** Control the cost of borrowing.
*   **Money Supply (QE/QT):** Print money to fight recession or sell bonds to curb inflation.

### 🏛️ Dynamic Political AI
Face 4 distinct government archetypes: **Populist, Austerity, Liberal, and Welfare**. Each government reacts differently to your policies. Keep political tension low, or face dismissal!

### 🔮 Ghost Chart Projections
Real-time forecasting system that predicts the future impact of your decisions before you commit to them.

### 🧠 The Council of Advisors
Receive conflicting advice from the **Hawk** (Anti-Inflation), the **Dove** (Pro-Employment), and the **Technocrat** (Stability).

### ⚡ Dynamic Events
Handle random shocks like Oil Crises, Tech Booms, and Labor Strikes.

---

## 🛠️ Tech Stack

**Backend (The Brain):**
*   **Python 3.x**
*   **FastAPI:** High-performance API framework.
*   **NumPy-style Logic:** Custom economic simulation classes.

**Frontend (The Face):**
*   **React.js (Vite)**
*   **Recharts:** For real-time data visualization.
*   **CSS Modules:** Custom dark-mode, RTL (Right-to-Left) design for Persian support.

---

## 🚀 Installation & Setup

To run Taraz locally, you need to start both the Backend (Python) and the Frontend (Node.js).

**Prerequisites:** Python 3.8+ and Node.js & npm.

### 1. Setup Backend (Python)

```bash
# Navigate to root directory
cd taraz

# Install dependencies
pip install -r requirements.txt

# Start the API Server
uvicorn api:app --reload
