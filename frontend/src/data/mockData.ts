import type { AnalysisResponse, AssetHistory, AssetQuote, FinancialsResponse, RiskResponse, WatchlistResponse } from '../types/market';

export const mockWatchlist: WatchlistResponse = {
  categories: [
    { id: 'crypto', name: 'Crypto', assets: ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD'].map((symbol) => ({ symbol, label: symbol.replace('-USD', ''), type: 'crypto' as const })) },
    { id: 'thai_stocks', name: 'Thai stocks', assets: [
      { symbol: 'SET.BK', label: 'SET Index alt', type: 'index' as const }, { symbol: '^SET.BK', label: 'SET Index', type: 'index' as const }, { symbol: '^SET50.BK', label: 'SET50', type: 'index' as const },
      ...['PTT.BK', 'AOT.BK', 'CPALL.BK', 'DELTA.BK', 'KBANK.BK'].map((symbol) => ({ symbol, label: symbol, type: 'stock' as const })),
    ] },
    { id: 'global_stocks', name: 'Global stocks', assets: ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META'].map((symbol) => ({ symbol, label: symbol, type: 'stock' as const })) },
    { id: 'global_indices', name: 'Global indices', assets: [
      { symbol: '^GSPC', label: 'S&P 500', type: 'index' as const }, { symbol: '^IXIC', label: 'Nasdaq', type: 'index' as const }, { symbol: '^DJI', label: 'Dow Jones', type: 'index' as const }, { symbol: '^N225', label: 'Nikkei', type: 'index' as const }, { symbol: '^HSI', label: 'Hang Seng', type: 'index' as const }, { symbol: '^GDAXI', label: 'DAX', type: 'index' as const },
    ] },
    { id: 'energy', name: 'Energy', assets: [{ symbol: 'CL=F', label: 'WTI Oil', type: 'commodity' as const }, { symbol: 'BZ=F', label: 'Brent Oil', type: 'commodity' as const }, { symbol: 'NG=F', label: 'Natural Gas', type: 'commodity' as const }] },
    { id: 'precious_metals', name: 'Precious metals', assets: [{ symbol: 'GC=F', label: 'Gold', type: 'commodity' as const }, { symbol: 'SI=F', label: 'Silver', type: 'commodity' as const }, { symbol: 'PL=F', label: 'Platinum', type: 'commodity' as const }, { symbol: 'HG=F', label: 'Copper', type: 'commodity' as const }] },
    { id: 'fx_macro', name: 'FX / Macro', assets: [{ symbol: 'THB=X', label: 'USDTHB', type: 'fx' as const }, { symbol: 'DX-Y.NYB', label: 'DXY', type: 'macro' as const }, { symbol: '^TNX', label: 'US10Y', type: 'macro' as const }] },
  ],
};

export const mockQuote = (symbol: string): AssetQuote => ({
  symbol, name: symbol, asset_type: symbol.endsWith('-USD') ? 'crypto' : 'global_stock', currency: 'USD', price: 428.72, previous_close: 421.18, change: 7.54, change_percent: 1.79,
  open: 419.5, high: 432.1, low: 414.2, volume: 1420000, market_cap: null, source: 'mock', timestamp: new Date().toISOString(),
});

export const mockHistory = (symbol: string): AssetHistory => ({
  symbol, range: '1mo', interval: '1d', source: 'mock',
  points: Array.from({ length: 30 }, (_, index) => ({
    time: new Date(Date.now() - (29 - index) * 86400000).toISOString(), open: 390 + index, high: 397 + index, low: 386 + index,
    close: Math.round((390 + index * 1.25 + Math.sin(index / 2) * 9) * 100) / 100, volume: 1000000 + index * 24000,
  })),
});

export const mockAnalysis = (symbol: string): AnalysisResponse => ({
  symbol, trend: 'sideways to constructive', facts: ['Mock provider data is active.', 'Price remains above the short-term reference area.', 'Volume confirmation is still needed.'],
  interpretation: ['น่าติดตาม, but confirmation is required.', 'รอจังหวะ is preferred after sharp moves.'], bullish_factors: ['Holding above support would help sentiment.', 'Liquidity conditions may support risk assets.'], bearish_factors: ['A break below support would weaken the setup.', 'Macro shocks can reverse momentum quickly.'], risks: ['เสี่ยงสูง if using leverage.', 'Provider data may be delayed.', 'Volatility can expand suddenly.'], risk_score: 6, volatility_level: 'medium', support_resistance: { support: 'Placeholder support from recent swing lows.', resistance: 'Placeholder resistance from recent swing highs.' }, invalidation: 'The view weakens if price loses support with rising volume.', cautious_action_plan: ['ควรกำหนดแผนรับมือก่อนลงทุน.', 'เหมาะกับผู้รับความเสี่ยงได้ after sizing risk carefully.', 'Avoid assuming any single scenario will happen.'], disclaimer: 'This is not financial advice.',
});

export const mockRisk = (symbol: string): RiskResponse => ({ symbol, asset_type: 'global_stock', risk_score: 6, volatility_level: 'medium', main_risks: ['Gap risk', 'Liquidity risk', 'Macro sensitivity', 'Headline risk'], risk_controls: ['Define maximum loss before entry.', 'Use smaller size during high volatility.', 'Review exposure correlation.'], facts: ['Risk score is heuristic.', 'Volatility and liquidity are reviewed qualitatively.'], interpretation: 'The asset needs disciplined position sizing and clear invalidation.', disclaimer: 'This is not financial advice.' });
export const mockFinancials = (symbol: string): FinancialsResponse => ({ symbol, applicable: true, status: 'mock', facts: { revenue_trend: 'Placeholder: stable to improving', net_profit_trend: 'Placeholder: cyclical', gross_margin: 0.52, net_margin: 0.21, debt_to_equity: 0.78, cash_flow_quality: 'Needs confirmation', roe: 0.18, roa: 0.09, eps: 7.42, pe: 24.8, pbv: 4.1, dividend_yield: 0.012 }, interpretation: { balance_sheet_strength: 'Moderate balance sheet strength.', earnings_quality: 'Review recurring earnings and cash conversion.', valuation_risk: 'Multiple compression risk if growth slows.' }, risks: ['Statement data can lag reality.', 'Valuation depends on growth assumptions.', 'Debt cost can change.'], cautious_action_plan: ['Compare against peers.', 'Check cash flow against earnings.', 'Avoid relying on one valuation metric.'], disclaimer: 'This is not financial advice.' });
