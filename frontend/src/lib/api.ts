import { defaultWatchlist, unavailableAnalysis, unavailableAssistant, unavailableCalendar, unavailableCompare, unavailableFinancials, unavailableHistory, unavailableNewsImpact, unavailableQuote, unavailableRisk, unavailableSentiment } from '../data/unavailableData';
import type { AnalysisResponse, AssetSearchResponse, AssistantResponse, AssetHistory, AssetQuote, CalendarResponse, CompareResponse, FinancialsResponse, NewsImpactResponse, PortfolioEvaluationResponse, PortfolioHolding, QuotesResponse, RiskResponse, SentimentResponse, WatchlistResponse } from '../types/market';

const PRODUCTION_API_BASE_URL = 'https://market-pulse-ai-api.onrender.com';
const RAW_API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').trim();
const API_BASE_URL = resolveApiBaseUrl(RAW_API_BASE_URL);
const REQUEST_TIMEOUT_MS = 8000;

if (!API_BASE_URL && import.meta.env.DEV) {
  console.warn('Market Pulse API base URL is not configured. Set VITE_API_BASE_URL to a running backend URL to load live market data.');
}

function resolveApiBaseUrl(value: string): string {
  const normalized = value.replace(/\/$/, '');
  if (isProductionPagesHost() && (!normalized || isLoopbackApiUrl(normalized))) {
    return PRODUCTION_API_BASE_URL;
  }
  return normalized;
}

function isProductionPagesHost(): boolean {
  return typeof window !== 'undefined' && window.location.hostname === 'market-pulse-ai.pages.dev';
}

function isLoopbackApiUrl(value: string): boolean {
  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(value);
}

async function getJson<T>(path: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    console.error(`Market Pulse API request failed for ${path}`, { url, error });
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function postJson<T>(path: string, body: unknown, fallback: T): Promise<T> {
  if (!API_BASE_URL) return fallback;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    console.error(`Market Pulse API request failed for ${path}`, { url, error });
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const api = {
  watchlist: (): Promise<WatchlistResponse> => getJson('/api/watchlist', defaultWatchlist),
  searchAssets: (query: string): Promise<AssetSearchResponse> => getJson(`/api/assets/search?q=${encodeURIComponent(query)}`, { query, count: 0, assets: [], source: 'Unavailable' }),
  quotes: (symbols: string[]): Promise<QuotesResponse> => getJson(`/api/assets/quotes?symbols=${symbols.map(encodeURIComponent).join(',')}`, { symbols, items: symbols.map(unavailableQuote), source: 'Unavailable' }),
  quote: (symbol: string): Promise<AssetQuote> => getJson(`/api/assets/${encodeURIComponent(symbol)}`, unavailableQuote(symbol)),
  history: (symbol: string, range = '1mo', interval = '1d'): Promise<AssetHistory> => getJson(`/api/assets/${encodeURIComponent(symbol)}/history?range=${encodeURIComponent(range)}&interval=${encodeURIComponent(interval)}`, unavailableHistory(symbol)),
  analysis: (symbol: string): Promise<AnalysisResponse> => getJson(`/api/analysis/${encodeURIComponent(symbol)}`, unavailableAnalysis(symbol)),
  risk: (symbol: string): Promise<RiskResponse> => getJson(`/api/risk/${encodeURIComponent(symbol)}`, unavailableRisk(symbol)),
  financials: (symbol: string): Promise<FinancialsResponse> => getJson(`/api/financials/${encodeURIComponent(symbol)}`, unavailableFinancials(symbol)),
  compare: (symbols: string[]): Promise<CompareResponse> => getJson(`/api/compare?symbols=${symbols.map(encodeURIComponent).join(',')}`, unavailableCompare(symbols)),
  ask: (question: string, selectedSymbol: string, language: string): Promise<AssistantResponse> => postJson('/api/assistant/ask', { question, selected_symbol: selectedSymbol, language }, unavailableAssistant(selectedSymbol, language)),
  evaluatePortfolio: (holdings: PortfolioHolding[]): Promise<PortfolioEvaluationResponse> => postJson('/api/portfolio/evaluate', { holdings }, { items: [], total_value: null, total_cost: null, total_gain_loss: null, total_gain_loss_percent: null, source: 'Unavailable', disclaimer: 'This is not financial advice.' }),
  calendar: (): Promise<CalendarResponse> => getJson('/api/calendar', unavailableCalendar),
  newsImpact: (symbol: string): Promise<NewsImpactResponse> => getJson(`/api/news-impact/${encodeURIComponent(symbol)}`, unavailableNewsImpact(symbol)),
  sentiment: (symbol: string): Promise<SentimentResponse> => getJson(`/api/sentiment/${encodeURIComponent(symbol)}`, unavailableSentiment(symbol)),
};
