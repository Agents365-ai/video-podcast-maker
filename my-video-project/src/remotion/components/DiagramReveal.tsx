// React import not needed with react-jsx transform
import type { VideoProps } from "../Root";
import { useEntrance, useDrawOn, staggerDelay } from "./animations";

/**
 * DiagramReveal — Animated SVG diagram with auto-layout and draw-on effect.
 *
 * Nodes are auto-positioned if x/y are omitted. The layout algorithm:
 * 1. Topological sort based on edges
 * 2. Assign layers (depth from root nodes)
 * 3. Center nodes within each layer
 *
 * Auto-layout usage (recommended):
 *   <DiagramReveal
 *     props={props}
 *     nodes={[
 *       { id: "a", label: "Input" },
 *       { id: "b", label: "Process" },
 *       { id: "c", label: "Output" },
 *     ]}
 *     edges={[
 *       { from: "a", to: "b" },
 *       { from: "b", to: "c" },
 *     ]}
 *   />
 *
 * Manual layout (override x/y):
 *   <DiagramReveal
 *     props={props}
 *     nodes={[
 *       { id: "a", label: "Input", x: 100, y: 80 },
 *       ...
 *     ]}
 *     edges={[...]}
 *   />
 */

export interface DiagramNode {
  id: string;
  label: string;
  x?: number;       // auto-computed if omitted
  y?: number;       // auto-computed if omitted
  icon?: string;
  width?: number;   // default: auto from label length
  height?: number;  // default 56
}

export interface DiagramEdge {
  from: string;
  to: string;
  label?: string;
  style?: "straight" | "curve" | "elbow"; // default "straight"
}

// --- Auto-layout algorithm ---

interface LayoutNode extends DiagramNode {
  x: number;
  y: number;
  width: number;
  height: number;
  layer: number;
}

const autoLayout = (
  nodes: DiagramNode[],
  edges: DiagramEdge[],
  viewWidth: number,
  viewHeight: number,
  direction: "vertical" | "horizontal",
): LayoutNode[] => {
  // Build adjacency lists
  const children = new Map<string, string[]>();
  const parents = new Map<string, string[]>();
  for (const n of nodes) {
    children.set(n.id, []);
    parents.set(n.id, []);
  }
  for (const e of edges) {
    children.get(e.from)?.push(e.to);
    parents.get(e.to)?.push(e.from);
  }

  // Assign layers via BFS from root nodes (nodes with no parents)
  const layerMap = new Map<string, number>();
  const roots = nodes.filter((n) => (parents.get(n.id)?.length ?? 0) === 0);
  // If no roots found (cycle), use all nodes as roots
  const startNodes = roots.length > 0 ? roots : [nodes[0]];

  const queue: { id: string; layer: number }[] = startNodes.map((n) => ({ id: n.id, layer: 0 }));
  const visited = new Set<string>();

  while (queue.length > 0) {
    const { id, layer } = queue.shift()!;
    if (visited.has(id)) {
      // Update to deeper layer if found via longer path
      const existing = layerMap.get(id) ?? 0;
      if (layer > existing) layerMap.set(id, layer);
      continue;
    }
    visited.add(id);
    layerMap.set(id, layer);
    for (const childId of children.get(id) ?? []) {
      queue.push({ id: childId, layer: layer + 1 });
    }
  }

  // Handle unvisited nodes (disconnected)
  for (const n of nodes) {
    if (!layerMap.has(n.id)) layerMap.set(n.id, 0);
  }

  // Group nodes by layer
  const maxLayer = Math.max(...layerMap.values());
  const layers: DiagramNode[][] = Array.from({ length: maxLayer + 1 }, () => []);
  for (const n of nodes) {
    layers[layerMap.get(n.id) ?? 0].push(n);
  }

  // Compute node dimensions
  const getNodeWidth = (n: DiagramNode) => n.width ?? Math.max(120, n.label.length * 16 + 40);
  const getNodeHeight = (n: DiagramNode) => n.height ?? 56;

  // Layout padding
  const padX = 60;
  const padY = 40;
  const usableW = viewWidth - padX * 2;
  const usableH = viewHeight - padY * 2;

  const layerCount = maxLayer + 1;

  // Position each node
  const result: LayoutNode[] = [];

  if (direction === "vertical") {
    // Top-to-bottom flow
    const layerSpacing = layerCount > 1 ? usableH / (layerCount - 1) : 0;

    for (let layer = 0; layer <= maxLayer; layer++) {
      const nodesInLayer = layers[layer];
      const count = nodesInLayer.length;
      const totalWidth = nodesInLayer.reduce((sum, n) => sum + getNodeWidth(n), 0);
      const gapCount = Math.max(count - 1, 1);
      const gap = count > 1 ? Math.min(40, (usableW - totalWidth) / gapCount) : 0;
      const rowWidth = totalWidth + gap * (count - 1);
      let cx = padX + (usableW - rowWidth) / 2;

      for (const n of nodesInLayer) {
        const w = getNodeWidth(n);
        const h = getNodeHeight(n);
        const y = layerCount === 1
          ? padY + usableH / 2
          : padY + layer * layerSpacing;

        result.push({
          ...n,
          x: n.x ?? (cx + w / 2),
          y: n.y ?? y,
          width: w,
          height: h,
          layer,
        });
        cx += w + gap;
      }
    }
  } else {
    // Left-to-right flow
    const layerSpacing = layerCount > 1 ? usableW / (layerCount - 1) : 0;

    for (let layer = 0; layer <= maxLayer; layer++) {
      const nodesInLayer = layers[layer];
      const count = nodesInLayer.length;
      const totalHeight = nodesInLayer.reduce((sum, n) => sum + getNodeHeight(n), 0);
      const gapCount = Math.max(count - 1, 1);
      const gap = count > 1 ? Math.min(30, (usableH - totalHeight) / gapCount) : 0;
      const colHeight = totalHeight + gap * (count - 1);
      let cy = padY + (usableH - colHeight) / 2;

      for (const n of nodesInLayer) {
        const w = getNodeWidth(n);
        const h = getNodeHeight(n);
        const x = layerCount === 1
          ? padX + usableW / 2
          : padX + layer * layerSpacing;

        result.push({
          ...n,
          x: n.x ?? x,
          y: n.y ?? (cy + h / 2),
          width: w,
          height: h,
          layer,
        });
        cy += h + gap;
      }
    }
  }

  return result;
};

