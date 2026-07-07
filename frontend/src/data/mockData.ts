import type { AnalysisResponse, AssetSnapshot, FinancialsResponse, RiskResponse, WatchlistResponse } from '../types/market';

export const mockWatchlist: WatchlistResponse = {
  categories: [
    { id: 'crypto', name: 'Crypto', assets: ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD'].map((symbol) => ({ symbol, label: symbol.replace('-USD', ''), type: 'crypto' as const })) },
    { id: 'thai_stocks', name: 'Thai stocks', assets: [
      { symbol: '^SET.BK', label: 'SET Index', type: 'index' as const }, { symbol: '^SET50.BK', label: 'SET50', type: 'index' as const },
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

export const mockSnapshot = (symbol: string): AssetSnapshot => ({
  symbol, price: 428.72, previousClose: 421.18, change: 7.54, changePercent: 1.79, currency: 'USD', asOf: 'mock', source: 'mock',
  history: Array.from({ length: 30 }, (_, index) => ({ date: `D-${29 - index}`, close: Math.round((390 + index * 1.25 + Math.sin(index / 2) * 9) * 100) / 100, volume: 1000000 + index * 24000 })),
});

export const mockAnalysis = (symbol: string): AnalysisResponse => ({
  symbol, trend: 'sideways to constructive', facts: ['Mock provider data is active.', 'Price remains above the short-term reference area.', 'Volume confirmation is still needed.'],
  interpretation: ['น่าติดตาม, but confirmation is required.', 'รอจังหวะ is preferred after sharp moves.'], bullishFactors: ['Holding above support would help sentiment.', 'Liquidity conditions may support risk assets.'], bearishFactors: ['A break below support would weaken the setup.', 'Macro shocks can reverse momentum quickly.'], risks: ['เสี่ยงสูง if using leverage.', 'Provider data may be delayed.', 'Volatility can expand suddenly.'], riskScore: 6, volatilityLevel: 'medium', supportResistance: { support: 'Placeholder support from recent swing lows.', resistance: 'Placeholder resistance from recent swing highs.' }, invalidation: 'The view weakens if price loses support with rising volume.', cautiousActionPlan: ['ควรกำหนดแผนรับมือก่อนลงทุน.', 'เหมาะกับผู้รับความเสี่ยงได้ after sizing risk carefully.', 'Avoid assuming any single scenario will happen.'], disclaimer: 'This is not financial advice.',
});

export const mockRisk = (symbol: string): RiskResponse => ({ symbol, assetType: 'stock', riskScore: 6, level: 'Medium', facts: ['Risk score is heuristic.', 'Volatility and liquidity are reviewed qualitatively.'], interpretation: 'The asset needs disciplined position sizing and clear invalidation.', risks: ['Gap risk', 'Liquidity risk', 'Macro sensitivity', 'Headline risk'], cautiousActionPlan: ['Define maximum loss before entry.', 'Use smaller size during high volatility.', 'Review exposure correlation.'], disclaimer: 'This is not financial advice.' });
export const mockFinancials = (symbol: string): FinancialsResponse => ({ symbol, applicable: true, facts: { revenueTrend: 'Placeholder: stable to improving', netProfitTrend: 'Placeholder: cyclical', grossMargin: 0.52, netMargin: 0.21, debtToEquity: 0.78, cashFlowQuality: 'Needs confirmation', roe: 0.18, roa: 0.09, eps: 7.42, pe: 24.8, pbv: 4.1, dividendYield: 0.012, threeToFiveYearTrend: 'Placeholder: compare through full cycle' }, interpretation: { balanceSheetStrength: 'Moderate balance sheet strength.', earningsQuality: 'Review recurring earnings and cash conversion.', valuationRisk: 'Multiple compression risk if growth slows.' }, risks: ['Statement data can lag reality.', 'Valuation depends on growth assumptions.', 'Debt cost can change.'], cautiousActionPlan: ['Compare against peers.', 'Check cash flow against earnings.', 'Avoid relying on one valuation metric.'], disclaimer: 'This is not financial advice.' });
