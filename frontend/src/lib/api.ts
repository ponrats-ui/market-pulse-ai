import { mockAnalysis, mockFinancials, mockHistory, mockQuote, mockRisk, mockWatchlist } from '../data/mockData';
import type { AnalysisResponse, AssetHistory, AssetQuote, FinancialsResponse, RiskResponse, WatchlistResponse } from '../types/market';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/$/, '');

async function getJson<T>(path: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  try {
    const response = await fetch(`${API_BASE_URL}${path}`);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch {
    return fallback;
  }
}

export const api = {
  watchlist: (): Promise<WatchlistResponse> => getJson('/api/watchlist', mockWatchlist),
  quote: (symbol: string): Promise<AssetQuote> => getJson(`/api/assets/${encodeURIComponent(symbol)}`, mockQuote(symbol)),
  history: (symbol: string, range = '1mo', interval = '1d'): Promise<AssetHistory> => getJson(`/api/assets/${encodeURIComponent(symbol)}/history?range=${range}&interval=${interval}`, mockHistory(symbol)),
  analysis: (symbol: string): Promise<AnalysisResponse> => getJson(`/api/analysis/${encodeURIComponent(symbol)}`, mockAnalysis(symbol)),
  risk: (symbol: string): Promise<RiskResponse> => getJson(`/api/risk/${encodeURIComponent(symbol)}`, mockRisk(symbol)),
  financials: (symbol: string): Promise<FinancialsResponse> => getJson(`/api/financials/${encodeURIComponent(symbol)}`, mockFinancials(symbol)),
};
