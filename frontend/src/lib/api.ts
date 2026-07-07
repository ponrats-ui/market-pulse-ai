import { mockAnalysis, mockFinancials, mockRisk, mockSnapshot, mockWatchlist } from '../data/mockData';
import type { AnalysisResponse, AssetSnapshot, FinancialsResponse, RiskResponse, WatchlistResponse } from '../types/market';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function getJson<T>(path: string, fallback: T): Promise<T> {
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
  asset: (symbol: string): Promise<AssetSnapshot> => getJson(`/api/assets/${encodeURIComponent(symbol)}`, mockSnapshot(symbol)),
  analysis: (symbol: string): Promise<AnalysisResponse> => getJson(`/api/analysis/${encodeURIComponent(symbol)}`, mockAnalysis(symbol)),
  risk: (symbol: string): Promise<RiskResponse> => getJson(`/api/risk/${encodeURIComponent(symbol)}`, mockRisk(symbol)),
  financials: (symbol: string): Promise<FinancialsResponse> => getJson(`/api/financials/${encodeURIComponent(symbol)}`, mockFinancials(symbol)),
};
