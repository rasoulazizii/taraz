// web/src/App.jsx
import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  // New State for recent events notification
  const [events, setEvents] = useState([]);

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    fetchInitialState();
  }, []);

  const fetchInitialState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);
      if (!response.ok) throw new Error("خطا در دریافت اطلاعات");
      const data = await response.json();
      
      setGameState(data);
      setInterestRate(data.effective_rate);
      setHistory([data]);
      setEvents(data.events || []);
      
    } catch (err) {
      setError("عدم اتصال به سرور بازی.");
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

      if (!response.ok) throw new Error("خطا در پردازش نوبت");
      
      const newData = await response.json();
      setGameState(newData);
      setHistory(prev => [...prev, newData]);
      setEvents(newData.events || []); // Update events list

    } catch (err) {
      setError("خطا در اعمال سیاست پولی.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!gameState) return <div className="loading">در حال اتصال به سامانه تراز...</div>;

  return (
    <div className="app-wrapper" dir="rtl">
      <div className="container">
        <header>
          <h1>شبیه‌ساز اقتصاد کلان: تراز</h1>
          <div className="status-badge">
             ماه جاری: <strong>{gameState.turn}</strong>
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        {/* Event Notifications Area */}
        {events.length > 0 && (
          <div className="events-container">
            {events.map((evt, index) => (
              <div key={index} className={`event-card ${evt.type}`}>
                <h4>⚠️ {evt.title}</h4>
                <p>{evt.desc}</p>
                <div className="event-impact">
                    {evt.impact.inflation && <span>تورم: {evt.impact.inflation > 0 ? '+' : ''}{evt.impact.inflation}% </span>}
                    {evt.impact.gdp && <span>تولید: {evt.impact.gdp > 0 ? '+' : ''}{evt.impact.gdp}% </span>}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="dashboard-grid">
          <div className="card">
            <h3>نرخ تورم</h3>
            <div className="value red">{gameState.inflation}%</div>
          </div>
          
          <div className="card">
            <h3>رشد تولید (GDP)</h3>
            <div className="value green">{gameState.gdp_growth}%</div>
          </div>
          
          <div className="card">
            <h3>نرخ بیکاری</h3>
            <div className="value orange">{gameState.unemployment}%</div>
          </div>

          <div className="card info">
            <h3>نرخ بهره بازار (مؤثر)</h3>
            <div className="value small">{gameState.effective_rate}%</div>
            <span className="hint">با تأخیر ۳ ماهه</span>
          </div>
        </div>

        <div className="chart-container" dir="ltr"> 
          <h3>روند شاخص‌های کلان</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="turn" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ backgroundColor: '#333', border: '1px solid #555' }} />
              <Legend />
              <Line type="monotone" dataKey="inflation" name="تورم" stroke="#ff6b6b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="gdp_growth" name="رشد GDP" stroke="#51cf66" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="unemployment" name="بیکاری" stroke="#fcc419" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="controls-area">
          <label>
            تنظیم نرخ بهره سیاستی: <strong>{interestRate}%</strong>
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
          <div className="slider-labels">
            <span>سیاست انبساطی</span>
            <span>سیاست انقباضی</span>
          </div>
          <button onClick={handleNextTurn} disabled={loading} className="action-btn">
            {loading ? "در حال محاسبه..." : "اعمال سیاست و رفتن به ماه بعد"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;