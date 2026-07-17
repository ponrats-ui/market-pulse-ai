import { indicatorToggles, type DrawingTool } from './chartTypes';

type Props = {
  activeIndicators: string[];
  toggleIndicator: (indicator: string) => void;
  tool: DrawingTool;
  setTool: (tool: DrawingTool) => void;
  undo: () => void;
  redo: () => void;
  reset: () => void;
};

export function ChartIndicatorPanel({ activeIndicators, toggleIndicator, tool, setTool, undo, redo, reset }: Props) {
  const show = (name: string) => activeIndicators.includes(name);
  return <details className="pro-chart-indicators"><summary>Indicators and Drawing Tools</summary><div className="indicator-grid">{indicatorToggles.map((item) => <button key={item} className={show(item) ? 'pill watch-button-active' : 'pill'} aria-pressed={show(item)} onClick={() => toggleIndicator(item)}>{item}</button>)}</div><div className="drawing-grid">{(['cursor', 'trend', 'horizontal', 'rectangle', 'text', 'arrow'] as DrawingTool[]).map((item) => <button key={item} className={tool === item ? 'toolbar-button active' : 'toolbar-button'} onClick={() => setTool(item)} aria-pressed={tool === item}>{item}</button>)}<button className="toolbar-button" onClick={undo}>Undo</button><button className="toolbar-button" onClick={redo}>Redo</button><button className="toolbar-button" onClick={reset}>Clear Drawings</button></div></details>;
}

