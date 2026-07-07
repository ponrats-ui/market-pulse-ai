export type AssetType = 'crypto' | 'stock' | 'index' | 'commodity' | 'fx' | 'macro';
export interface Asset { symbol: string; label: string; type: AssetType; }
export interface AssetCategory { id: string; name: string; assets: Asset[]; }
export interface WatchlistResponse { categories: AssetCategory[]; }
export interface ChartPoint { date: string; close: number; volume?: number; }
export interface AssetSnapshot { symbol: string; price: number | null; previousClose: number | null; change: number | null; changePercent: number | null; currency: string; asOf: string; source: string; history: ChartPoint[]; }
export interface AnalysisResponse { symbol: string; trend: string; facts: string[]; interpretation: string[]; bullishFactors: string[]; bearishFactors: string[]; risks: string[]; riskScore: number; volatilityLevel: string; supportResistance: { support: string; resistance: string }; invalidation: string; cautiousActionPlan: string[]; disclaimer: string; }
export interface RiskResponse { symbol: string; assetType: string; riskScore: number; level: string; facts: string[]; interpretation: string; risks: string[]; cautiousActionPlan: string[]; disclaimer: string; }
export interface FinancialsResponse { symbol: string; applicable: boolean; message?: string; facts?: Record<string, string | number | null>; interpretation?: Record<string, string | null>; risks?: string[]; cautiousActionPlan?: string[]; alternativeFundamentals?: { assetType: string; focusAreas: string[] }; disclaimer: string; }
