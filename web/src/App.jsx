import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

// --- Static Translations ---
const TRANSLATIONS = {
  en: {
    title: "Taraz: Macro-Economic Simulator",
    month: "Month",
    reset: "Reset Game",
    tension: "Political Tension",
    news: "News & Events",
    fx: "Exchange Rate",
    inflation: "Inflation",
    gdp: "GDP Growth",
    unemployment: "Unemployment",
    market_rate: "Effective Rate",
    lag_hint: "3-month lag",
    forecast_legend: "Projection (6mo)",
    rate_control: "Policy Interest Rate",
    money_control: "Money Supply (QE/QT)",
    btn_process: "Processing...",
    btn_action: "Execute Policy & Next Month",
    expansionary: "Expansionary",
    contractionary: "Contractionary",
    sell_bonds: "Sell Bonds",
    print_money: "Print Money",
    gov_monitor: "Government is monitoring.",
    currency_unit: "",
    modal_win: "🏆 Term Completed",
    modal_lose: "💀 Game Over",
    restart: "Start New Term",
    final_stats: "Final Stats",
    confirm_reset: "Are you sure? Current game progress will be lost."
  },
  fa: {
    title: "شبیه‌ساز اقتصاد کلان: تراز",
    month: "ماه",
    reset: "بازی جدید",
    tension: "تنش سیاسی",
    news: "اخبار و رویدادها",
    fx: "نرخ ارز",
    inflation: "تورم",
    gdp: "رشد تولید",
    unemployment: "بیکاری",
    market_rate: "نرخ بهره بازار",
    lag_hint: "با تأخیر ۳ ماهه",
    forecast_legend: "پیش‌بینی (۶ ماه)",
    rate_control: "نرخ بهره سیاستی",
    money_control: "مدیریت نقدینگی (چاپ پول)",
    btn_process: "در حال محاسبه...",
    btn_action: "اعمال سیاست‌ها و ماه بعد",
    expansionary: "انبساطی",
    contractionary: "انقباضی",
    sell_bonds: "فروش اوراق",
    print_money: "چاپ پول",
    gov_monitor: "دولت وضعیت را رصد می‌کند.",
    currency_unit: "تومان",
    modal_win: "🏆 پایان دوره",
    modal_lose: "💀 پایان بازی",
    restart: "شروع مجدد",
    final_stats: "آمار نهایی",
    confirm_reset: "آیا مطمئن هستید؟ بازی کاملاً ریست شده و نوع دولت تغییر می‌کند."
  }
};

