import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

// --- دیکشنری ترجمه‌ها ---
const TRANSLATIONS = {
  en: {
    title: "TARAZ COMMAND",
    turn: "Turn",
    reset: "Reset",
    news_title: "INTELLIGENCE",
    advisors_title: "ADVISORS",
    inflation: "Inflation",
    gdp: "GDP",
    unemployment: "Unemp.",
    fx: "FX Rate",
    fx_unit: "",
    rate_lbl: "Interest Rate",
    money_lbl: "Money Supply",
    btn_exec: "EXECUTE ORDER",
    btn_wait: "CALCULATING...",
    gov_tension: "Gov Tension",
    modal_win: "MISSION ACCOMPLISHED",
    modal_lose: "MISSION FAILED",
    restart: "INITIALIZE NEW TERM",
    confirm_reset: "Reset game progress? This cannot be undone.",
    status_stable: "Stable",
    status_critical: "Critical",
    control_deck: "CONTROL DECK",
    stimulate: "Stimulate",
    restrict: "Restrict",
    tighten: "Tighten (QT)",
    ease: "Ease (QE)",
    loading: "INITIALIZING TARAZ SYSTEMS..."
  },
  fa: {
    title: "سامانه فرماندهی تراز",
    turn: "ماه",
    reset: "ریست",
    news_title: "اخبار و اطلاعات",
    advisors_title: "شورای مشاوران",
    inflation: "تورم",
    gdp: "رشد تولید",
    unemployment: "بیکاری",
    fx: "دلار",
    fx_unit: "تومان",
    rate_lbl: "نرخ بهره",
    money_lbl: "چاپ پول",
    btn_exec: "اجرای دستورات",
    btn_wait: "محاسبه...",
    gov_tension: "تنش با دولت",
    modal_win: "مأموریت موفق",
    modal_lose: "شکست مأموریت",
    restart: "شروع دوره جدید",
    confirm_reset: "آیا مطمئن هستید؟ بازی ریست می‌شود.",
    status_stable: "پایدار",
    status_critical: "بحرانی",
    control_deck: "پنل کنترل",
    stimulate: "انبساطی",
    restrict: "انقباضی",
    tighten: "فروش اوراق",
    ease: "چاپ پول",
    loading: "در حال بارگذاری سیستم..."
  }
};

