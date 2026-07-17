import { defaultWatchlist, unavailableAnalysis, unavailableAssistant, unavailableCalendar, unavailableCompare, unavailableFinancials, unavailableHistory, unavailableNewsImpact, unavailableQuote, unavailableRisk, unavailableSentiment } from '../data/unavailableData';
import type { AnalysisResponse, AssetSearchResponse, AssistantResponse, AssetHistory, AssetQuote, CalendarResponse, CompareResponse, FinancialsResponse, MarketConditionResponse, NewsImpactResponse, PortfolioEvaluationResponse, PortfolioHolding, QuotesResponse, RiskResponse, SectorResponse, SentimentResponse, TechnicalResponse, SparklinesResponse, WatchlistResponse } from '../types/market';

const PRODUCTION_API_BASE_URL = 'https://market-pulse-ai-api.onrender.com';
const RAW_API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').trim();
const API_BASE_URL = resolveApiBaseUrl(RAW_API_BASE_URL);
const REQUEST_TIMEOUT_MS = 20000;
const BATCH_QUOTES_TIMEOUT_MS = 120000;

export class ApiRequestCanceledError extends Error {
  constructor(message = 'Request was canceled') {
    super(message);
    this.name = 'ApiRequestCanceledError';
  }
}

class ApiRequestTimeoutError extends Error {
  constructor(message = 'Request timed out') {
    super(message);
    this.name = 'ApiRequestTimeoutError';
  }
}

interface ApiRequestOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
}

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

export function isApiRequestCanceled(error: unknown): boolean {
  return error instanceof ApiRequestCanceledError || (error instanceof DOMException && error.name === 'AbortError');
}

async function getJson<T>(path: string, fallback: T, options: ApiRequestOptions = {}): Promise<T> {
  if (!API_BASE_URL) return fallback;
  if (options.signal?.aborted) throw new ApiRequestCanceledError();
  const controller = new AbortController();
  let timedOut = false;
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, options.timeoutMs ?? REQUEST_TIMEOUT_MS);
  const abortActiveRequest = () => controller.abort();
  options.signal?.addEventListener('abort', abortActiveRequest, { once: true });
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    if (timedOut) {
      const timeoutError = new ApiRequestTimeoutError(`Request timed out after ${options.timeoutMs ?? REQUEST_TIMEOUT_MS}ms`);
      console.error(`Market Pulse API request timed out for ${path}`, { url, error: timeoutError });
      throw timeoutError;
    }
    if (isApiRequestCanceled(error)) {
      throw new ApiRequestCanceledError();
    }
    console.error(`Market Pulse API request failed for ${path}`, { url, error });
    throw error;
  } finally {
    window.clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abortActiveRequest);
  }
}

async function postJson<T>(path: string, body: unknown, fallback: T, options: ApiRequestOptions = {}): Promise<T> {
  if (!API_BASE_URL) return fallback;
  if (options.signal?.aborted) throw new ApiRequestCanceledError();
  const controller = new AbortController();
  let timedOut = false;
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, options.timeoutMs ?? REQUEST_TIMEOUT_MS);
  const abortActiveRequest = () => controller.abort();
  options.signal?.addEventListener('abort', abortActiveRequest, { once: true });
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.json() as T;
  } catch (error) {
    if (timedOut) {
      const timeoutError = new ApiRequestTimeoutError(`Request timed out after ${options.timeoutMs ?? REQUEST_TIMEOUT_MS}ms`);
      console.error(`Market Pulse API request timed out for ${path}`, { url, error: timeoutError });
      throw timeoutError;
    }
    if (isApiRequestCanceled(error)) {
      throw new ApiRequestCanceledError();
    }
    console.error(`Market Pulse API request failed for ${path}`, { url, error });
    throw error;
  } finally {
    window.clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abortActiveRequest);
  }
}

async function searchJson(query: string): Promise<AssetSearchResponse> {
  if (!API_BASE_URL) throw new Error('Market Pulse API base URL is not configured for asset registry search.');
  return getJson(`/api/assets/search?q=${encodeURIComponent(query)}&limit=50`, { query, count: 0, assets: [], source: 'Unavailable' });
}

