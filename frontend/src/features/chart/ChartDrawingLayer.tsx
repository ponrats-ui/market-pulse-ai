import type { ReactNode } from 'react';
import type { Drawing } from './chartTypes';

export function ChartDrawingLayer({ drawings, draft, renderDrawing }: { drawings: Drawing[]; draft: Drawing | null; renderDrawing: (drawing: Drawing) => ReactNode }) {
  return <g aria-label="User drawing layer">{drawings.map(renderDrawing)}{draft && renderDrawing({ ...draft, x2: draft.x1 + 1, y2: draft.y1 + 1 })}</g>;
}

