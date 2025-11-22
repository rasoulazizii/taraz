import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [moneyPrinter, setMoneyPrinter] = useState(0.0); 
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]); 
  const [eventLog, setEventLog] = useState([]); 

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    fetchInitialState();
  }, []);

  useEffect(() => {
    if (!gameState || gameState.is_game_over) return;
    const timer = setTimeout(() => { fetchForecast(); }, 400);
    return () => clearTimeout(timer);
  }, [interestRate, moneyPrinter, gameState?.turn]);

  const fetchInitialState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);
      if (!response.ok) throw new Error("خطا در دریافت اطلاعات");
      const data = await response.json();
      setGameState(data);
      setInterestRate(data.effective_rate);
      setMoneyPrinter(0.0); 
      setHistory([data]);
      if (data.events && data.events.length > 0) addEventsToLog(data.events, data.turn);
    } catch (err) {
      setError("عدم اتصال به سرور.");
      console.error(err);
    }
  };

  const fetchForecast = async () => {
      try {
        const response = await fetch(`${API_URL}/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interest_rate: parseFloat(interestRate), money_printer: parseFloat(moneyPrinter) }),
        });
        if (response.ok) {
            const data = await response.json();
            setForecast(data);
        }
      } catch (err) { console.error(err); }
  };

  const handleNextTurn = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/next_turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interest_rate: parseFloat(interestRate), money_printer: parseFloat(moneyPrinter) }),
      });
      if (!response.ok) throw new Error("خطا در پردازش");
      const newData = await response.json();
      setGameState(newData);
      setHistory(prev => [...prev, newData]);
      addEventsToLog(newData.events, newData.turn);
      setForecast([]);
    } catch (err) { setError("خطا در سرور"); } 
    finally { setLoading(false); }
  };

  const handleReset = async () => {
      if(!gameState.is_game_over && !confirm("آیا مطمئن هستید؟")) return;
      setLoading(true);
      try {
          await fetch(`${API_URL}/reset`, { method: "POST" });
          setHistory([]); setEventLog([]); setMoneyPrinter(0.0); setForecast([]);
          await fetchInitialState();
      } catch(err) { setError("خطا در ریست"); } 
      finally { setLoading(false); }
  };

  const addEventsToLog = (newEvents, turn) => {
      if (!newEvents || newEvents.length === 0) return;
      const taggedEvents = newEvents.map(evt => ({ ...evt, turn }));
      setEventLog(prevLog => [...taggedEvents, ...prevLog]); 
  };

  const formatCurrency = (val) => new Intl.NumberFormat('fa-IR').format(val);
  const getTensionColor = (val) => val < 30 ? '#51cf66' : val < 70 ? '#fcc419' : '#ff6b6b';

  const combinedData = useMemo(() => {
      if (history.length === 0) return [];
      const data = history.map(h => ({ ...h, inflation_proj: null, gdp_proj: null, unemp_proj: null }));
      const lastPoint = data[data.length - 1];
      if (lastPoint) { lastPoint.inflation_proj = lastPoint.inflation; lastPoint.gdp_proj = lastPoint.gdp_growth; lastPoint.unemp_proj = lastPoint.unemployment; }
      const projData = forecast.map(f => ({ turn: f.turn, inflation: null, gdp_growth: null, unemployment: null, inflation_proj: f.inflation, gdp_proj: f.gdp_growth, unemp_proj: f.unemployment }));
      return [...data, ...projData];
  }, [history, forecast]);

  if (!gameState) return <div className="loading">در حال اتصال...</div>;
  const isGameOver = gameState.is_game_over;

  return (
    <div className="app-wrapper" dir="rtl">
      <div className={`container ${isGameOver ? 'blur-background' : ''}`}>
        <header>
          <div className="header-info">
            <h1>شبیه‌ساز اقتصاد کلان: تراز</h1>
            <div className="gov-badge">
                🏛 {gameState.gov_type}
                <div className="tooltip">{gameState.gov_desc}</div>
            </div>
          </div>
          <div className="header-actions">
              <div className="status-badge">ماه: <strong>{gameState.turn}</strong></div>
              <button onClick={handleReset} className="reset-btn" title="بازی جدید">⟳</button>
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        <div className="tension-container">
            <div className="tension-header">
                <span>تنش سیاسی</span>
                <strong style={{color: getTensionColor(gameState.political_tension)}}>{gameState.political_tension}%</strong>
            </div>
            <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: `${gameState.political_tension}%`, backgroundColor: getTensionColor(gameState.political_tension) }}></div>
            </div>
            <div className="gov-message">💬 {gameState.gov_message}</div>
        </div>

        {/* --- Advisors Section (New) --- */}
        <div className="advisors-grid">
            {gameState.advisors && gameState.advisors.map((adv, idx) => (
                <div key={idx} className={`advisor-card ${adv.type}`}>
                    <div className="advisor-icon">
                        {adv.type === 'hawk' ? '🦅' : adv.type === 'dove' ? '🕊️' : '🤖'}
                    </div>
                    <div className="advisor-content">
                        <h5>{adv.name}</h5>
                        <p>"{adv.msg}"</p>
                    </div>
                </div>
            ))}
        </div>

        {eventLog.length > 0 && (
          <div className="news-feed">
            <h3>🗞 اخبار</h3>
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
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="dashboard-grid">
          <div className="card"><h3>نرخ ارز</h3><div className="value gold">{formatCurrency(gameState.exchange_rate)}</div><span className="hint" style={{color: gameState.fx_change > 0 ? '#ff6b6b' : '#51cf66'}}>{gameState.fx_change > 0 ? '▲' : '▼'} {Math.abs(gameState.fx_change)}%</span></div>
          <div className="card"><h3>تورم</h3><div className="value red">{gameState.inflation}%</div></div>
          <div className="card"><h3>رشد GDP</h3><div className="value green">{gameState.gdp_growth}%</div></div>
          <div className="card"><h3>بیکاری</h3><div className="value orange">{gameState.unemployment}%</div></div>
          <div className="card info"><h3>نرخ بازار</h3><div className="value small">{gameState.effective_rate}%</div><span className="hint">مؤثر</span></div>
        </div>

        <div className="chart-container" dir="ltr"> 
          <h3>روند شاخص‌ها (خط‌چین: پیش‌بینی)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={combinedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="turn" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ backgroundColor: '#333', border: '1px solid #555' }} />
              <Legend />
              <Line type="monotone" dataKey="inflation" name="تورم" stroke="#ff6b6b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="gdp_growth" name="رشد GDP" stroke="#51cf66" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="unemployment" name="بیکاری" stroke="#fcc419" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="inflation_proj" name="پیش‌بینی تورم" stroke="#ff6b6b" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="gdp_proj" name="پیش‌بینی رشد" stroke="#51cf66" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="unemp_proj" name="پیش‌بینی بیکاری" stroke="#fcc419" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="controls-area">
          <div className="control-group">
              <label>نرخ بهره سیاستی: <strong>{interestRate}%</strong></label>
              <input type="range" min="-5" max="50" step="0.5" value={interestRate} onChange={(e) => setInterestRate(e.target.value)} className="slider" />
              <div className="slider-labels"><span>انبساطی</span><span>انقباضی</span></div>
          </div>
          <div className="control-group printer-group">
              <label>چاپ پول / اوراق: <strong style={{color: moneyPrinter > 0 ? '#51cf66' : moneyPrinter < 0 ? '#ff6b6b' : '#aaa'}}>{moneyPrinter > 0 ? '+' : ''}{moneyPrinter}</strong></label>
              <input type="range" min="-20" max="20" step="1" value={moneyPrinter} onChange={(e) => setMoneyPrinter(e.target.value)} className="slider printer-slider" />
              <div className="slider-labels"><span>فروش اوراق</span><span>چاپ پول</span></div>
          </div>
          <button onClick={handleNextTurn} disabled={loading || isGameOver} className="action-btn">{loading ? "..." : "اعمال سیاست‌ها"}</button>
        </div>
      </div>

      {isGameOver && (
        <div className="modal-overlay">
          <div className={`modal-content ${gameState.game_over_type}`}>
            <h2>{gameState.game_over_type === 'win' ? '🏆 پیروزی' : '💀 شکست'}</h2>
            <p className="game-over-reason">{gameState.game_over_reason}</p>
            <div className="final-stats">
                <div>تورم: {gameState.inflation}%</div>
                <div>رشد: {gameState.gdp_growth}%</div>
            </div>
            <button onClick={handleReset} className="restart-btn">شروع مجدد</button>
          </div>
        </div>
      )}
    </div>
  );
}
export default App;