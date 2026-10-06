// Draws a quiz scenario seen from above, from the description the server
// sends (internal/quiz/scene.go). Everything is built with createElementNS:
// no markup from content ever reaches the page.
//
// The grid is 160 x 120, north up. "You" drive up the page on the left, so on
// an ordinary road your lane is centred on x = 66 and the oncoming one on 94.

import type { QuizScene, SceneThing } from "../api";

const NS = "http://www.w3.org/2000/svg";
const W = 160;
const H = 120;

// A scene keeps its own colours in both themes, like a map tile.
const C = {
  ground: "#1c2530",
  block: "#243041",
  pave: "#5d6b7c",
  road: "#39434f",
  shoulder: "#465261",
  line: "#eef2f6",
  yellow: "#f2c94c",
  green: "#3f5d4b",
  hill: "#2f4a3a",
  drop: "#151b23",
  ballast: "#51483a",
  rail: "#cfd6dd",
  me: "#35e0d0",
  car: "#a9bace",
  van: "#c7ced6",
  bus: "#e3b65a",
  truck: "#8fa0b3",
  box: "#d9dfe6",
  glass: "#1d2733",
  white: "#f4f6f8",
  red: "#e5484d",
  amber: "#ffb224",
  skin: "#ffb38a",
  coat: "#ff7eb6",
  ink: "#0e131a",
};

type Attrs = Record<string, string | number>;

function el(tag: string, attrs: Attrs = {}, ...kids: (SVGElement | string)[]): SVGElement {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
  for (const k of kids) e.append(k);
  return e;
}

const rect = (x: number, y: number, w: number, h: number, fill: string, more: Attrs = {}) => el("rect", { x, y, width: w, height: h, fill, ...more });
const line = (x1: number, y1: number, x2: number, y2: number, stroke: string, width: number, more: Attrs = {}) =>
  el("line", { x1, y1, x2, y2, stroke, "stroke-width": width, ...more });
const circle = (cx: number, cy: number, r: number, fill: string, more: Attrs = {}) => el("circle", { cx, cy, r, fill, ...more });

const DASH = { "stroke-dasharray": "6 5" };

// ---------- roads ----------

/** Where the carriageway of the up-and-down road lies. */
function roadSpan(s: QuizScene): [number, number] {
  if (s.road === "bend") return [32, 88];
  return s.road === "straight" && s.narrow ? [60, 100] : [52, 108];
}

function straight(s: QuizScene): SVGElement[] {
  const [x0, x1] = roadSpan(s);
  const out: SVGElement[] = [];
  if (!s.no_sidewalk) out.push(rect(x0 - 10, 0, 10, H, C.pave), rect(x1, 0, 10, H, C.pave));
  out.push(rect(x0, 0, x1 - x0, H, C.road));
  if (s.no_sidewalk) out.push(line(x0 + 2, 0, x0 + 2, H, C.line, 0.8), line(x1 - 2, 0, x1 - 2, H, C.line, 0.8));
  if (!s.narrow) out.push(line(80, 0, 80, H, C.line, 1, DASH));
  return out;
}

function cross(): SVGElement[] {
  const out: SVGElement[] = [];
  // Four corners: pavement round a block.
  for (const [x, y] of [
    [0, 0],
    [108, 0],
    [0, 88],
    [108, 88],
  ]) {
    out.push(rect(x, y, 52, 32, C.pave));
    out.push(rect(x === 0 ? 0 : 118, y === 0 ? 0 : 98, 42, 22, C.block));
  }
  out.push(rect(52, 0, 56, H, C.road), rect(0, 32, W, 56, C.road));
  out.push(line(80, 0, 80, 30, C.line, 1, DASH), line(80, 90, 80, H, C.line, 1, DASH));
  out.push(line(0, 60, 35, 60, C.line, 1, DASH), line(125, 60, W, 60, C.line, 1, DASH));
  // Stop lines, each across the lane that arrives at the junction. The side
  // arms have theirs further out, leaving room for a crosswalk.
  out.push(line(52, 91, 80, 91, C.line, 1.4), line(80, 29, 108, 29, C.line, 1.4));
  out.push(line(35, 32, 35, 60, C.line, 1.4), line(125, 60, 125, 88, C.line, 1.4));
  return out;
}

