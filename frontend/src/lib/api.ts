import { defaultWatchlist, unavailableAnalysis, unavailableAssistant, unavailableCalendar, unavailableCompare, unavailableFinancials, unavailableHistory, unavailableNewsImpact, unavailableQuote, unavailableRisk, unavailableSentiment } from '../data/unavailableData';
import type { AnalysisResponse, AssistantResponse, AssetHistory, AssetQuote, CalendarResponse, CompareResponse, FinancialsResponse, NewsImpactResponse, RiskResponse, SentimentResponse, WatchlistResponse } from '../types/market';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 8000;

async function getJson<T>(path: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    console.warn(`Market Pulse API unavailable for ${path}`, error);
    return fallback;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function postJson<T>(path: string, body: unknown, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    console.warn(`Market Pulse API unavailable for ${path}`, error);
    return fallback;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const api = {
  watchlist: (): Promise<WatchlistResponse> => getJson('/api/watchlist', defaultWatchlist),
  quote: (symbol: string): Promise<AssetQuote> => getJson(`/api/assets/${encodeURIComponent(symbol)}`, unavailableQuote(symbol)),
  history: (symbol: string, range = '1mo', interval = '1d'): Promise<AssetHistory> => getJson(`/api/assets/${encodeURIComponent(symbol)}/history?range=${encodeURIComponent(range)}&interval=${encodeURIComponent(interval)}`, unavailableHistory(symbol)),
  analysis: (symbol: string): Promise<AnalysisResponse> => getJson(`/api/analysis/${encodeURIComponent(symbol)}`, unavailableAnalysis(symbol)),
  risk: (symbol: string): Promise<RiskResponse> => getJson(`/api/risk/${encodeURIComponent(symbol)}`, unavailableRisk(symbol)),
  financials: (symbol: string): Promise<FinancialsResponse> => getJson(`/api/financials/${encodeURIComponent(symbol)}`, unavailableFinancials(symbol)),
  compare: (symbols: string[]): Promise<CompareResponse> => getJson(`/api/compare?symbols=${symbols.map(encodeURIComponent).join(',')}`, unavailableCompare(symbols)),
  ask: (question: string, selectedSymbol: string, language: string): Promise<AssistantResponse> => postJson('/api/assistant/ask', { question, selected_symbol: selectedSymbol, language }, unavailableAssistant(selectedSymbol, language)),
  calendar: (): Promise<CalendarResponse> => getJson('/api/calendar', unavailableCalendar),
  newsImpact: (symbol: string): Promise<NewsImpactResponse> => getJson(`/api/news-impact/${encodeURIComponent(symbol)}`, unavailableNewsImpact(symbol)),
  sentiment: (symbol: string): Promise<SentimentResponse> => getJson(`/api/sentiment/${encodeURIComponent(symbol)}`, unavailableSentiment(symbol)),
};
