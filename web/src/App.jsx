// web/src/App.jsx
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State variables for the game
  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // API Configuration
  const API_URL = "http://127.0.0.1:8000";

  // Fetch initial state on load
  useEffect(() => {
    fetchState();
  }, []);

  const fetchState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);
      if (!response.ok) throw new Error("Failed to fetch state");
      const data = await response.json();
      setGameState(data);
      // Set the slider to the current effective rate initially
      if (data.effective_rate) setInterestRate(data.effective_rate);
    } catch (err) {
      setError("Error connecting to Game Engine. Is backend running?");
      console.error(err);
    }
  };

  const handleNextTurn = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/next_turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interest_rate: parseFloat(interestRate) }),
      });

      if (!response.ok) throw new Error("Failed to process turn");
      
      const newData = await response.json();
      setGameState(newData);
    } catch (err) {
      setError("Failed to execute policy.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!gameState) return <div className="loading">Connecting to Taraz Engine...</div>;

  return (
    <div className="container">
      <header>
        <h1>TARAZ Simulator (Wireframe)</h1>
        <div className="status-badge">
           Turn: <strong>{gameState.turn}</strong>
        </div>
      </header>

      {error && <div className="error-box">{error}</div>}

      <div className="dashboard-grid">
        {/* Indicator Cards */}
        <div className="card">
          <h3>Inflation</h3>
          <div className="value">{gameState.inflation}%</div>
        </div>
        
        <div className="card">
          <h3>GDP Growth</h3>
          <div className="value">{gameState.gdp_growth}%</div>
        </div>
        
        <div className="card">
          <h3>Unemployment</h3>
          <div className="value">{gameState.unemployment}%</div>
        </div>

        <div className="card info">
          <h3>Effective Rate</h3>
          <div className="value small">{gameState.effective_rate}%</div>
        </div>
      </div>

      <div className="controls-area">
        <label>
          Set Policy Interest Rate: <strong>{interestRate}%</strong>
        </label>
        
        <input 
          type="range" 
          min="-5" 
          max="50" 
          step="0.5"
          value={interestRate}
          onChange={(e) => setInterestRate(e.target.value)}
          className="slider"
        />
        
        <button 
          onClick={handleNextTurn} 
          disabled={loading}
          className="action-btn"
        >
          {loading ? "Processing..." : "Execute Policy (Next Month)"}
        </button>
      </div>
    </div>
  );
}

export default App;