function rail(s: QuizScene): SVGElement[] {
  const out = straight(s);
  out.push(rect(0, 50, W, 20, C.ballast));
  for (let x = 2; x < W; x += 7) out.push(rect(x, 52, 2.6, 16, "#3b3429"));
  out.push(rect(52, 50, 56, 20, "#4b5563")); // the planked crossing itself
  out.push(line(0, 55, W, 55, C.rail, 1.2), line(0, 65, W, 65, C.rail, 1.2));
  out.push(line(52, 77, 80, 77, C.line, 1.4), line(80, 43, 108, 43, C.line, 1.4));
  // Barriers, raised: a post and its arm standing up beside the road.
  for (const [x, y, up] of [
    [47, 74, -1],
    [113, 46, 1],
  ]) {
    out.push(line(x, y, x, y + up * 13, C.yellow, 1.6, { "stroke-dasharray": "2.4 2.4" }));
    out.push(circle(x, y, 2.2, C.ink, { stroke: C.yellow, "stroke-width": 0.9 }));
  }
  // The crossing sign: a saltire on a post.
  out.push(line(41, 78, 47, 84, C.yellow, 1.3), line(47, 78, 41, 84, C.yellow, 1.3));
  return out;
}

function expressway(ramp: boolean): SVGElement[] {
  const out: SVGElement[] = [];
  out.push(rect(108, 0, 9, H, C.green)); // central reservation
  if (ramp) {
    out.push(el("polygon", { points: "26,120 26,58 52,20 52,120", fill: C.road }));
    out.push(el("polyline", { points: "27.5,120 27.5,58 52,22", fill: "none", stroke: C.line, "stroke-width": 0.8 }));
  } else {
    out.push(rect(44, 0, 8, H, C.shoulder));
  }
  out.push(rect(52, 0, 56, H, C.road));
  out.push(line(107, 0, 107, H, C.line, 0.9));
  out.push(line(80, 0, 80, H, C.line, 1, DASH));
  if (ramp) {
    out.push(line(52, 0, 52, 20, C.line, 0.9));
    out.push(line(52, 20, 52, H, C.line, 1.6, { "stroke-dasharray": "4 3.5" }));
  } else {
    out.push(line(52, 0, 52, H, C.line, 0.9));
  }
  return out;
}

const BEND = "M 60 126 L 60 78 Q 60 30 110 30 L 166 30";

function bend(): SVGElement[] {
  return [
    // The drop on the outside of the bend, the hillside on the inside.
    rect(0, 0, W, H, C.drop),
    rect(84, 54, W - 84, H - 54, C.hill), // the road is painted over its corner
    el("path", { d: BEND, fill: "none", stroke: C.road, "stroke-width": 56 }),
    // The guard rail along the outer edge.
    el("path", { d: "M 31 126 L 31 78 Q 31 1.5 110 1.5 L 166 1.5", fill: "none", stroke: C.rail, "stroke-width": 0.9, "stroke-dasharray": "1.5 2.5" }),
    el("path", { d: BEND, fill: "none", stroke: C.yellow, "stroke-width": 1 }),
  ];
}

// ---------- things ----------

interface Shape {
  hw: number; // half width
  hl: number; // half length
  draw: () => SVGElement[];
}

const body = (hw: number, hl: number, fill: string, rx = 2.6) => rect(-hw, -hl, hw * 2, hl * 2, fill, { rx, stroke: C.ink, "stroke-width": 0.6 });
const glass = (hw: number, y: number, h: number) => rect(-hw, y, hw * 2, h, C.glass, { rx: 0.9 });

