import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  // --- State Management ---
  const [gameState, setGameState] = useState(null);
  
  // Inputs
  const [interestRate, setInterestRate] = useState(15.0);
  const [moneyPrinter, setMoneyPrinter] = useState(0.0); // New: -20 to +20
  
  // UX States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Data for Visualization
  const [history, setHistory] = useState([]);
  const [eventLog, setEventLog] = useState([]); // Persistent News Feed

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    fetchInitialState();
  }, []);

  // --- API Interactions ---

  const fetchInitialState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);
      if (!response.ok) throw new Error("خطا در دریافت اطلاعات");
      const data = await response.json();
      
      setGameState(data);
      setInterestRate(data.effective_rate);
      
      // Initialize History
      setHistory([data]);
      
      // Initialize Events if any
      if (data.events && data.events.length > 0) {
          addEventsToLog(data.events, data.turn);
      }
      
    } catch (err) {
      setError("عدم اتصال به سرور بازی. آیا فایل api.py اجرا شده است؟");
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
        body: JSON.stringify({ 
            interest_rate: parseFloat(interestRate),
            money_printer: parseFloat(moneyPrinter)
        }),
      });

      if (!response.ok) throw new Error("خطا در پردازش نوبت");
      
      const newData = await response.json();
      setGameState(newData);
      
      // Update Charts
      setHistory(prev => [...prev, newData]);
      
      // Update News Feed
      addEventsToLog(newData.events, newData.turn);

    } catch (err) {
      setError("خطا در اعمال سیاست پولی.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // --- Helpers ---

  const addEventsToLog = (newEvents, turn) => {
      if (!newEvents || newEvents.length === 0) return;
      const taggedEvents = newEvents.map(evt => ({ ...evt, turn }));
      setEventLog(prevLog => [...taggedEvents, ...prevLog]); // Newest first
  };

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('fa-IR').format(val);
  };

  const getTensionColor = (val) => {
    if (val < 30) return '#51cf66'; // Green
    if (val < 70) return '#fcc419'; // Yellow
    return '#ff6b6b'; // Red
  };

  // --- Render ---

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

        {/* 1. Political Tension Section */}
        <div className="tension-container">
            <div className="tension-header">
                <span>تنش سیاسی با دولت</span>
                <strong style={{color: getTensionColor(gameState.political_tension)}}>
                    {gameState.political_tension}%
                </strong>
            </div>
            <div className="progress-bar-bg">
                <div 
                    className="progress-bar-fill"
                    style={{ 
                        width: `${gameState.political_tension}%`,
                        backgroundColor: getTensionColor(gameState.political_tension)
                    }}
                ></div>
            </div>
            <div className="gov-message">
                💬 {gameState.gov_message}
            </div>
        </div>

        {/* 2. News Feed */}
        {eventLog.length > 0 && (
          <div className="news-feed">
            <h3>🗞 اخبار و رویدادها</h3>
            <div className="news-list">
              {eventLog.map((evt, index) => (
                <div key={index} className={`news-item ${evt.type}`}>
                  <div className="news-turn">ماه {evt.turn}</div>
                  <div className="news-content">
                    <h4>{evt.title}</h4>
                    <p>{evt.desc}</p>
                    <div className="news-impact">
                        {evt.impact.inflation && <span>تورم: {evt.impact.inflation > 0 ? '+' : ''}{evt.impact.inflation}% </span>}
                        {evt.impact.gdp && <span>تولید: {evt.impact.gdp > 0 ? '+' : ''}{evt.impact.gdp}% </span>}
                        {evt.impact.unemployment && <span>بیکاری: {evt.impact.unemployment > 0 ? '+' : ''}{evt.impact.unemployment}% </span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. Main Dashboard */}
        <div className="dashboard-grid">
          {/* FX Card */}
          <div className="card">
            <h3>نرخ ارز (تومان)</h3>
            <div className="value gold">{formatCurrency(gameState.exchange_rate)}</div>
            <span className="hint" style={{color: gameState.fx_change > 0 ? '#ff6b6b' : '#51cf66'}}>
                {gameState.fx_change > 0 ? '▲' : '▼'} {Math.abs(gameState.fx_change)}%
            </span>
          </div>

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
            <h3>نرخ بهره بازار</h3>
            <div className="value small">{gameState.effective_rate}%</div>
            <span className="hint">با تأخیر ۳ ماهه</span>
          </div>
        </div>

        {/* 4. Charts */}
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

        {/* 5. Controls */}
        <div className="controls-area">
          {/* Slider 1: Interest Rate */}
          <div className="control-group">
              <label>
                تنظیم نرخ بهره سیاستی: <strong>{interestRate}%</strong>
              </label>
              <input 
                type="range" min="-5" max="50" step="0.5"
                value={interestRate}
                onChange={(e) => setInterestRate(e.target.value)}
                className="slider"
              />
              <div className="slider-labels">
                <span>سیاست انبساطی (ارزان)</span>
                <span>سیاست انقباضی (گران)</span>
              </div>
          </div>

          {/* Slider 2: Money Printer */}
          <div className="control-group printer-group">
              <label>
                مدیریت نقدینگی (چاپ پول / فروش اوراق): 
                <strong style={{color: moneyPrinter > 0 ? '#51cf66' : moneyPrinter < 0 ? '#ff6b6b' : '#aaa'}}>
                    {moneyPrinter > 0 ? '+' : ''}{moneyPrinter}
                </strong>
              </label>
              
              <input 
                type="range" 
                min="-20" 
                max="20" 
                step="1"
                value={moneyPrinter}
                onChange={(e) => setMoneyPrinter(e.target.value)}
                className="slider printer-slider"
              />
              
              <div className="slider-labels">
                <span>فروش اوراق (انقباض)</span>
                <span>چاپ پول (تورم‌زا)</span>
              </div>
          </div>

          <button 
            onClick={handleNextTurn} 
            disabled={loading}
            className="action-btn"
          >
            {loading ? "در حال محاسبه..." : "اعمال سیاست‌ها و ماه بعد"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;