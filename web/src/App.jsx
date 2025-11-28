import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

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
    restart: "INITIALIZE NEW TERM"
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
    restart: "شروع دوره جدید"
  }
};

function App() {
  const [lang, setLang] = useState('en');
  const t = TRANSLATIONS[lang];
  
  const [gameState, setGameState] = useState(null);
  const [interestRate, setInterestRate] = useState(15.0);
  const [moneyPrinter, setMoneyPrinter] = useState(0.0);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [eventLog, setEventLog] = useState([]);

  const API_URL = "http://127.0.0.1:8000";

  // ... (Initialization & Fetch logic same as before, condensed for brevity) ...
  useEffect(() => { fetchInitialState(); }, [lang]);
  useEffect(() => {
    if (!gameState || gameState.is_game_over) return;
    const timer = setTimeout(() => fetchForecast(), 400);
    return () => clearTimeout(timer);
  }, [interestRate, moneyPrinter, gameState?.turn]);

  const fetchInitialState = async () => {
    try {
      const res = await fetch(`${API_URL}/state?lang=${lang}`);
      const data = await res.json();
      setGameState(data);
      if(data.turn === 1) setInterestRate(data.effective_rate);
      if(history.length === 0) setHistory([data]);
      else setHistory(prev => { const n=[...prev]; n[n.length-1]=data; return n; });
      if (data.events?.length > 0 && (!eventLog.length || eventLog[0].turn !== data.turn)) {
         addEventsToLog(data.events, data.turn);
      }
    } catch (e) { console.error(e); }
  };

  const fetchForecast = async () => {
      try {
        const res = await fetch(`${API_URL}/forecast`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({interest_rate: parseFloat(interestRate), money_printer: parseFloat(moneyPrinter), lang}) });
        if(res.ok) setForecast(await res.json());
      } catch(e){}
  };

  const handleNextTurn = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/next_turn`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({interest_rate: parseFloat(interestRate), money_printer: parseFloat(moneyPrinter), lang}) });
      if(!res.ok) throw new Error();
      const data = await res.json();
      setGameState(data);
      setHistory(p => [...p, data]);
      addEventsToLog(data.events, data.turn);
      setForecast([]);
    } catch(e){} finally { setLoading(false); }
  };

  const handleReset = async () => {
      if(!confirm("Reset game?")) return;
      await fetch(`${API_URL}/reset`, {method:"POST"});
      setHistory([]); setEventLog([]); setMoneyPrinter(0.0); setForecast([]);
      await fetchInitialState();
  };

  const addEventsToLog = (evts, turn) => {
      const tagged = evts.map(e => ({...e, turn}));
      setEventLog(p => [...tagged, ...p]);
  };

  const combinedData = useMemo(() => {
      if (!history.length) return [];
      const h = history.map(d => ({...d, inf_p: null, gdp_p: null, une_p: null}));
      const last = h[h.length-1];
      if(last) { last.inf_p=last.inflation; last.gdp_p=last.gdp_growth; last.une_p=last.unemployment; }
      const f = forecast.map(d => ({turn: d.turn, inflation: null, gdp_growth: null, unemployment: null, inf_p: d.inflation, gdp_p: d.gdp_growth, une_p: d.unemployment}));
      return [...h, ...f];
  }, [history, forecast]);

  if (!gameState) return <div className="loading">LOADING SYSTEM...</div>;
  
  const formatNum = (n) => new Intl.NumberFormat(lang==='fa'?'fa-IR':'en-US').format(n);
  const getTensionColor = (v) => v < 30 ? '#10b981' : v < 70 ? '#f59e0b' : '#ef4444';

  return (
    <div dir={lang === 'fa' ? 'rtl' : 'ltr'}>
      <div className={`app-container ${gameState.is_game_over ? 'blur-bg' : ''}`}>
        
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
                <button className="lang-btn" onClick={() => setLang(l => l==='en'?'fa':'en')}>{lang.toUpperCase()}</button>
                <div className="gov-badge">{t.turn}: {gameState.turn}</div>
                <button className="reset-btn" onClick={handleReset}>⟳</button>
            </div>
        </header>

        {/* --- COL 1: NARRATIVE (Left) --- */}
        <aside className="col-narrative">
            <div className="panel news-feed-container">
                <div className="panel-title">{t.news_title}</div>
                {eventLog.map((e, i) => (
                    <div key={i} className={`news-item ${e.type}`}>
                        <h4>[{e.turn}] {e.title}</h4>
                        <div className="news-meta">{e.desc}</div>
                    </div>
                ))}
                {eventLog.length === 0 && <div style={{color:'#666', fontStyle:'italic', padding:'10px'}}>No recent events.</div>}
            </div>
            
            <div className="panel advisors-container">
                <div className="panel-title">{t.advisors_title}</div>
                {gameState.advisors.map((adv, i) => (
                    <div key={i} className="advisor-mini">
                        <div className="advisor-avatar">{adv.type==='hawk'?'🦅':adv.type==='dove'?'🕊️':'🤖'}</div>
                        <div className="advisor-text">
                            <h5>{adv.name}</h5>
                            <p>{adv.msg}</p>
                        </div>
                    </div>
                ))}
            </div>
        </aside>

        {/* --- COL 2: DATA (Center) --- */}
        <main className="col-data">
            <div className="kpi-row">
                <div className="kpi-card">
                    <span className="kpi-label">{t.inflation}</span>
                    <span className="kpi-value text-red">{gameState.inflation}%</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">{t.gdp}</span>
                    <span className="kpi-value text-green">{gameState.gdp_growth}%</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">{t.unemployment}</span>
                    <span className="kpi-value text-orange">{gameState.unemployment}%</span>
                </div>
                <div className="kpi-card">
                    <span className="kpi-label">{t.fx}</span>
                    <span className="kpi-value text-gold">{formatNum(gameState.exchange_rate)}</span>
                    <span className="kpi-sub">{t.fx_unit}</span>
                </div>
            </div>

            <div className="chart-panel" dir="ltr">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={combinedData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="turn" stroke="#666" />
                        <YAxis stroke="#666" domain={['auto', 'auto']} />
                        <Tooltip contentStyle={{background:'#111', border:'1px solid #444'}} />
                        <Legend />
                        <Line type="monotone" dataKey="inflation" name={t.inflation} stroke="#ef4444" dot={false} strokeWidth={2} />
                        <Line type="monotone" dataKey="gdp_growth" name={t.gdp} stroke="#10b981" dot={false} strokeWidth={2} />
                        <Line type="monotone" dataKey="unemployment" name={t.unemployment} stroke="#f97316" dot={false} strokeWidth={2} />
                        
                        <Line type="monotone" dataKey="inf_p" stroke="#ef4444" strokeDasharray="5 5" dot={false} strokeOpacity={0.5} name="Forecast" />
                        <Line type="monotone" dataKey="gdp_p" stroke="#10b981" strokeDasharray="5 5" dot={false} strokeOpacity={0.5} name="" />
                        <Line type="monotone" dataKey="une_p" stroke="#f97316" strokeDasharray="5 5" dot={false} strokeOpacity={0.5} name="" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </main>

        {/* --- COL 3: COMMAND (Right) --- */}
        <aside className="col-command">
            <div className="panel" style={{flex:'0 0 auto'}}>
                <div className="panel-title">{t.gov_tension}</div>
                <div className="gov-status">
                    <div style={{display:'flex', justifyContent:'space-between', fontSize:'0.8rem'}}>
                        <span>Stable</span><span>Critical</span>
                    </div>
                    <div className="tension-bar">
                        <div className="tension-fill" style={{width:`${gameState.political_tension}%`, background: getTensionColor(gameState.political_tension)}}></div>
                    </div>
                    <div className="gov-text">{gameState.gov_message}</div>
                </div>
            </div>

            <div className="panel controls-panel">
                <div className="panel-title">POLICY CONTROLS</div>
                
                <div className="control-group">
                    <div className="control-label"><span>{t.rate_control}</span><strong>{interestRate}%</strong></div>
                    <input type="range" min="-5" max="50" step="0.5" value={interestRate} onChange={e=>setInterestRate(e.target.value)} className="slider" />
                    <div className="legend"><span>Stimulate</span><span>Restrict</span></div>
                </div>

                <div className="control-group">
                    <div className="control-label"><span>{t.money_control}</span><strong>{moneyPrinter}</strong></div>
                    <input type="range" min="-20" max="20" step="1" value={moneyPrinter} onChange={e=>setMoneyPrinter(e.target.value)} className="slider green" />
                    <div className="legend"><span>Tighten (QT)</span><span>Ease (QE)</span></div>
                </div>

                <button className="big-btn" onClick={handleNextTurn} disabled={loading}>
                    {loading ? t.btn_wait : t.btn_exec}
                </button>
            </div>
        </aside>

      </div>

      {/* --- MODAL --- */}
      {gameState.is_game_over && (
          <div className="modal-overlay">
              <div className={`modal-box ${gameState.game_over_type === 'win' ? 'win' : 'lose'}`}>
                  <h2>{gameState.game_over_type === 'win' ? t.modal_win : t.modal_lose}</h2>
                  <p>{gameState.game_over_reason}</p>
                  <button className="big-btn" onClick={handleReset}>{t.restart}</button>
              </div>
          </div>
      )}
    </div>
  );
}

export default App;