export const api = {
  watchlist: (): Promise<WatchlistResponse> => getJson('/api/watchlist', defaultWatchlist),
  searchAssets: (query: string): Promise<AssetSearchResponse> => searchJson(query),
  sectors: (): Promise<SectorResponse> => getJson('/api/sectors', { sectors: [], source: 'Unavailable', limitations: ['Sector browser is unavailable until the backend is reachable.'] }),
  quotes: (symbols: string[], options?: ApiRequestOptions): Promise<QuotesResponse> => getJson(`/api/assets/quotes?symbols=${symbols.map(encodeURIComponent).join(',')}`, { symbols, items: symbols.map(unavailableQuote), source: 'Unavailable' }, { timeoutMs: BATCH_QUOTES_TIMEOUT_MS, ...options }),
  quote: (symbol: string): Promise<AssetQuote> => getJson(`/api/assets/${encodeURIComponent(symbol)}`, unavailableQuote(symbol)),
  history: (symbol: string, range = '1mo', interval = '1d'): Promise<AssetHistory> => getJson(`/api/assets/${encodeURIComponent(symbol)}/history?range=${encodeURIComponent(range)}&interval=${encodeURIComponent(interval)}`, unavailableHistory(symbol)),
  sparklines: (symbols: string[]): Promise<SparklinesResponse> => getJson(`/api/assets/sparklines?symbols=${symbols.map(encodeURIComponent).join(',')}`, { symbols, items: symbols.map((symbol) => ({ symbol, points: [], start_price: null, end_price: null, change_percent: null, provider: 'Unavailable', timestamp: '', stale: false, unavailable_reason: '7-day history unavailable from provider' })), source: 'Unavailable' }),
  technical: (symbol: string, range = '1y', interval = '1d'): Promise<TechnicalResponse> => getJson(`/api/technical/${encodeURIComponent(symbol)}?range=${encodeURIComponent(range)}&interval=${encodeURIComponent(interval)}`, { symbol, status: 'unavailable', available_indicators: [], indicators: {}, series: [], source: 'Unavailable', message: 'Technical analysis unavailable.', message_th: 'ยังไม่มีข้อมูลวิเคราะห์ทางเทคนิค', disclaimer: 'This is not financial advice.' }),
  analysis: (symbol: string): Promise<AnalysisResponse> => getJson(`/api/analysis/${encodeURIComponent(symbol)}`, unavailableAnalysis(symbol)),
  risk: (symbol: string): Promise<RiskResponse> => getJson(`/api/risk/${encodeURIComponent(symbol)}`, unavailableRisk(symbol)),
  financials: (symbol: string): Promise<FinancialsResponse> => getJson(`/api/financials/${encodeURIComponent(symbol)}`, unavailableFinancials(symbol)),
  compare: (symbols: string[]): Promise<CompareResponse> => getJson(`/api/compare?symbols=${symbols.map(encodeURIComponent).join(',')}`, unavailableCompare(symbols)),
  ask: (question: string, selectedSymbol: string, language: string): Promise<AssistantResponse> => postJson('/api/assistant/ask', { question, selected_symbol: selectedSymbol, language }, unavailableAssistant(selectedSymbol, language)),
  evaluatePortfolio: (holdings: PortfolioHolding[]): Promise<PortfolioEvaluationResponse> => postJson('/api/portfolio/evaluate', { holdings }, { items: [], total_value: null, total_cost: null, total_gain_loss: null, total_gain_loss_percent: null, source: 'Unavailable', disclaimer: 'This is not financial advice.' }),
  calendar: (): Promise<CalendarResponse> => getJson('/api/calendar', unavailableCalendar),
  newsImpact: (symbol: string): Promise<NewsImpactResponse> => getJson(`/api/news-impact/${encodeURIComponent(symbol)}`, unavailableNewsImpact(symbol)),
  sentiment: (symbol: string): Promise<SentimentResponse> => getJson(`/api/sentiment/${encodeURIComponent(symbol)}`, unavailableSentiment(symbol)),
  marketCondition: (): Promise<MarketConditionResponse> => getJson('/api/market-condition', { state_th: 'รอข้อมูล', state_en: 'Awaiting data', average_change_percent: null, sentiment: unavailableSentiment('BTC-USD'), metrics: [], evidence: [], unavailable: ['Market condition provider unavailable'], provider: 'Unavailable', disclaimer: 'This is not financial advice.' }),
};
