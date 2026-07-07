export type AssetType = 'crypto' | 'stock' | 'index' | 'commodity' | 'fx' | 'macro';
export interface Asset { symbol: string; label: string; type: AssetType; }
export interface AssetCategory { id: string; name: string; assets: Asset[]; }
export interface WatchlistResponse { categories: AssetCategory[]; }
export interface HistoryPoint { time: string; open: number | null; high: number | null; low: number | null; close: number | null; volume: number | null; }
export interface AssetQuote { symbol: string; name: string; asset_type: string; currency: string; price: number | null; previous_close: number | null; change: number | null; change_percent: number | null; open: number | null; high: number | null; low: number | null; volume: number | null; market_cap: number | null; source: string; timestamp: string; error?: string; }
export interface AssetHistory { symbol: string; range: string; interval: string; points: HistoryPoint[]; source: string; error?: string; }
export interface AnalysisResponse { symbol: string; trend: string; facts: string[]; interpretation: string[]; bullish_factors: string[]; bearish_factors: string[]; risks: string[]; risk_score: number; volatility_level: string; support_resistance: { support: string; resistance: string }; invalidation: string; cautious_action_plan: string[]; disclaimer: string; }
export interface RiskResponse { symbol: string; asset_type: string; risk_score: number; volatility_level: string; main_risks: string[]; risk_controls: string[]; facts: string[]; interpretation: string; disclaimer: string; }
export interface FinancialsResponse { symbol: string; applicable: boolean; status?: string; message?: string; facts?: Record<string, string | number | null>; interpretation?: Record<string, string | null>; risks?: string[]; cautious_action_plan?: string[]; alternative_fundamentals?: { asset_type: string; focus_areas: string[] }; disclaimer: string; }