const SHAPES: Record<string, Shape> = {
  you: { hw: 6, hl: 11, draw: () => [rect(-6, -11, 12, 22, C.me, { rx: 3, stroke: C.white, "stroke-width": 0.9 }), glass(4.6, -6.5, 4.2), glass(4.4, 5.6, 2.6)] },
  car: { hw: 6, hl: 11, draw: () => [body(6, 11, C.car, 3), glass(4.6, -6.5, 4.2), glass(4.4, 5.6, 2.6)] },
  van: { hw: 6.5, hl: 12.5, draw: () => [body(6.5, 12.5, C.van, 2.2), glass(5, -10.6, 4)] },
  bus: {
    hw: 7,
    hl: 20,
    draw: () => [body(7, 20, C.bus, 2), glass(5.6, -18.4, 3.6), rect(-3.5, -9, 7, 5, "#c99d45", { rx: 0.8 }), rect(-3.5, 4, 7, 5, "#c99d45", { rx: 0.8 })],
  },
  truck: {
    hw: 7,
    hl: 18,
    draw: () => [rect(-7, -8.4, 14, 26.4, C.box, { rx: 1, stroke: C.ink, "stroke-width": 0.6 }), rect(-6.5, -18, 13, 9, C.truck, { rx: 1.6, stroke: C.ink, "stroke-width": 0.6 }), glass(5.2, -16.6, 3.2)],
  },
  ambulance: {
    hw: 6.5,
    hl: 12.5,
    draw: () => [body(6.5, 12.5, C.white, 2.2), glass(5, -10.6, 4), rect(-4.4, -5.6, 8.8, 1.8, C.red, { rx: 0.6 }), rect(-1.1, 0, 2.2, 8, C.red), rect(-4, 2.9, 8, 2.2, C.red)],
  },
  moped: { hw: 2.4, hl: 6.5, draw: () => [rect(-1.3, -6.5, 2.6, 13, C.ink, { rx: 1.2, stroke: C.van, "stroke-width": 0.5 }), circle(0, 0.6, 2.7, C.amber, { stroke: C.ink, "stroke-width": 0.5 })] },
  bicycle: { hw: 2.2, hl: 6, draw: () => [rect(-0.7, -6, 1.4, 12, C.van), line(-2.4, -3.2, 2.4, -3.2, C.van, 0.8), circle(0, 0.6, 2.4, C.coat, { stroke: C.ink, "stroke-width": 0.5 })] },
  person: { hw: 4, hl: 2.4, draw: () => [el("ellipse", { cx: 0, cy: 0, rx: 4, ry: 2.3, fill: C.coat, stroke: C.ink, "stroke-width": 0.5 }), circle(0, 0, 2.1, C.skin)] },
  child: { hw: 3, hl: 1.8, draw: () => [el("ellipse", { cx: 0, cy: 0, rx: 2.9, ry: 1.7, fill: C.amber, stroke: C.ink, "stroke-width": 0.5 }), circle(0, 0, 1.6, C.skin)] },
  elder: {
    hw: 5,
    hl: 2.4,
    draw: () => [line(4.2, -0.4, 5.8, -5, C.white, 0.8), el("ellipse", { cx: 0, cy: 0, rx: 4, ry: 2.3, fill: "#9aa7b6", stroke: C.ink, "stroke-width": 0.5 }), circle(0, 0, 2.1, C.skin)],
  },
  ball: { hw: 2, hl: 2, draw: () => [circle(0, 0, 2, C.red, { stroke: C.white, "stroke-width": 0.6 })] },
  busstop: { hw: 2.4, hl: 2.4, draw: () => [circle(0, 0, 2.4, C.white, { stroke: "#2f6fed", "stroke-width": 1.1 })] },
};

const upright = (heading: number) => {
  const h = ((heading % 180) + 180) % 180;
  return h < 45 || h > 135;
};

let uid = 0;

function label(text: string, x: number, y: number, anchor: string): SVGElement {
  return el("text", { x, y, "text-anchor": anchor, "font-size": 4.6, "font-weight": 600, fill: C.line, stroke: C.ink, "stroke-width": 1.3, "paint-order": "stroke", "stroke-linejoin": "round" }, text);
}

function labelFor(t: SceneThing, hw: number, hl: number): SVGElement | null {
  if (!t.label || !t.at) return null;
  const [x, y] = t.at;
  const up = upright(t.heading ?? 0);
  const dx = (up ? hw : hl) + 2.5;
  const dy = (up ? hl : hw) + 2.5;
  switch (t.label_at ?? "right") {
    case "left":
      return label(t.label, x - dx, y + 1.6, "end");
    case "above":
      return label(t.label, x, y - dy, "middle");
    case "below":
      return label(t.label, x, y + dy + 3.6, "middle");
    default:
      return label(t.label, x + dx, y + 1.6, "start");
  }
}

function crosswalk(t: SceneThing, s: QuizScene): SVGElement[] {
  const [x, y] = t.at!;
  const out: SVGElement[] = [];
  if (upright(t.heading ?? 0)) {
    // Across the up-and-down road: bars side by side along x.
    const [x0, x1] = roadSpan(s);
    for (let bx = x0 + 2.5; bx + 3.5 <= x1 - 1; bx += 7) out.push(rect(bx, y - 5, 3.5, 10, C.line));
  } else {
    // Across the left-and-right road of a junction.
    for (let by = 34.5; by + 3.5 <= 87; by += 7) out.push(rect(x - 5, by, 10, 3.5, C.line));
  }
  return out;
}

function light(t: SceneThing): SVGElement[] {
  const [x, y] = t.at!;
  const lit = t.color ?? "green";
  const lamp = (dx: number, name: string, colour: string) => circle(x + dx, y, 1.9, lit === name ? colour : "#2a3440");
  // Green on the left, as a Japanese signal has it.
  return [rect(x - 8.6, y - 3.2, 17.2, 6.4, C.ink, { rx: 3.2, stroke: C.van, "stroke-width": 0.5 }), lamp(-5.4, "green", "#3ddc97"), lamp(0, "yellow", C.yellow), lamp(5.4, "red", C.red)];
}