function App() {
  const [lang, setLang] = useState('en'); // Default English
  const t = TRANSLATIONS[lang];

  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [moneyPrinter, setMoneyPrinter] = useState(0.0); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]); 
  const [eventLog, setEventLog] = useState([]); 

  const API_URL = "http://127.0.0.1:8000";

  // Reload state when language changes to get translated dynamic text
  useEffect(() => {
    fetchInitialState();
  }, [lang]);

  useEffect(() => {
    if (!gameState || gameState.is_game_over) return;
    const timer = setTimeout(() => { fetchForecast(); }, 400);
    return () => clearTimeout(timer);
  }, [interestRate, moneyPrinter, gameState?.turn]);

  const fetchInitialState = async () => {
    try {
      // Pass lang parameter
      const response = await fetch(`${API_URL}/state?lang=${lang}`);
      if (!response.ok) throw new Error("Failed to fetch");
      const data = await response.json();
      
      setGameState(data);
      // Only set interest rate on first load (turn 1) to avoid jumping slider on lang switch
      if(data.turn === 1) setInterestRate(data.effective_rate);
      
      // If just switching lang, we don't want to reset history, but we need to re-fetch history 
      // to translate it? No, history is numbers. Just labels change.
      // Ideally we keep history but update current state.
      if (history.length === 0) setHistory([data]);
      
      // Update latest history point with new translated data
      setHistory(prev => {
          if(prev.length === 0) return [data];
          const newHist = [...prev];
          newHist[newHist.length - 1] = data; 
          return newHist;
      });

      // Don't duplicate events on lang switch
      if (data.events && data.events.length > 0) {
          // Simple check to see if we already logged this turn's events
          const lastLoggedTurn = eventLog.length > 0 ? eventLog[0].turn : 0;
          if (lastLoggedTurn !== data.turn) {
             addEventsToLog(data.events, data.turn);
          }
      }
    } catch (err) { setError("Connection Error"); }
  };

  const fetchForecast = async () => {
      try {
        const response = await fetch(`${API_URL}/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interest_rate: parseFloat(interestRate), money_printer: parseFloat(moneyPrinter), lang }),
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
        body: JSON.stringify({ 
            interest_rate: parseFloat(interestRate), 
            money_printer: parseFloat(moneyPrinter),
            lang: lang 
        }),
      });
      if (!response.ok) throw new Error("Error");
      const newData = await response.json();
      setGameState(newData);
      setHistory(prev => [...prev, newData]);
      addEventsToLog(newData.events, newData.turn);
      setForecast([]);
    } catch (err) { setError("Server Error"); } 
    finally { setLoading(false); }
  };

  const handleReset = async () => {
      if(!gameState.is_game_over && !confirm(t.confirm_reset)) return;
      setLoading(true);
      try {
          await fetch(`${API_URL}/reset`, { method: "POST" });
          setHistory([]); setEventLog([]); setMoneyPrinter(0.0); setForecast([]);
          await fetchInitialState(); // Refetch with current lang
      } catch(err) { setError("Error"); } 
      finally { setLoading(false); }
  };

  const toggleLang = () => {
      setLang(prev => prev === 'en' ? 'fa' : 'en');
  };

  const addEventsToLog = (newEvents, turn) => {
      if (!newEvents || newEvents.length === 0) return;
      const taggedEvents = newEvents.map(evt => ({ ...evt, turn }));
      setEventLog(prevLog => [...taggedEvents, ...prevLog]); 
  };

  const formatCurrency = (val) => {
      const locale = lang === 'fa' ? 'fa-IR' : 'en-US';
      return new Intl.NumberFormat(locale).format(val);
  };

  const getTensionColor = (val) => val < 30 ? '#51cf66' : val < 70 ? '#fcc419' : '#ff6b6b';

  const combinedData = useMemo(() => {
      if (history.length === 0) return [];
      const data = history.map(h => ({ ...h, inflation_proj: null, gdp_proj: null, unemp_proj: null }));
      const lastPoint = data[data.length - 1];
      if (lastPoint) { lastPoint.inflation_proj = lastPoint.inflation; lastPoint.gdp_proj = lastPoint.gdp_growth; lastPoint.unemp_proj = lastPoint.unemployment; }
      const projData = forecast.map(f => ({ turn: f.turn, inflation: null, gdp_growth: null, unemployment: null, inflation_proj: f.inflation, gdp_proj: f.gdp_growth, unemp_proj: f.unemployment }));
      return [...data, ...projData];
  }, [history, forecast]);

  if (!gameState) return <div className="loading">Connecting to Taraz...</div>;
  const isGameOver = gameState.is_game_over;

  return (
    <div className="app-wrapper" dir={lang === 'fa' ? 'rtl' : 'ltr'}>
      <div className={`container ${isGameOver ? 'blur-background' : ''}`}>
        <header>
          <div className="header-info">
            <h1>{t.title}</h1>
            <div className="gov-badge">🏛 {gameState.gov_type}<div className="tooltip">{gameState.gov_desc}</div></div>
          </div>
          <div className="header-actions">
              <button onClick={toggleLang} className="lang-btn">{lang === 'en' ? 'FA' : 'EN'}</button>
              <div className="status-badge">{t.month}: <strong>{gameState.turn}</strong></div>
              <button onClick={handleReset} className="reset-btn" title={t.reset}>⟳</button>
          </div>
        </header>

        {error && <div className="error-box">{error}</div>}

        <div className="tension-container">
            <div className="tension-header"><span>{t.tension}</span><strong style={{color: getTensionColor(gameState.political_tension)}}>{gameState.political_tension}%</strong></div>
            <div className="progress-bar-bg"><div className="progress-bar-fill" style={{ width: `${gameState.political_tension}%`, backgroundColor: getTensionColor(gameState.political_tension) }}></div></div>
            <div className="gov-message">💬 {gameState.gov_message}</div>
        </div>

        <div className="advisors-grid">
            {gameState.advisors && gameState.advisors.map((adv, idx) => (
                <div key={idx} className={`advisor-card ${adv.type}`}>
                    <div className="advisor-icon">{adv.type === 'hawk' ? '🦅' : adv.type === 'dove' ? '🕊️' : '🤖'}</div>
                    <div className="advisor-content"><h5>{adv.name}</h5><p>"{adv.msg}"</p></div>
                </div>
            ))}
        </div>

        {eventLog.length > 0 && (
          <div className="news-feed">
            <h3>🗞 {t.news}</h3>
            <div className="news-list">
              {eventLog.map((evt, index) => (
                <div key={index} className={`news-item ${evt.type}`}>
                  <div className="news-turn">{t.month} {evt.turn}</div>
                  <div className="news-content">
                    <h4>{evt.title}</h4>
                    <p>{evt.desc}</p>
                    <div className="news-impact">
                        {evt.impact.inflation && <span>{t.inflation}: {evt.impact.inflation > 0 ? '+' : ''}{evt.impact.inflation}% </span>}
                        {evt.impact.gdp && <span>{t.gdp}: {evt.impact.gdp > 0 ? '+' : ''}{evt.impact.gdp}% </span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="dashboard-grid">
          <div className="card"><h3>{t.fx} ({t.currency_unit})</h3><div className="value gold">{formatCurrency(gameState.exchange_rate)}</div><span className="hint" style={{color: gameState.fx_change > 0 ? '#ff6b6b' : '#51cf66'}}>{gameState.fx_change > 0 ? '▲' : '▼'} {Math.abs(gameState.fx_change)}%</span></div>
          <div className="card"><h3>{t.inflation}</h3><div className="value red">{gameState.inflation}%</div></div>
          <div className="card"><h3>{t.gdp}</h3><div className="value green">{gameState.gdp_growth}%</div></div>
          <div className="card"><h3>{t.unemployment}</h3><div className="value orange">{gameState.unemployment}%</div></div>
          <div className="card info"><h3>{t.market_rate}</h3><div className="value small">{gameState.effective_rate}%</div><span className="hint">{t.lag_hint}</span></div>
        </div>

        <div className="chart-container" dir="ltr"> 
          <h3>{t.forecast_legend}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={combinedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="turn" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ backgroundColor: '#333', border: '1px solid #555' }} />
              <Legend />
              <Line type="monotone" dataKey="inflation" name={t.inflation} stroke="#ff6b6b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="gdp_growth" name={t.gdp} stroke="#51cf66" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="unemployment" name={t.unemployment} stroke="#fcc419" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="inflation_proj" name="" stroke="#ff6b6b" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="gdp_proj" name="" stroke="#51cf66" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
              <Line type="monotone" dataKey="unemp_proj" name="" stroke="#fcc419" strokeWidth={2} strokeDasharray="5 5" dot={false} activeDot={false} strokeOpacity={0.6} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="controls-area">
          <div className="control-group">
              <label>{t.rate_control}: <strong>{interestRate}%</strong></label>
              <input type="range" min="-5" max="50" step="0.5" value={interestRate} onChange={(e) => setInterestRate(e.target.value)} className="slider" />
              <div className="slider-labels"><span>{t.expansionary}</span><span>{t.contractionary}</span></div>
          </div>
          <div className="control-group printer-group">
              <label>{t.money_control}: <strong style={{color: moneyPrinter > 0 ? '#51cf66' : moneyPrinter < 0 ? '#ff6b6b' : '#aaa'}}>{moneyPrinter > 0 ? '+' : ''}{moneyPrinter}</strong></label>
              <input type="range" min="-20" max="20" step="1" value={moneyPrinter} onChange={(e) => setMoneyPrinter(e.target.value)} className="slider printer-slider" />
              <div className="slider-labels"><span>{t.sell_bonds}</span><span>{t.print_money}</span></div>
          </div>
          <button onClick={handleNextTurn} disabled={loading || isGameOver} className="action-btn">{loading ? t.btn_process : t.btn_action}</button>
        </div>
      </div>

      {isGameOver && (
        <div className="modal-overlay">
          <div className={`modal-content ${gameState.game_over_type}`}>
            <h2>{gameState.game_over_type === 'win' ? t.modal_win : t.modal_lose}</h2>
            <p className="game-over-reason">{gameState.game_over_reason}</p>
            <div className="final-stats"><div>{t.inflation}: {gameState.inflation}%</div><div>{t.gdp}: {gameState.gdp_growth}%</div></div>
            <button onClick={handleReset} className="restart-btn">{t.restart}</button>
          </div>
        </div>
      )}
    </div>
  );
}
export default App;