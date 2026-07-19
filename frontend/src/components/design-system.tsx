import React from 'react';
import { AlertTriangle, CheckCircle2, Info, ShieldAlert, TrendingDown, TrendingUp } from 'lucide-react';

export const designTokens = {
  color: {
    background: {
      primary: '#05070d',
      secondary: '#08111f',
      card: '#0a101c',
      elevated: '#101827',
    },
    border: '#1e2b3f',
    divider: '#26364f',
    text: {
      primary: '#f4f8ff',
      secondary: '#c6d3e6',
      muted: '#8ea0ba',
      metadata: '#6f8099',
    },
    state: {
      positive: '#39e58d',
      negative: '#ff6678',
      warning: '#f5b84b',
      neutral: '#8ca3bd',
      information: '#38bdf8',
      ai: '#b78cff',
      health: '#34d399',
      risk: '#fb923c',
      news: '#38bdf8',
      success: '#33d17a',
      selected: '#35d0ff',
      disabled: '#52627a',
    },
  },
  radius: {
    card: 8,
    control: 6,
    pill: 999,
  },
  spacing: {
    xxs: 4,
    xs: 8,
    sm: 12,
    md: 16,
    lg: 20,
    xl: 24,
    '2xl': 32,
    '3xl': 40,
    '4xl': 48,
    '5xl': 64,
  },
  typography: {
    hero: '1.9rem',
    sectionTitle: '0.78rem',
    cardTitle: '0.86rem',
    headline: '1.15rem',
    body: '0.88rem',
    caption: '0.75rem',
    metadata: '0.68rem',
    button: '0.78rem',
    badge: '0.68rem',
  },
} as const;

type Tone = 'positive' | 'negative' | 'warning' | 'neutral' | 'info' | 'ai' | 'health' | 'risk' | 'unavailable';

const toneIcon: Record<Tone, React.ReactNode> = {
  positive: <TrendingUp size={13} />,
  negative: <TrendingDown size={13} />,
  warning: <AlertTriangle size={13} />,
  neutral: <Info size={13} />,
  info: <Info size={13} />,
  ai: <Info size={13} />,
  health: <CheckCircle2 size={13} />,
  risk: <ShieldAlert size={13} />,
  unavailable: <Info size={13} />,
};

export function Card({ title, insight, children, footer }: { title?: string; insight?: string; children: React.ReactNode; footer?: React.ReactNode }) {
  return <section className="ds-card">{title && <SectionHeader title={title} insight={insight} />}{children}{footer && <footer className="ds-card-footer">{footer}</footer>}</section>;
}

export function SectionHeader({ title, insight }: { title: string; insight?: string }) {
  return <header className="ds-section-header"><h2>{title}</h2>{insight && <p>{insight}</p>}</header>;
}

export function Badge({ tone = 'neutral', children }: { tone?: Tone; children: React.ReactNode }) {
  return <span className={`ds-badge ds-badge-${tone}`}>{toneIcon[tone]}{children}</span>;
}

export function Button({ variant = 'secondary', children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' }) {
  return <button {...props} className={`ds-button ds-button-${variant} ${props.className ?? ''}`.trim()}>{children}</button>;
}

export function IconButton({ label, children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { label: string }) {
  return <button {...props} aria-label={label} className={`ds-icon-button ${props.className ?? ''}`.trim()}>{children}</button>;
}

export function Metric({ label, value, hint, tone = 'neutral' }: { label: string; value: React.ReactNode; hint?: string; tone?: Tone }) {
  return <div className={`ds-metric ds-metric-${tone}`}><span>{label}</span><strong>{value}</strong>{hint && <small>{hint}</small>}</div>;
}

export function ProgressMeter({ value, label, tone = 'info' }: { value: number; label?: string; tone?: Tone }) {
  const safeValue = Math.max(0, Math.min(100, value));
  return <div className={`ds-progress ds-progress-${tone}`} aria-label={label ?? `Progress ${safeValue}%`}><i style={{ width: `${safeValue}%` }} /></div>;
}

export function InsightBox({ tone = 'info', children }: { tone?: Tone; children: React.ReactNode }) {
  return <div className={`ds-insight ds-insight-${tone}`}>{toneIcon[tone]}<p>{children}</p></div>;
}

export const Tooltip = ({ label, children }: { label: string; children: React.ReactNode }) => <span className="ds-tooltip" title={label}>{children}</span>;
export const InfoRow = ({ label, value }: { label: string; value: React.ReactNode }) => <div className="ds-info-row"><span>{label}</span><strong>{value}</strong></div>;
export const ExecutiveSummary = Card;
export const RiskMeter = ProgressMeter;
export const HealthMeter = ProgressMeter;