// Detect if nodes need auto-layout (any node missing x or y)
const needsAutoLayout = (nodes: DiagramNode[]): boolean =>
  nodes.some((n) => n.x === undefined || n.y === undefined);

// --- Edge path builders ---

const buildEdgePath = (
  fromNode: LayoutNode,
  toNode: LayoutNode,
  style: "straight" | "curve" | "elbow" = "straight",
): string => {
  const fw = fromNode.width / 2;
  const fh = fromNode.height / 2;
  const tw = toNode.width / 2;
  const th = toNode.height / 2;

  const dx = toNode.x - fromNode.x;
  const dy = toNode.y - fromNode.y;
  const horizontal = Math.abs(dx) > Math.abs(dy);

  let x1: number, y1: number, x2: number, y2: number;

  if (horizontal) {
    x1 = fromNode.x + (dx > 0 ? fw : -fw);
    y1 = fromNode.y;
    x2 = toNode.x + (dx > 0 ? -tw : tw);
    y2 = toNode.y;
  } else {
    x1 = fromNode.x;
    y1 = fromNode.y + (dy > 0 ? fh : -fh);
    x2 = toNode.x;
    y2 = toNode.y + (dy > 0 ? -th : th);
  }

  switch (style) {
    case "straight":
      return `M ${x1} ${y1} L ${x2} ${y2}`;
    case "elbow": {
      return horizontal
        ? `M ${x1} ${y1} L ${(x1 + x2) / 2} ${y1} L ${(x1 + x2) / 2} ${y2} L ${x2} ${y2}`
        : `M ${x1} ${y1} L ${x1} ${(y1 + y2) / 2} L ${x2} ${(y1 + y2) / 2} L ${x2} ${y2}`;
    }
    case "curve":
    default: {
      if (horizontal) {
        const cx = (x1 + x2) / 2;
        return `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`;
      }
      const cy = (y1 + y2) / 2;
      return `M ${x1} ${y1} C ${x1} ${cy}, ${x2} ${cy}, ${x2} ${y2}`;
    }
  }
};

const buildArrowHead = (
  fromNode: LayoutNode,
  toNode: LayoutNode,
  size = 7,
): string => {
  const dx = toNode.x - fromNode.x;
  const dy = toNode.y - fromNode.y;
  const horizontal = Math.abs(dx) > Math.abs(dy);
  const tw = toNode.width / 2;
  const th = toNode.height / 2;

  if (horizontal) {
    const x = toNode.x + (dx > 0 ? -tw : tw);
    const y = toNode.y;
    const dir = dx > 0 ? -1 : 1;
    return `M ${x + dir * size} ${y - size} L ${x} ${y} L ${x + dir * size} ${y + size}`;
  }
  const x = toNode.x;
  const y = toNode.y + (dy > 0 ? -th : th);
  const dir = dy > 0 ? -1 : 1;
  return `M ${x - size} ${y + dir * size} L ${x} ${y} L ${x + size} ${y + dir * size}`;
};

// --- Animated sub-components ---

