import React from 'react';
import { chartModes, chartRanges, type ChartMode } from './chartTypes';

type Props = {
  range: string;
  setRange: (range: string) => void;
  mode: ChartMode;
  setMode: (mode: ChartMode) => void;
  compareEnabled: boolean;
  setCompareEnabled: React.Dispatch<React.SetStateAction<boolean>>;
  fullscreen: boolean;
  setFullscreen: React.Dispatch<React.SetStateAction<boolean>>;
  reset: () => void;
  download: () => void;
};

export function ChartToolbar({ range, setRange, mode, setMode, compareEnabled, setCompareEnabled, setFullscreen, reset, download }: Props) {
  return <div className="pro-chart-toolbar" role="toolbar" aria-label="Professional chart toolbar"><div className="toolbar-group">{chartRanges.map((item) => <button key={item} className={range === item ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setRange(item)} aria-pressed={range === item}>{item.toUpperCase()}</button>)}</div><div className="toolbar-group">{chartModes.map((item) => <button key={item.id} className={mode === item.id ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setMode(item.id)} aria-pressed={mode === item.id}>{item.label}</button>)}</div><div className="toolbar-group"><button className={compareEnabled ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setCompareEnabled((value) => !value)} aria-pressed={compareEnabled}>Compare</button><button className="toolbar-button" onClick={() => setFullscreen((value) => !value)}>Fullscreen</button><button className="toolbar-button" onClick={reset}>Reset View</button><button className="toolbar-button" onClick={download}>Export PNG</button></div></div>;
}

