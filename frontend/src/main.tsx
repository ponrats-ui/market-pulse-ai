import React from 'react';
import ReactDOM from 'react-dom/client';
import { Activity, AlertTriangle, BarChart3, Brain, Building2, ChevronDown, Clock3, Globe2, LineChart, Newspaper, Radar, ShieldCheck, Sparkles, WalletCards } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from './lib/api';
import type { AnalysisResponse, Asset, AssetCategory, AssetHistory, AssetQuote, FinancialsResponse, RiskResponse } from './types/market';
import './styles.css';

const formatNumber = (value: number | null | undefined, digits = 2) => value == null ? 'N/A' : new Intl.NumberFormat('en-US', { maximumFractionDigits: digits }).format(value);
const formatPercent = (value: number | null | undefined) => value == null ? 'N/A' : `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
const formatTime = (value: string | undefined) => value ? new Date(value).toLocaleString() : 'N/A';

function App() {
  const [categories, setCategories] = React.useState<AssetCategory[]>([]);
  const [categoryId, setCategoryId] = React.useState('crypto');
  const [assetSymbol, setAssetSymbol] = React.useState('BTC-USD');
  const [quote, setQuote] = React.useState<AssetQuote | null>(null);
  const [history, setHistory] = React.useState<AssetHistory | null>(null);
  const [analysis, setAnalysis] = React.useState<AnalysisResponse | null>(null);
  const [risk, setRisk] = React.useState<RiskResponse | null>(null);
  const [financials, setFinancials] = React.useState<FinancialsResponse | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    api.watchlist().then((data) => {
      setCategories(data.categories);
      const first = data.categories[0];
      if (first) {
        setCategoryId(first.id);
        setAssetSymbol(first.assets[0]?.symbol ?? 'BTC-USD');
      }
    });
  }, []);

  const selectedCategory = categories.find((category) => category.id === categoryId) ?? categories[0];
  const selectedAsset = selectedCategory?.assets.find((asset) => asset.symbol === assetSymbol) ?? selectedCategory?.assets[0];

  React.useEffect(() => {
    if (!assetSymbol) return;
    let isMounted = true;
    setLoading(true);
    setError(null);
    Promise.all([api.quote(assetSymbol), api.history(assetSymbol), api.analysis(assetSymbol), api.risk(assetSymbol), api.financials(assetSymbol)])
      .then(([quoteData, historyData, analysisData, riskData, financialData]) => {
        if (!isMounted) return;
        setQuote(quoteData);
        setHistory(historyData);
        setAnalysis(analysisData);
        setRisk(riskData);
        setFinancials(financialData);
        setError(quoteData.error ?? historyData.error ?? null);
      })
      .finally(() => isMounted && setLoading(false));
    return () => { isMounted = false; };
  }, [assetSymbol]);

  const handleCategoryChange = (id: string) => {
    const next = categories.find((category) => category.id === id);
    setCategoryId(id);
    setAssetSymbol(next?.assets[0]?.symbol ?? assetSymbol);
  };

  return <main className="min-h-screen bg-terminal-bg text-terminal-text"><div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8"><Header loading={loading} error={error} /><section className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]"><aside className="space-y-4"><ControlPanel categories={categories} categoryId={categoryId} assetSymbol={assetSymbol} onCategoryChange={handleCategoryChange} onAssetChange={setAssetSymbol} /><Watchlist categories={categories} selectedSymbol={assetSymbol} onSelect={setAssetSymbol} /></aside><section className="space-y-4"><PriceStrip quote={quote} asset={selectedAsset} /><DataNotice quote={quote} history={history} error={error} /><div className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(360px,0.8fr)]"><ChartPanel history={history} /><AnalysisPanel analysis={analysis} /></div><div className="grid gap-4 xl:grid-cols-3"><RiskPanel risk={risk} /><FinancialPanel financials={financials} /><NewsPanel asset={selectedAsset} /></div></section></section><footer className="rounded-md border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-100"><span className="font-semibold">This is not financial advice.</span> Use this dashboard for education and research only. Verify market data independently before making decisions.</footer></div></main>;
}

function Header({ loading, error }: { loading: boolean; error: string | null }) { return <header className="flex flex-col gap-4 border-b border-terminal-border pb-5 lg:flex-row lg:items-center lg:justify-between"><div><div className="flex items-center gap-3 text-terminal-cyan"><Sparkles size={20} /><span className="text-xs font-semibold uppercase tracking-[0.24em]">Market Intelligence Terminal</span></div><h1 className="mt-2 text-3xl font-semibold text-white sm:text-4xl">Market Pulse AI</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-terminal-muted">A cautious, data-first dashboard for price action, AI analysis, risk context, and financial statement review.</p></div><div className="flex items-center gap-3 rounded-md border border-terminal-border bg-terminal-panel px-4 py-3 shadow-glow"><Activity className={loading ? 'animate-pulse text-terminal-amber' : error ? 'text-terminal-amber' : 'text-terminal-green'} size={20} /><div><p className="text-xs text-terminal-muted">System status</p><p className="text-sm font-semibold text-white">{loading ? 'Refreshing data' : error ? 'Provider fallback active' : 'Market data ready'}</p></div></div></header>; }
function ControlPanel({ categories, categoryId, assetSymbol, onCategoryChange, onAssetChange }: { categories: AssetCategory[]; categoryId: string; assetSymbol: string; onCategoryChange: (id: string) => void; onAssetChange: (symbol: string) => void; }) { const assets = categories.find((category) => category.id === categoryId)?.assets ?? []; return <Panel title="Asset Console" icon={<WalletCards size={18} />}><label className="field-label">Category</label><div className="select-shell"><select value={categoryId} onChange={(event) => onCategoryChange(event.target.value)}>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select><ChevronDown size={16} /></div><label className="field-label mt-4">Asset</label><div className="select-shell"><select value={assetSymbol} onChange={(event) => onAssetChange(event.target.value)}>{assets.map((asset) => <option key={asset.symbol} value={asset.symbol}>{asset.label}</option>)}</select><ChevronDown size={16} /></div></Panel>; }
function Watchlist({ categories, selectedSymbol, onSelect }: { categories: AssetCategory[]; selectedSymbol: string; onSelect: (symbol: string) => void; }) { return <Panel title="Watchlist" icon={<Radar size={18} />}><div className="space-y-3">{categories.map((category) => <div key={category.id}><p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-terminal-muted">{category.name}</p><div className="grid grid-cols-2 gap-2">{category.assets.map((asset) => <button className={`watch-button ${asset.symbol === selectedSymbol ? 'watch-button-active' : ''}`} key={asset.symbol} onClick={() => onSelect(asset.symbol)}>{asset.label}</button>)}</div></div>)}</div></Panel>; }
function PriceStrip({ quote, asset }: { quote: AssetQuote | null; asset?: Asset }) { const positive = (quote?.change_percent ?? 0) >= 0; return <div className="grid gap-3 md:grid-cols-4"><MetricCard label="Selected asset" value={asset?.label ?? quote?.symbol ?? 'Loading'} icon={<Globe2 size={18} />} /><MetricCard label="Last price" value={`${formatNumber(quote?.price)} ${quote?.currency ?? ''}`} icon={<BarChart3 size={18} />} /><MetricCard label="Daily change" value={formatPercent(quote?.change_percent)} tone={positive ? 'green' : 'red'} icon={<LineChart size={18} />} /><MetricCard label="Data source" value={quote?.source ?? 'mock'} icon={<ShieldCheck size={18} />} /></div>; }
function DataNotice({ quote, history, error }: { quote: AssetQuote | null; history: AssetHistory | null; error: string | null }) { return <div className={`rounded-md border px-4 py-3 text-sm ${error ? 'border-amber-400/30 bg-amber-400/10 text-amber-100' : 'border-terminal-border bg-terminal-panel text-terminal-muted'}`}><div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><span>{error ? `Provider notice: ${error}` : `Quote source: ${quote?.source ?? 'mock'} | History source: ${history?.source ?? 'mock'}`}</span><span className="flex items-center gap-2"><Clock3 size={15} />{formatTime(quote?.timestamp)}</span></div></div>; }
function MetricCard({ label, value, icon, tone }: { label: string; value: string; icon: React.ReactNode; tone?: 'green' | 'red' }) { return <div className="rounded-md border border-terminal-border bg-terminal-panel p-4"><div className="mb-3 flex items-center justify-between text-terminal-muted">{icon}<span className="text-xs uppercase tracking-[0.14em]">{label}</span></div><p className={`text-xl font-semibold ${tone === 'green' ? 'text-terminal-green' : tone === 'red' ? 'text-terminal-red' : 'text-white'}`}>{value}</p></div>; }
function ChartPanel({ history }: { history: AssetHistory | null }) { const chartData = (history?.points ?? []).map((point) => ({ ...point, label: new Date(point.time).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) })); return <Panel title="Price Chart" icon={<LineChart size={18} />} tall><div className="mb-3 flex items-center justify-between text-xs text-terminal-muted"><span>{history?.range ?? '1mo'} / {history?.interval ?? '1d'}</span><span>{history?.points.length ?? 0} points</span></div><div className="h-[360px] w-full"><ResponsiveContainer><AreaChart data={chartData} margin={{ left: 0, right: 10, top: 20, bottom: 0 }}><defs><linearGradient id="pulse" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#35d0ff" stopOpacity={0.42}/><stop offset="95%" stopColor="#35d0ff" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#1e2b3f" strokeDasharray="3 3" /><XAxis dataKey="label" stroke="#7e8da8" tick={{ fontSize: 11 }} /><YAxis stroke="#7e8da8" tick={{ fontSize: 11 }} domain={['dataMin', 'dataMax']} /><Tooltip contentStyle={{ background: '#0a101c', border: '1px solid #1e2b3f', borderRadius: 6, color: '#d9e7ff' }} /><Area type="monotone" dataKey="close" stroke="#35d0ff" strokeWidth={2} fill="url(#pulse)" /></AreaChart></ResponsiveContainer></div></Panel>; }
function AnalysisPanel({ analysis }: { analysis: AnalysisResponse | null }) { return <Panel title="AI Analysis" icon={<Brain size={18} />} tall><div className="space-y-4"><StatusRow label="Trend" value={analysis?.trend ?? 'Loading'} /><StatusRow label="Risk score" value={`${analysis?.risk_score ?? '-'} / 10`} /><StatusRow label="Volatility" value={analysis?.volatility_level ?? 'Loading'} /><ListBlock title="Facts" items={analysis?.facts} /><ListBlock title="Interpretation" items={analysis?.interpretation} /><ListBlock title="Bullish factors" items={analysis?.bullish_factors} /><ListBlock title="Bearish factors" items={analysis?.bearish_factors} /><div className="rounded-md border border-terminal-border bg-terminal-panel2 p-3"><p className="text-xs uppercase tracking-[0.16em] text-terminal-muted">Invalidation</p><p className="mt-2 text-sm leading-6 text-white">{analysis?.invalidation ?? 'Loading'}</p></div></div></Panel>; }
function RiskPanel({ risk }: { risk: RiskResponse | null }) { return <Panel title="Risk Analysis" icon={<AlertTriangle size={18} />}><StatusRow label="Volatility" value={risk?.volatility_level ?? 'Loading'} /><StatusRow label="Score" value={`${risk?.risk_score ?? '-'} / 10`} /><ListBlock title="Main risks" items={risk?.main_risks} /><ListBlock title="Risk controls" items={risk?.risk_controls} /></Panel>; }
function FinancialPanel({ financials }: { financials: FinancialsResponse | null }) { return <Panel title="Financial Statements" icon={<Building2 size={18} />}>{!financials ? <p className="text-sm text-terminal-muted">Loading</p> : !financials.applicable ? <div><p className="text-sm leading-6 text-white">{financials.message}</p><div className="mt-3 flex flex-wrap gap-2">{financials.alternative_fundamentals?.focus_areas.map((item) => <span className="pill" key={item}>{item}</span>)}</div></div> : <div className="grid grid-cols-2 gap-2">{Object.entries(financials.facts ?? {}).slice(0, 12).map(([key, value]) => <div className="rounded-md bg-terminal-panel2 p-2" key={key}><p className="text-[11px] uppercase text-terminal-muted">{key}</p><p className="mt-1 text-sm text-white">{typeof value === 'number' ? formatNumber(value, 3) : value ?? 'N/A'}</p></div>)}</div>}</Panel>; }
function NewsPanel({ asset }: { asset?: Asset }) { return <Panel title="News Monitor" icon={<Newspaper size={18} />}><p className="text-sm leading-6 text-terminal-muted">News integration placeholder for {asset?.label ?? 'selected asset'}. Future providers can add headlines, source credibility, sentiment, and event risk flags.</p><div className="mt-4 space-y-2"><div className="news-line" /><div className="news-line w-4/5" /><div className="news-line w-2/3" /></div></Panel>; }
function Panel({ title, icon, children, tall }: { title: string; icon: React.ReactNode; children: React.ReactNode; tall?: boolean }) { return <section className={`rounded-md border border-terminal-border bg-terminal-panel/95 p-4 shadow-glow ${tall ? 'min-h-[460px]' : ''}`}><div className="mb-4 flex items-center gap-2 border-b border-terminal-border pb-3 text-white">{icon}<h2 className="text-sm font-semibold uppercase tracking-[0.16em]">{title}</h2></div>{children}</section>; }
function StatusRow({ label, value }: { label: string; value: string }) { return <div className="flex items-center justify-between gap-3 rounded-md bg-terminal-panel2 px-3 py-2"><span className="text-xs uppercase tracking-[0.14em] text-terminal-muted">{label}</span><span className="text-sm font-semibold text-white">{value}</span></div>; }
function ListBlock({ title, items }: { title: string; items?: string[] }) { return <div><p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-terminal-muted">{title}</p><ul className="space-y-2">{(items ?? ['Loading']).map((item) => <li className="rounded-md bg-terminal-panel2 px-3 py-2 text-sm leading-6 text-terminal-text" key={item}>{item}</li>)}</ul></div>; }

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