function App() {
  // --- States ---
  const [lang, setLang] = useState('en');
  const t = TRANSLATIONS[lang]; // دسترسی راحت به ترجمه جاری
  
  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [moneyPrinter, setMoneyPrinter] = useState(0.0);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [eventLog, setEventLog] = useState([]);

  const API_URL = "http://127.0.0.1:8000";

  // --- Effects ---

  // 1. Load data on mount or lang change
  useEffect(() => {
    fetchInitialState();
  }, [lang]);

  // 2. Fetch forecast when inputs change (Debounced)
  useEffect(() => {
    if (!gameState || gameState.is_game_over) return;
    const timer = setTimeout(() => {
        fetchForecast();
    }, 400); // 400ms delay
    return () => clearTimeout(timer);
  }, [interestRate, moneyPrinter, gameState?.turn]);

  // --- API Calls ---

  const fetchInitialState = async () => {
    try {
      const response = await fetch(`${API_URL}/state?lang=${lang}`);
      if (!response.ok) throw new Error("API Connection Failed");
      const data = await response.json();
      
      setGameState(data);
      
      // فقط در اولین لود، اسلایدر را با عدد واقعی سینک کن
      if(data.turn === 1) setInterestRate(data.effective_rate);
      
      // مدیریت تاریخچه نمودار
      if (history.length === 0) {
          setHistory([data]);
      } else {
          // آپدیت آخرین نقطه (برای ترجمه)
          setHistory(prev => {
              const newHist = [...prev];
              newHist[newHist.length - 1] = data; 
              return newHist;
          });
      }

      // لاگ کردن ایونت‌های اولیه
      if (data.events && data.events.length > 0) {
          // جلوگیری از تکرار ایونت در ریلود
          const lastLoggedTurn = eventLog.length > 0 ? eventLog[0].turn : -1;
          if (lastLoggedTurn !== data.turn) {
             addEventsToLog(data.events, data.turn);
          }
      }
    } catch (err) {
      console.error(err);
      setError("خطا در اتصال به سرور. لطفاً backend (uvicorn) را بررسی کنید.");
    }
  };

  const fetchForecast = async () => {
      try {
        const response = await fetch(`${API_URL}/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                interest_rate: parseFloat(interestRate), 
                money_printer: parseFloat(moneyPrinter), 
                lang 
            }),
        });
        if (response.ok) {
            const data = await response.json();
            setForecast(data);
        }
      } catch (err) {
          console.error("Forecast error", err);
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
            money_printer: parseFloat(moneyPrinter), 
            lang 
        }),
      });

      if (!response.ok) throw new Error("Processing Error");
      
      const newData = await response.json();
      setGameState(newData);
      
      setHistory(prev => [...prev, newData]);
      addEventsToLog(newData.events, newData.turn);
      
      // پاک کردن موقت پیش‌بینی تا محاسبه جدید
      setForecast([]);

    } catch (err) {
      setError("خطا در پردازش نوبت.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
      if(!gameState?.is_game_over && !confirm(t.confirm_reset)) return;
      
      setLoading(true);
      try {
          await fetch(`${API_URL}/reset`, { method: "POST" });
          // پاکسازی کامل کلاینت
          setHistory([]);
          setEventLog([]);
          setMoneyPrinter(0.0);
          setForecast([]);
          // دریافت دیتای جدید
          await fetchInitialState();
      } catch(err) {
          setError("Reset Failed");
      } finally {
          setLoading(false);
      }
  };

  // --- Helpers ---

  const addEventsToLog = (newEvents, turn) => {
      if (!newEvents || newEvents.length === 0) return;
      const taggedEvents = newEvents.map(evt => ({ ...evt, turn }));
      setEventLog(prevLog => [...taggedEvents, ...prevLog]); 
  };

  const formatCurrency = (val) => {
      const locale = lang === 'fa' ? 'fa-IR' : 'en-US';
      return new Intl.NumberFormat(locale).format(val);
  };

  const getTensionColor = (val) => {
    if (val < 30) return '#10b981'; // Green
    if (val < 70) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  // آماده‌سازی دیتای نمودار (ترکیب تاریخچه + پیش‌بینی)
  const combinedData = useMemo(() => {
      if (history.length === 0) return [];
      
      // دیتای تاریخی (خط ممتد)
      const data = history.map(h => ({
          ...h,
          inf_p: null, gdp_p: null, une_p: null
      }));

      // نقطه اتصال (آخرین نقطه تاریخچه باید شروع نقطه چین باشد)
      const lastPoint = data[data.length - 1];
      if (lastPoint) {
          lastPoint.inf_p = lastPoint.inflation;
          lastPoint.gdp_p = lastPoint.gdp_growth;
          lastPoint.une_p = lastPoint.unemployment;
      }

      // دیتای پیش‌بینی (خط چین)
      const projData = forecast.map(f => ({
          turn: f.turn,
          inflation: null, gdp_growth: null, unemployment: null,
          inf_p: f.inflation,
          gdp_p: f.gdp_growth,
          une_p: f.unemployment
      }));

      return [...data, ...projData];
  }, [history, forecast]);

  // --- Render ---

  // Loading / Error Screen
  if (!gameState) {
      return (
        <div className="loading-screen" dir={lang === 'fa' ? 'rtl' : 'ltr'}>
            <div className="loading-text">{t.loading}</div>
            {error && <div className="error-message">{error}</div>}
        </div>
      );
  }

  const isGameOver = gameState.is_game_over;

  return (
    <div className="app-wrapper" dir={lang === 'fa' ? 'rtl' : 'ltr'}>
      
      <div className={`container ${isGameOver ? 'blur-background' : ''}`}>
        
        {/* --- HEADER --- */}
        <header className="header-bar">
            <div className="header-left">
                <h1>{t.title}</h1>
                <div className="gov-badge">
                    {gameState.gov_type}
                    <div className="tooltip">{gameState.gov_desc}</div>
                </div>
            </div>
            <div className="header-right">
                <button className="lang-btn" onClick={() => setLang(l => l==='en'?'fa':'en')}>
                    {lang.toUpperCase()}
                </button>
                <div className="status-badge">{t.turn} {gameState.turn}</div>
                <button className="reset-btn" onClick={handleReset} title={t.reset}>⟳</button>
            </div>
        </header>

        {/* --- LEFT: NARRATIVE --- */}
        <aside className="col-narrative">
            {/* News Feed */}
            <div className="panel news-feed">
                <div className="panel-title">{t.news_title}</div>
                <div className="news-list">
                    {eventLog.map((e, i) => (
                        <div key={i} className={`news-item ${e.type}`}>
                            <span className="news-turn">[{t.turn} {e.turn}]</span>
                            <h4>{e.title}</h4>
                            <div className="news-meta">{e.desc}</div>
                        </div>
                    ))}
                    {eventLog.length === 0 && <div className="empty-state">No Data.</div>}
                </div>
            </div>
            
            {/* Advisors */}
            <div className="panel advisors-grid">
                <div className="panel-title">{t.advisors_title}</div>
                {gameState.advisors && gameState.advisors.map((adv, i) => (
                    <div key={i} className={`advisor-card ${adv.type}`}>
                        <div className="advisor-icon">
                            {adv.type==='hawk'?'🦅':adv.type==='dove'?'🕊️':'🤖'}
                        </div>
                        <div className="advisor-content">
                            <h5>{adv.name}</h5>
                            <p>{adv.msg}</p>
                        </div>
                    </div>
                ))}
            </div>
        </aside>

        {/* --- CENTER: DATA --- */}
        <main className="col-data">
            <div className="kpi-row">
                <div className="card">
                    <h3>{t.inflation}</h3>
                    <div className="value red">{gameState.inflation}%</div>
                </div>
                <div className="card">
                    <h3>{t.gdp}</h3>
                    <div className="value green">{gameState.gdp_growth}%</div>
                </div>
                <div className="card">
                    <h3>{t.unemployment}</h3>
                    <div className="value orange">{gameState.unemployment}%</div>
                </div>
                <div className="card">
                    <h3>{t.fx}</h3>
                    <div className="value gold">{formatCurrency(gameState.exchange_rate)}</div>
                    <span className="hint" style={{color: gameState.fx_change > 0 ? '#ef4444' : '#10b981'}}>
                        {gameState.fx_change > 0 ? '▲' : '▼'} {Math.abs(gameState.fx_change)}%
                    </span>
                </div>
            </div>

            <div className="panel chart-panel" dir="ltr">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={combinedData} margin={{top:10, right:10, left:-20, bottom:0}}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                        <XAxis dataKey="turn" stroke="#666" tick={{fontSize: 10}} />
                        <YAxis stroke="#666" tick={{fontSize: 10}} domain={['auto', 'auto']} />
                        <Tooltip contentStyle={{background:'#050505', border:'1px solid #333', borderRadius:'8px'}} />
                        <Legend wrapperStyle={{fontSize:'0.8rem', paddingTop:'10px'}} />
                        
                        <Line type="monotone" dataKey="inflation" name={t.inflation} stroke="#ef4444" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="gdp_growth" name={t.gdp} stroke="#10b981" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="unemployment" name={t.unemployment} stroke="#f59e0b" strokeWidth={2} dot={false} />
                        
                        {/* Forecast Lines (Dashed) */}
                        <Line type="monotone" dataKey="inf_p" stroke="#ef4444" strokeDasharray="4 4" dot={false} strokeOpacity={0.5} name="" />
                        <Line type="monotone" dataKey="gdp_p" stroke="#10b981" strokeDasharray="4 4" dot={false} strokeOpacity={0.5} name="" />
                        <Line type="monotone" dataKey="une_p" stroke="#f59e0b" strokeDasharray="4 4" dot={false} strokeOpacity={0.5} name="" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </main>

        {/* --- RIGHT: COMMAND --- */}
        <aside className="col-command">
            <div className="panel tension-panel">
                <div className="tension-header">
                    <span>{t.gov_tension}</span>
                    <span style={{color: getTensionColor(gameState.political_tension)}}>{gameState.political_tension}%</span>
                </div>
                <div className="progress-bar-bg">
                    <div 
                        className="progress-bar-fill" 
                        style={{
                            width:`${gameState.political_tension}%`, 
                            background: getTensionColor(gameState.political_tension)
                        }}>
                    </div>
                </div>
                <div className="gov-message">{gameState.gov_message}</div>
            </div>

            <div className="panel controls-panel">
                <div className="panel-title">{t.control_deck}</div>
                
                <div className="control-group">
                    <div className="control-label"><span>{t.rate_control}</span><strong>{interestRate}%</strong></div>
                    <input 
                        type="range" min="-5" max="50" step="0.5" 
                        value={interestRate} 
                        onChange={e=>setInterestRate(e.target.value)} 
                        className="slider rate-slider" 
                    />
                    <div className="slider-labels"><span>{t.stimulate}</span><span>{t.restrict}</span></div>
                </div>

                <div className="control-group">
                    <div className="control-label"><span>{t.money_control}</span><strong>{moneyPrinter > 0 ? '+' : ''}{moneyPrinter}</strong></div>
                    <input 
                        type="range" min="-20" max="20" step="1" 
                        value={moneyPrinter} 
                        onChange={e=>setMoneyPrinter(e.target.value)} 
                        className="slider print-slider" 
                    />
                    <div className="slider-labels"><span>{t.tighten}</span><span>{t.ease}</span></div>
                </div>

                <div className="card info" style={{marginTop:'auto', padding:'10px', background:'transparent', border:'none', boxShadow:'none'}}>
                    <div style={{display:'flex', justifyContent:'space-between', width:'100%', fontSize:'0.8rem', color:'#888'}}>
                        <span>{t.market_rate}</span>
                        <span className="value small" style={{fontSize:'1rem', color:'#fff'}}>{gameState.effective_rate}%</span>
                    </div>
                </div>

                <button className="big-btn" onClick={handleNextTurn} disabled={loading || isGameOver}>
                    {loading ? t.btn_wait : t.btn_exec}
                </button>
            </div>
        </aside>

      </div>

      {/* --- MODAL --- */}
      {isGameOver && (
          <div className="modal-overlay">
              <div className={`modal-box ${gameState.game_over_type === 'win' ? 'win' : 'lose'}`}>
                  <h2>{gameState.game_over_type === 'win' ? t.modal_win : t.modal_lose}</h2>
                  <p style={{color:'#ccc', lineHeight:'1.6', marginBottom:'30px'}}>{gameState.game_over_reason}</p>
                  
                  <div className="kpi-row" style={{height:'auto', marginBottom:'30px'}}>
                      <div className="card" style={{background:'rgba(0,0,0,0.3)'}}>
                          <h3>{t.inflation}</h3><div className="value">{gameState.inflation}%</div>
                      </div>
                      <div className="card" style={{background:'rgba(0,0,0,0.3)'}}>
                          <h3>{t.gdp}</h3><div className="value">{gameState.gdp_growth}%</div>
                      </div>
                  </div>

                  <button className="big-btn" onClick={handleReset}>{t.restart}</button>
              </div>
          </div>
      )}
    </div>
  );
}

export default App;