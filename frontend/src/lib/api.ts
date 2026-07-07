import { mockAnalysis, mockAssistant, mockCalendar, mockCompare, mockFinancials, mockHistory, mockNewsImpact, mockQuote, mockRisk, mockSentiment, mockWatchlist } from '../data/mockData';
import type { AnalysisResponse, AssistantResponse, AssetHistory, AssetQuote, CalendarResponse, CompareResponse, FinancialsResponse, NewsImpactResponse, RiskResponse, SentimentResponse, WatchlistResponse } from '../types/market';

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

async function postJson<T>(path: string, body: unknown, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
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
  compare: (symbols: string[]): Promise<CompareResponse> => getJson(`/api/compare?symbols=${symbols.map(encodeURIComponent).join(',')}`, mockCompare(symbols)),
  ask: (question: string, selectedSymbol: string, language: string): Promise<AssistantResponse> => postJson('/api/assistant/ask', { question, selected_symbol: selectedSymbol, language }, mockAssistant(selectedSymbol, language)),
  calendar: (): Promise<CalendarResponse> => getJson('/api/calendar', mockCalendar),
  newsImpact: (symbol: string): Promise<NewsImpactResponse> => getJson(`/api/news-impact/${encodeURIComponent(symbol)}`, mockNewsImpact(symbol)),
  sentiment: (symbol: string): Promise<SentimentResponse> => getJson(`/api/sentiment/${encodeURIComponent(symbol)}`, mockSentiment(symbol)),
};