function arrow(t: SceneThing, marker: string): SVGElement {
  const p = t.via!;
  let d = `M ${p[0][0]} ${p[0][1]}`;
  if (p.length === 3) d += ` Q ${p[1][0]} ${p[1][1]} ${p[2][0]} ${p[2][1]}`;
  else if (p.length === 4) d += ` C ${p[1][0]} ${p[1][1]} ${p[2][0]} ${p[2][1]} ${p[3][0]} ${p[3][1]}`;
  else d += ` L ${p[1][0]} ${p[1][1]}`;
  return el("path", { d, fill: "none", stroke: C.me, "stroke-width": 1.3, "stroke-dasharray": "3.2 2.4", "stroke-linecap": "round", "marker-end": `url(#${marker})` });
}

function vehicle(t: SceneThing): SVGElement[] {
  const shape = SHAPES[t.is];
  if (!shape || !t.at) return [];
  const { hw, hl } = shape;
  const g = el("g", { transform: `translate(${t.at[0]} ${t.at[1]}) rotate(${t.heading ?? 0})` });
  if (t.lights) g.append(el("polygon", { points: `${-hw + 1},${-hl} ${hw - 1},${-hl} ${hw + 7},${-hl - 22} ${-hw - 7},${-hl - 22}`, fill: "#ffe9a3", opacity: 0.24 }));
  g.append(...shape.draw());
  if (t.blink) {
    const x = t.blink === "left" ? -hw + 0.4 : hw - 0.4;
    g.append(circle(x, -hl + 1.2, 1.5, C.amber), circle(x, hl - 1.2, 1.5, C.amber));
  }
  const text = labelFor(t, hw, hl);
  return text ? [g, text] : [g];
}

// ---------- the picture ----------

export function sceneFigure(s: QuizScene): HTMLElement {
  const id = `sc${++uid}`;
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "The scene seen from above. You are the car marked in cyan, driving up the picture." });
  svg.append(
    el(
      "defs",
      {},
      el("marker", { id: `${id}a`, viewBox: "0 0 8 8", refX: 6.4, refY: 4, markerWidth: 5, markerHeight: 5, orient: "auto-start-reverse" }, el("path", { d: "M 0 0.6 L 8 4 L 0 7.4 Z", fill: C.me })),
      el("pattern", { id: `${id}r`, width: 9, height: 12, patternUnits: "userSpaceOnUse", patternTransform: "rotate(18)" }, line(2, 0, 2, 5, "#bcd3ea", 0.5), line(6.5, 6, 6.5, 11, "#bcd3ea", 0.5)),
      el("clipPath", { id: `${id}c` }, rect(0, 0, W, H, "#000")),
    ),
  );
  const pic = el("g", { "clip-path": `url(#${id}c)` });
  pic.append(rect(0, 0, W, H, C.ground));

  switch (s.road) {
    case "cross":
      pic.append(...cross());
      break;
    case "rail":
      pic.append(...rail(s));
      break;
    case "merge":
      pic.append(...expressway(true));
      break;
    case "expressway":
      pic.append(...expressway(false));
      break;
    case "bend":
      pic.append(...bend());
      break;
    default:
      pic.append(...straight(s));
  }

  // Paint on the road first, then where people mean to go, then the people.
  const things = s.things ?? [];
  for (const t of things) if (t.is === "crosswalk" && t.at) pic.append(...crosswalk(t, s));
  if (s.night) pic.append(rect(0, 0, W, H, "#03060f", { opacity: 0.55 }));
  for (const t of things) if (t.is === "arrow" && t.via) pic.append(arrow(t, `${id}a`));
  const small = (t: SceneThing) => ["person", "child", "elder", "ball", "busstop"].includes(t.is);
  for (const t of things) if (SHAPES[t.is] && !small(t)) pic.append(...vehicle(t));
  for (const t of things) if (small(t)) pic.append(...vehicle(t));
  for (const t of things) if (t.is === "light" && t.at) pic.append(...light(t));
  if (s.rain) pic.append(rect(0, 0, W, H, `url(#${id}r)`, { opacity: 0.55 }));
  for (const t of things) if (t.is === "label" && t.at && t.label) pic.append(label(t.label, t.at[0], t.at[1], "middle"));
  svg.append(pic);

  const fig = document.createElement("figure");
  fig.className = "q-scene";
  fig.append(svg);
  const cap = document.createElement("figcaption");
  const notes = ["Seen from above. You are the cyan car, driving up the picture."];
  if (s.night) notes.push("Night.");
  if (s.rain) notes.push("Raining.");
  cap.textContent = notes.join(" ");
  fig.append(cap);
  return fig;
}
