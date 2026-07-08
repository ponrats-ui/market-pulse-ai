import type { AnalysisResponse, AssetHistory, AssetQuote, CalendarResponse, CompareResponse, FinancialsResponse, NewsImpactResponse, RiskResponse, SentimentResponse, WatchlistResponse } from '../types/market';

const unavailableMetadata = {
  provider: 'Unavailable',
  source: 'Unavailable',
  updated_at: '',
  cache_age_seconds: 0,
  cache_status: 'unavailable',
  confidence: 'low',
  status: 'unavailable',
  latency_ms: 0,
};

export const defaultWatchlist: WatchlistResponse = {
  categories: [
    { id: 'crypto', name: 'Crypto', assets: ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD'].map((symbol) => ({ symbol, label: symbol.replace('-USD', ''), type: 'crypto' as const })) },
    { id: 'thai_stocks', name: 'Thai stocks', assets: [{ symbol: 'SET.BK', label: 'SET Index alt', type: 'index' as const }, { symbol: '^SET.BK', label: 'SET Index', type: 'index' as const }, { symbol: '^SET50.BK', label: 'SET50', type: 'index' as const }, ...['PTT.BK', 'AOT.BK', 'CPALL.BK', 'DELTA.BK', 'KBANK.BK'].map((symbol) => ({ symbol, label: symbol, type: 'stock' as const }))] },
    { id: 'global_stocks', name: 'Global stocks', assets: ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META'].map((symbol) => ({ symbol, label: symbol, type: 'stock' as const })) },
    { id: 'global_indices', name: 'Global indices', assets: [{ symbol: '^GSPC', label: 'S&P 500', type: 'index' as const }, { symbol: '^IXIC', label: 'Nasdaq', type: 'index' as const }, { symbol: '^DJI', label: 'Dow Jones', type: 'index' as const }, { symbol: '^N225', label: 'Nikkei', type: 'index' as const }, { symbol: '^HSI', label: 'Hang Seng', type: 'index' as const }, { symbol: '^GDAXI', label: 'DAX', type: 'index' as const }] },
    { id: 'energy', name: 'Energy', assets: [{ symbol: 'CL=F', label: 'WTI Oil', type: 'commodity' as const }, { symbol: 'BZ=F', label: 'Brent Oil', type: 'commodity' as const }, { symbol: 'NG=F', label: 'Natural Gas', type: 'commodity' as const }] },
    { id: 'precious_metals', name: 'Precious metals', assets: [{ symbol: 'GC=F', label: 'Gold', type: 'commodity' as const }, { symbol: 'SI=F', label: 'Silver', type: 'commodity' as const }, { symbol: 'PL=F', label: 'Platinum', type: 'commodity' as const }, { symbol: 'HG=F', label: 'Copper', type: 'commodity' as const }] },
    { id: 'fx_macro', name: 'FX / Macro', assets: [{ symbol: 'THB=X', label: 'USDTHB', type: 'fx' as const }, { symbol: 'DX-Y.NYB', label: 'DXY', type: 'macro' as const }, { symbol: '^TNX', label: 'US10Y', type: 'macro' as const }] },
  ],
};

export const unavailableQuote = (symbol: string): AssetQuote => ({ symbol, name: symbol, asset_type: symbol.endsWith('-USD') ? 'crypto' : 'global_stock', currency: 'Unavailable', price: null, previous_close: null, change: null, change_percent: null, open: null, high: null, low: null, volume: null, market_cap: null, source: 'Unavailable', timestamp: '', metadata: unavailableMetadata, error: 'Real market quote unavailable. Configure the backend API to load live provider data.' });
export const unavailableHistory = (symbol: string): AssetHistory => ({ symbol, range: '1mo', interval: '1d', source: 'Unavailable', metadata: unavailableMetadata, points: [], error: 'Historical data unavailable.' });
export const unavailableAnalysis = (symbol: string): AnalysisResponse => ({ symbol, trend: 'unavailable', facts: ['There is currently insufficient market data to produce a reliable analysis.'], interpretation: ['ข้อมูลยังไม่เพียงพอสำหรับการวิเคราะห์ที่น่าเชื่อถือ'], bullish_factors: [], bearish_factors: [], risks: ['Provider data is unavailable or incomplete.'], risk_score: null, volatility_level: 'unavailable', support_resistance: { support: 'Unavailable', resistance: 'Unavailable' }, invalidation: 'Unavailable until sufficient market data is available.', cautious_action_plan: ['Wait for complete market data before forming a view.'], disclaimer: 'This is not financial advice.', metadata: unavailableMetadata });
export const unavailableRisk = (symbol: string): RiskResponse => ({ symbol, asset_type: 'Unavailable', risk_score: null, volatility_level: 'unavailable', main_risks: ['Unable to estimate risk.'], risk_controls: ['Wait for real quote and historical price data before estimating risk.'], facts: ['Risk analysis requires real price movement and historical volatility data.'], interpretation: 'Unable to estimate risk.', disclaimer: 'This is not financial advice.', metadata: unavailableMetadata });
export const unavailableFinancials = (symbol: string): FinancialsResponse => ({ symbol, applicable: false, status: 'unavailable', message: 'Financial statement data is unavailable for this asset or provider response.', message_th: 'ยังไม่มีข้อมูลงบการเงินสำหรับสินทรัพย์นี้หรือจากผู้ให้บริการ', disclaimer: 'This is not financial advice.', metadata: unavailableMetadata });
export const unavailableCompare = (symbols: string[]): CompareResponse => ({ symbols, items: symbols.map((symbol) => ({ symbol, name: symbol, asset_type: 'Unavailable', price: null, change_percent: null, currency: 'Unavailable', volatility_estimate: 'unavailable', risk_score: null, source: 'Unavailable' })), performance_points: [], summary: { th: 'ยังไม่มีข้อมูลตลาดจริงเพียงพอสำหรับการเปรียบเทียบ', en: 'Insufficient real market data is available for comparison.' }, disclaimer: 'This is not financial advice.' });
export const unavailableAssistant = (symbol: string, language: string) => ({ answer: language === 'th' ? `ข้อมูลยังไม่เพียงพอสำหรับการวิเคราะห์ที่น่าเชื่อถือสำหรับ ${symbol}` : `There is currently insufficient market data to produce a reliable analysis for ${symbol}.`, facts_used: [`symbol=${symbol}`, 'source=Unavailable'], risks: language === 'th' ? ['ข้อมูลตลาดไม่ครบถ้วน'] : ['Market data is incomplete'], follow_up_questions: [], disclaimer: 'This is not financial advice.' });
export const unavailableCalendar: CalendarResponse = { source: 'Unavailable', provider_configured: false, message: 'Economic calendar provider is not configured.', message_th: 'ยังไม่ได้ตั้งค่าผู้ให้บริการปฏิทินเศรษฐกิจ', events: [] };
export const unavailableNewsImpact = (symbol: string): NewsImpactResponse => ({ symbol, source: 'Unavailable', provider_configured: false, provider_roadmap: ['Finnhub', 'NewsAPI', 'Alpha Vantage News', 'GDELT', 'RSS feeds'], items: [], message: 'No news provider configured.', message_th: 'ยังไม่ได้ตั้งค่าผู้ให้บริการข่าว', disclaimer: 'This is not financial advice.' });
export const unavailableSentiment = (symbol: string): SentimentResponse => ({ symbol, score: null, label: 'Unavailable', source: 'Unavailable', provider_configured: false, note: 'Sentiment data unavailable.', note_th: 'ยังไม่มีข้อมูล sentiment' });