const AnimatedEdge = ({
  fromNode, toNode, edge, color, enabled, delay,
}: {
  fromNode: LayoutNode; toNode: LayoutNode; edge: DiagramEdge;
  color: string; enabled: boolean; delay: number;
}) => {
  const edgePath = buildEdgePath(fromNode, toNode, edge.style);
  const headPath = buildArrowHead(fromNode, toNode);
  const line = useDrawOn(edgePath, enabled, delay, 24, "gentle");
  const head = useDrawOn(headPath, enabled, delay + 16, 10, "snappy");

  return (
    <>
      <path
        d={edgePath}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeOpacity={0.5}
        strokeLinecap="round"
        strokeDasharray={line.strokeDasharray}
        strokeDashoffset={line.strokeDashoffset}
      />
      <path
        d={headPath}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeOpacity={0.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={head.strokeDasharray}
        strokeDashoffset={head.strokeDashoffset}
      />
      {edge.label && line.progress > 0.5 && (
        <text
          x={(fromNode.x + toNode.x) / 2}
          y={(fromNode.y + toNode.y) / 2 - 10}
          textAnchor="middle"
          fill={color}
          fontSize={16}
          opacity={Math.min(1, (line.progress - 0.5) * 4)}
        >
          {edge.label}
        </text>
      )}
    </>
  );
};

const AnimatedNode = ({
  node, color, textColor, bgColor, enabled, delay,
}: {
  node: LayoutNode; color: string; textColor: string;
  bgColor: string; enabled: boolean; delay: number;
}) => {
  const w = node.width;
  const h = node.height;
  const r = 12;

  const rectPath = `M ${node.x - w / 2 + r} ${node.y - h / 2}
    L ${node.x + w / 2 - r} ${node.y - h / 2}
    Q ${node.x + w / 2} ${node.y - h / 2} ${node.x + w / 2} ${node.y - h / 2 + r}
    L ${node.x + w / 2} ${node.y + h / 2 - r}
    Q ${node.x + w / 2} ${node.y + h / 2} ${node.x + w / 2 - r} ${node.y + h / 2}
    L ${node.x - w / 2 + r} ${node.y + h / 2}
    Q ${node.x - w / 2} ${node.y + h / 2} ${node.x - w / 2} ${node.y + h / 2 - r}
    L ${node.x - w / 2} ${node.y - h / 2 + r}
    Q ${node.x - w / 2} ${node.y - h / 2} ${node.x - w / 2 + r} ${node.y - h / 2} Z`;

  const draw = useDrawOn(rectPath, enabled, delay, 20, "snappy");

  return (
    <>
      <rect
        x={node.x - w / 2}
        y={node.y - h / 2}
        width={w}
        height={h}
        rx={r}
        fill={bgColor}
        opacity={draw.progress * 0.08}
      />
      <path
        d={rectPath}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeOpacity={0.3}
        strokeDasharray={draw.strokeDasharray}
        strokeDashoffset={draw.strokeDashoffset}
      />
      <text
        x={node.x}
        y={node.y + 6}
        textAnchor="middle"
        fill={textColor}
        fontSize={20}
        fontWeight={600}
        opacity={Math.min(1, draw.progress * 2)}
      >
        {node.label}
      </text>
    </>
  );
};

// --- Main component ---

export const DiagramReveal = ({
  props,
  nodes,
  edges,
  width = 900,
  height = 400,
  direction = "vertical",
  delay = 0,
}: {
  props: VideoProps;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  width?: number;
  height?: number;
  /** Layout direction: "vertical" (top-to-bottom) or "horizontal" (left-to-right) */
  direction?: "vertical" | "horizontal";
  delay?: number;
}) => {
  const a = useEntrance(props.enableAnimations, delay, "gentle");

  // Auto-layout or use provided coordinates
  const layoutNodes: LayoutNode[] = needsAutoLayout(nodes)
    ? autoLayout(nodes, edges, width, height, direction)
    : nodes.map((n) => ({
        ...n,
        x: n.x!,
        y: n.y!,
        width: n.width ?? Math.max(120, n.label.length * 16 + 40),
        height: n.height ?? 56,
        layer: 0,
      }));

  const nodeMap = new Map(layoutNodes.map((n) => [n.id, n]));

  return (
    <div style={{
      width: "100%",
      opacity: a.opacity,
      transform: `translateY(${a.translateY}px)`,
    }}>
      <svg
        width="100%"
        viewBox={`0 0 ${width} ${height}`}
        style={{ overflow: "visible" }}
      >
        {edges.map((edge, i) => {
          const fromNode = nodeMap.get(edge.from);
          const toNode = nodeMap.get(edge.to);
          if (!fromNode || !toNode) return null;
          return (
            <AnimatedEdge
              key={`${edge.from}-${edge.to}`}
              fromNode={fromNode}
              toNode={toNode}
              edge={edge}
              color={props.primaryColor}
              enabled={props.enableAnimations}
              delay={staggerDelay(i, delay + 5, 8)}
            />
          );
        })}
        {layoutNodes.map((node, i) => (
          <AnimatedNode
            key={node.id}
            node={node}
            color={props.primaryColor}
            textColor={props.textColor}
            bgColor={props.primaryColor}
            enabled={props.enableAnimations}
            delay={staggerDelay(i, delay, 6)}
          />
        ))}
      </svg>
    </div>
  );
};
