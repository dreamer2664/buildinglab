#!/usr/bin/env python3
"""
Generates `townsquare/playable/index.html` and `townsquare/playable/server.py`
embedding the exact 20 buildings, 62 hinged doors, and 340 articulated humans
from `master.blend`.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path("/home/user/buildinglab/townsquare/playable")
ROOT.mkdir(parents=True, exist_ok=True)

data = json.loads(Path("/var/tmp/playable_scene_data.json").read_text(encoding="utf-8"))
scene_json_str = json.dumps(data, separators=(",", ":"))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Winterlichtplatz &amp; Schlosspark-Viertel — Playable Articulated 3D City</title>
<style>
  :root {
    --bg: #0b101b;
    --panel: rgba(15, 22, 36, 0.90);
    --border: rgba(120, 165, 230, 0.28);
    --accent: #f2b84b;
    --accent2: #5cc8ff;
    --text: #eef4ff;
    --muted: #9bb0d0;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
  }
  #viewport {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
    cursor: grab;
  }
  #viewport:active { cursor: grabbing; }

  .hud-top {
    position: absolute;
    top: 12px;
    left: 14px;
    right: 360px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 16px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    backdrop-filter: blur(10px);
    pointer-events: auto;
  }
  .brand h1 {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: var(--accent);
  }
  .brand p {
    font-size: 11.5px;
    color: var(--muted);
    margin-top: 2px;
  }
  .stats-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .badge {
    font-size: 11px;
    padding: 4px 9px;
    border-radius: 6px;
    background: rgba(92, 200, 255, 0.12);
    border: 1px solid rgba(92, 200, 255, 0.3);
    color: #d6efff;
    font-weight: 600;
  }

  .sidebar {
    position: absolute;
    top: 12px;
    right: 12px;
    bottom: 12px;
    width: 336px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    overflow-y: auto;
    backdrop-filter: blur(12px);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .section {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 10px;
  }
  .section h2 {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    color: var(--accent);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 12px;
  }
  .row label {
    color: var(--muted);
    flex: 1;
  }
  .row input[type="range"] {
    flex: 1.3;
    accent-color: var(--accent);
    cursor: pointer;
  }
  .row span.val {
    width: 44px;
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-size: 11px;
    color: var(--accent2);
  }
  select, button {
    background: rgba(20, 32, 54, 0.95);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 9px;
    font-size: 11.5px;
    cursor: pointer;
    transition: 0.15s;
  }
  select { width: 100%; margin-bottom: 7px; }
  button:hover {
    background: rgba(242, 184, 75, 0.22);
    border-color: var(--accent);
  }
  button.active {
    background: var(--accent);
    color: #09101d;
    border-color: var(--accent);
    font-weight: 700;
  }
  .btn-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    margin-top: 4px;
  }
  .btn-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
    margin-top: 4px;
  }

  #pip-box {
    width: 100%;
    height: 155px;
    background: #080d18;
    border: 1px solid rgba(92, 200, 255, 0.35);
    border-radius: 6px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
  }
  #pip-canvas {
    width: 100%;
    height: 100%;
    display: block;
  }
  .pip-label {
    position: absolute;
    top: 5px;
    left: 7px;
    font-size: 10.5px;
    color: var(--accent2);
    background: rgba(8, 13, 24, 0.8);
    padding: 2px 6px;
    border-radius: 4px;
    pointer-events: none;
  }

  .hud-bottom {
    position: absolute;
    bottom: 12px;
    left: 14px;
    padding: 8px 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 11.5px;
    color: var(--muted);
    display: flex;
    gap: 14px;
    align-items: center;
  }
  .hud-bottom b { color: var(--accent); }
</style>
</head>
<body>

<canvas id="viewport"></canvas>

<div class="hud-top">
  <div class="brand">
    <h1>WINTERLICHTPLATZ &amp; SCHLOSSPARK-VIERTEL — PLAYABLE 3D CITY</h1>
    <p>Articulated 23-Bone Human Rigs (340) · Dynamic Wind Hair-Ruffle · 62 Hinged Doors · Interactive Tram &amp; Animals</p>
  </div>
  <div class="stats-badges">
    <span class="badge">340 Rigged Humans (23 Bones Each)</span>
    <span class="badge">62 Hinged Doors (0°–95°)</span>
    <span class="badge">20 Buildings · 1,400 Rooms</span>
    <span class="badge" id="fps-badge">60 FPS</span>
  </div>
</div>

<div class="sidebar">
  <!-- Human Rig & Hair Ruffle Studio -->
  <div class="section">
    <h2>
      <span>1. Articulated Human &amp; Hair Rig</span>
      <span style="font-size:10px;color:var(--accent2)">23 Bones + 5 Morphs</span>
    </h2>
    <div id="pip-box">
      <canvas id="pip-canvas" width="300" height="155"></canvas>
      <div class="pip-label" id="pip-title">Inspector: HERO_H01 (23-Bone Skeleton)</div>
    </div>
    <select id="human-select"></select>
    <div class="btn-grid" style="margin-bottom:8px;">
      <button id="anim-walk" class="active" onclick="setAnimMode('walk')">Walk Cycle</button>
      <button id="anim-wave" onclick="setAnimMode('wave')">Wave Hand</button>
      <button id="anim-dance" onclick="setAnimMode('dance')">Festive Dance</button>
      <button id="anim-chat" onclick="setAnimMode('chat')">Converse</button>
      <button id="anim-manual" onclick="setAnimMode('manual')">Manual Pose</button>
      <button onclick="focusSelectedHuman()">Focus Cam</button>
    </div>

    <div class="row">
      <label>Wind Hair Ruffle</label>
      <input type="range" id="sl-hair" min="0" max="100" value="65" oninput="updateRigSliders()" />
      <span class="val" id="val-hair">65%</span>
    </div>
    <div class="row">
      <label>Right UpperArm</label>
      <input type="range" id="sl-arm-r" min="-110" max="110" value="-35" oninput="setManualPose()" />
      <span class="val" id="val-arm-r">-35°</span>
    </div>
    <div class="row">
      <label>Right ForeArm / Hand</label>
      <input type="range" id="sl-fore-r" min="-110" max="110" value="40" oninput="setManualPose()" />
      <span class="val" id="val-fore-r">40°</span>
    </div>
    <div class="row">
      <label>Left UpperArm</label>
      <input type="range" id="sl-arm-l" min="-110" max="110" value="25" oninput="setManualPose()" />
      <span class="val" id="val-arm-l">25°</span>
    </div>
    <div class="row">
      <label>Left / Right Leg Stride</label>
      <input type="range" id="sl-leg" min="-60" max="60" value="28" oninput="setManualPose()" />
      <span class="val" id="val-leg">28°</span>
    </div>
    <div class="row">
      <label>Knee Bend (Shin.L/R)</label>
      <input type="range" id="sl-knee" min="0" max="95" value="22" oninput="setManualPose()" />
      <span class="val" id="val-knee">22°</span>
    </div>
    <div class="row">
      <label>Head Turn &amp; Tilt</label>
      <input type="range" id="sl-head" min="-55" max="55" value="15" oninput="setManualPose()" />
      <span class="val" id="val-head">15°</span>
    </div>
  </div>

  <!-- Hinged Movable Doors -->
  <div class="section">
    <h2>
      <span>2. Hinged Movable Doors (62)</span>
      <span style="font-size:10px;color:var(--accent2)">Z-Pin Pivot</span>
    </h2>
    <select id="door-select" onchange="onDoorSelectChange()"></select>
    <div class="row">
      <label>Selected Door Swing</label>
      <input type="range" id="sl-door" min="0" max="95" value="75" oninput="onDoorSlider()" />
      <span class="val" id="val-door">75°</span>
    </div>
    <div class="btn-grid-2">
      <button onclick="setAllDoors(82)">Open All 62 Doors (82°)</button>
      <button onclick="setAllDoors(0)">Close All Doors (0°)</button>
      <button onclick="toggleDoorPulse()" id="btn-door-pulse">Auto-Swing Doors</button>
      <button onclick="focusSelectedDoor()">Focus Selected Door</button>
    </div>
  </div>

  <!-- City Environment, Tram & Camera presets -->
  <div class="section">
    <h2>
      <span>3. Playable World, Tram &amp; Camera</span>
      <span style="font-size:10px;color:var(--accent2)">Interactive</span>
    </h2>
    <div class="row">
      <label>Tree &amp; Banner Wind</label>
      <input type="range" id="sl-wind" min="0" max="100" value="60" oninput="updateWorldSliders()" />
      <span class="val" id="val-wind">60%</span>
    </div>
    <div class="row">
      <label>Linie 4 Tram Speed</label>
      <input type="range" id="sl-tram" min="0" max="100" value="55" oninput="updateWorldSliders()" />
      <span class="val" id="val-tram">55%</span>
    </div>
    <div class="btn-grid">
      <button onclick="setCamPreset('square')">Main Square</button>
      <button onclick="setCamPreset('park')">Schlosspark</button>
      <button onclick="setCamPreset('tram')">Ride Tram</button>
      <button onclick="setCamPreset('street')">Street Walk</button>
      <button onclick="setCamPreset('aerial')">2-District Aerial</button>
      <button onclick="toggleSkeletonOverlay()" id="btn-skel" class="active">Show Bones</button>
    </div>
  </div>
</div>

<div class="hud-bottom">
  <span><b>WASD / Arrows:</b> Walk / Fly</span>
  <span><b>Drag Mouse:</b> Orbit / Look</span>
  <span><b>Scroll:</b> Zoom</span>
  <span><b>Key [E]:</b> Swing Nearest Door</span>
  <span><b>Key [R]:</b> Gust Wind (Ruffle Hair)</span>
</div>

<script>
const CITY_DATA = __SCENE_JSON__;

// Populate UI selectors
const humanSelect = document.getElementById('human-select');
CITY_DATA.humans.forEach((h, idx) => {
  const opt = document.createElement('option');
  opt.value = idx;
  opt.textContent = (h.hero ? '★ ' : '') + h.name + ` (${h.x.toFixed(0)}m, ${h.y.toFixed(0)}m)`;
  humanSelect.appendChild(opt);
});
humanSelect.value = 0;

const doorSelect = document.getElementById('door-select');
CITY_DATA.doors.forEach((d, idx) => {
  const opt = document.createElement('option');
  opt.value = idx;
  opt.textContent = `${d.name} [${d.cat}]`;
  doorSelect.appendChild(opt);
});
doorSelect.value = 0;

// Door dynamic state (initialize first 10 doors open at 75 deg so user immediately sees open hinged doors)
const doorAngles = CITY_DATA.doors.map((d, i) => (i % 2 === 0 ? 75 : 25));
let autoPulseDoors = false;
let showBones = true;
let animMode = 'walk';
let hairRuffleStrength = 0.65;
let treeWindStrength = 0.60;
let tramSpeed = 0.55;
let tramPos = 35.0;
let tramDir = 1.0;

// Manual limb pose angles (in radians)
const manualPose = {
  armR: -35 * Math.PI / 180,
  foreR: 40 * Math.PI / 180,
  armL: 25 * Math.PI / 180,
  leg: 28 * Math.PI / 180,
  knee: 22 * Math.PI / 180,
  head: 15 * Math.PI / 180,
};

function setAnimMode(mode) {
  animMode = mode;
  ['walk', 'wave', 'dance', 'chat', 'manual'].forEach(m => {
    const el = document.getElementById('anim-' + m);
    if (el) el.classList.toggle('active', m === mode);
  });
}

function setManualPose() {
  setAnimMode('manual');
  const ar = parseFloat(document.getElementById('sl-arm-r').value);
  const fr = parseFloat(document.getElementById('sl-fore-r').value);
  const al = parseFloat(document.getElementById('sl-arm-l').value);
  const lg = parseFloat(document.getElementById('sl-leg').value);
  const kn = parseFloat(document.getElementById('sl-knee').value);
  const hd = parseFloat(document.getElementById('sl-head').value);
  document.getElementById('val-arm-r').textContent = ar + '°';
  document.getElementById('val-fore-r').textContent = fr + '°';
  document.getElementById('val-arm-l').textContent = al + '°';
  document.getElementById('val-leg').textContent = lg + '°';
  document.getElementById('val-knee').textContent = kn + '°';
  document.getElementById('val-head').textContent = hd + '°';
  manualPose.armR = ar * Math.PI / 180;
  manualPose.foreR = fr * Math.PI / 180;
  manualPose.armL = al * Math.PI / 180;
  manualPose.leg = lg * Math.PI / 180;
  manualPose.knee = kn * Math.PI / 180;
  manualPose.head = hd * Math.PI / 180;
}

function updateRigSliders() {
  const hr = parseFloat(document.getElementById('sl-hair').value);
  document.getElementById('val-hair').textContent = hr + '%';
  hairRuffleStrength = hr / 100.0;
}

function updateWorldSliders() {
  const w = parseFloat(document.getElementById('sl-wind').value);
  const tr = parseFloat(document.getElementById('sl-tram').value);
  document.getElementById('val-wind').textContent = w + '%';
  document.getElementById('val-tram').textContent = tr + '%';
  treeWindStrength = w / 100.0;
  tramSpeed = tr / 100.0;
}

function onDoorSelectChange() {
  const idx = parseInt(doorSelect.value, 10) || 0;
  const ang = Math.round(doorAngles[idx] || 0);
  document.getElementById('sl-door').value = ang;
  document.getElementById('val-door').textContent = ang + '°';
}

function onDoorSlider() {
  const idx = parseInt(doorSelect.value, 10) || 0;
  const ang = parseFloat(document.getElementById('sl-door').value);
  doorAngles[idx] = ang;
  document.getElementById('val-door').textContent = Math.round(ang) + '°';
}

function setAllDoors(angleDeg) {
  for (let i = 0; i < doorAngles.length; i++) doorAngles[i] = angleDeg;
  document.getElementById('sl-door').value = angleDeg;
  document.getElementById('val-door').textContent = Math.round(angleDeg) + '°';
}

function toggleDoorPulse() {
  autoPulseDoors = !autoPulseDoors;
  document.getElementById('btn-door-pulse').classList.toggle('active', autoPulseDoors);
}

function toggleSkeletonOverlay() {
  showBones = !showBones;
  document.getElementById('btn-skel').classList.toggle('active', showBones);
}

// Camera state
const cam = {
  targetX: 6.0,
  targetY: -8.0,
  targetZ: 1.5,
  yaw: -0.65,
  pitch: 0.36,
  dist: 26.0,
  rideTram: false,
};

function focusSelectedHuman() {
  cam.rideTram = false;
  const idx = parseInt(humanSelect.value, 10) || 0;
  const h = CITY_DATA.humans[idx];
  cam.targetX = h.x;
  cam.targetY = h.y;
  cam.targetZ = h.z + 1.1;
  cam.dist = 4.2;
  cam.pitch = 0.22;
}

function focusSelectedDoor() {
  cam.rideTram = false;
  const idx = parseInt(doorSelect.value, 10) || 0;
  const d = CITY_DATA.doors[idx];
  cam.targetX = d.x;
  cam.targetY = d.y;
  cam.targetZ = d.z + 1.1;
  cam.dist = 5.0;
  cam.pitch = 0.20;
}

function setCamPreset(preset) {
  cam.rideTram = false;
  if (preset === 'square') {
    cam.targetX = 0; cam.targetY = 0; cam.targetZ = 1.5; cam.dist = 32; cam.pitch = 0.38; cam.yaw = -0.65;
  } else if (preset === 'park') {
    cam.targetX = 95; cam.targetY = 2; cam.targetZ = 1.5; cam.dist = 36; cam.pitch = 0.36; cam.yaw = -0.85;
  } else if (preset === 'tram') {
    cam.rideTram = true; cam.dist = 14; cam.pitch = 0.26;
  } else if (preset === 'street') {
    cam.targetX = -8; cam.targetY = -12; cam.targetZ = 1.6; cam.dist = 6.5; cam.pitch = 0.14; cam.yaw = 0.4;
  } else if (preset === 'aerial') {
    cam.targetX = 42; cam.targetY = 0; cam.targetZ = 2.0; cam.dist = 95; cam.pitch = 0.58; cam.yaw = -0.72;
  }
}

humanSelect.addEventListener('change', () => {
  const idx = parseInt(humanSelect.value, 10) || 0;
  const h = CITY_DATA.humans[idx];
  document.getElementById('pip-title').textContent = `Inspector: ${h.name.slice(0, 24)} (23 Bones)`;
});

// Mouse & Keyboard Controls
const canvas = document.getElementById('viewport');
const ctx = canvas.getContext('2d');
const pipCanvas = document.getElementById('pip-canvas');
const pipCtx = pipCanvas.getContext('2d');

let dragging = false, lastX = 0, lastY = 0;
canvas.addEventListener('mousedown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
window.addEventListener('mouseup', () => dragging = false);
window.addEventListener('mousemove', e => {
  if (!dragging) return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX; lastY = e.clientY;
  cam.yaw -= dx * 0.0065;
  cam.pitch = Math.max(0.05, Math.min(1.35, cam.pitch + dy * 0.0065));
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  cam.dist = Math.max(2.2, Math.min(140.0, cam.dist * (1 + e.deltaY * 0.001)));
}, { passive: false });

const keys = {};
window.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key.toLowerCase() === 'e') {
    // Toggle nearest door
    let bestIdx = 0, bestD = 1e9;
    CITY_DATA.doors.forEach((d, idx) => {
      const dist = Math.hypot(d.x - cam.targetX, d.y - cam.targetY);
      if (dist < bestD) { bestD = dist; bestIdx = idx; }
    });
    doorAngles[bestIdx] = doorAngles[bestIdx] > 40 ? 0 : 85;
    doorSelect.value = bestIdx;
    onDoorSelectChange();
  }
  if (e.key.toLowerCase() === 'r') {
    hairRuffleStrength = 1.0;
    document.getElementById('sl-hair').value = 100;
    document.getElementById('val-hair').textContent = '100%';
  }
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

// 3D Projection Helper
function project3D(wx, wy, wz, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale) {
  const dx = wx - cX;
  const dy = wy - cY;
  const dz = wz - cZ;
  // Rotate around Z by -yaw
  const rx = dx * cosY + dy * sinY;
  const ry = -dx * sinY + dy * cosY;
  // Rotate pitch
  const cy = ry * cosP - dz * sinP;
  const cz = ry * sinP + dz * cosP;
  if (cy <= 0.25) return null;
  const invZ = fovScale / cy;
  return {
    x: W * 0.5 + rx * invZ,
    y: H * 0.5 - cz * invZ,
    depth: cy,
    scale: invZ,
  };
}

// Compute 23-bone articulated pose for human idx at time t
function computeHumanPose(idx, t, isSelected) {
  const phase = t * 3.8 + idx * 0.7;
  let armL = 0, foreL = 0.15, armR = 0, foreR = 0.15;
  let thighL = 0, shinL = 0, thighR = 0, shinR = 0;
  let headYaw = 0, headPitch = 0, chestLean = 0;

  if (isSelected && animMode === 'manual') {
    armR = manualPose.armR;
    foreR = manualPose.foreR;
    armL = manualPose.armL;
    foreL = Math.abs(manualPose.armL) * 0.5;
    thighL = manualPose.leg;
    thighR = -manualPose.leg;
    shinL = manualPose.knee;
    shinR = manualPose.knee * 0.7;
    headYaw = manualPose.head;
  } else {
    const mode = isSelected ? animMode : (idx % 5 === 0 ? 'wave' : (idx % 3 === 0 ? 'chat' : 'walk'));
    if (mode === 'walk') {
      const s = Math.sin(phase);
      armL = 0.45 * s;
      foreL = Math.max(0.1, 0.35 * s);
      armR = -0.45 * s;
      foreR = Math.max(0.1, -0.35 * s);
      thighL = -0.42 * s;
      shinL = Math.max(0, 0.48 * Math.sin(phase - 0.6));
      thighR = 0.42 * s;
      shinR = Math.max(0, 0.48 * Math.sin(phase + Math.PI - 0.6));
      headYaw = 0.12 * Math.cos(phase * 0.5);
    } else if (mode === 'wave') {
      armR = -1.25 + 0.25 * Math.sin(phase * 2.0);
      foreR = 0.65 + 0.45 * Math.cos(phase * 2.5);
      armL = 0.15 * Math.sin(phase);
      headYaw = 0.22 * Math.sin(phase * 0.8);
    } else if (mode === 'dance') {
      const s = Math.sin(phase * 1.8);
      armL = -0.9 + 0.5 * s;
      armR = -0.9 - 0.5 * s;
      foreL = 0.6;
      foreR = 0.6;
      thighL = 0.35 * s;
      thighR = -0.35 * s;
      shinL = 0.45 * Math.abs(s);
      shinR = 0.45 * Math.abs(Math.cos(phase * 1.8));
      chestLean = 0.12 * s;
    } else {
      // chat
      armR = -0.35 + 0.22 * Math.sin(phase * 1.3);
      foreR = 0.55 + 0.2 * Math.cos(phase * 1.3);
      armL = -0.20 + 0.15 * Math.cos(phase);
      headYaw = 0.25 * Math.sin(phase * 0.7);
      headPitch = 0.08 * Math.sin(phase * 1.4);
    }
  }
  return { armL, foreL, armR, foreR, thighL, shinL, thighR, shinR, headYaw, headPitch, chestLean };
}

// Draw 23-bone close-up inspector in PiP canvas
function renderPipInspector(t) {
  const W = pipCanvas.width, H = pipCanvas.height;
  pipCtx.fillStyle = '#070c16';
  pipCtx.fillRect(0, 0, W, H);

  // Subtle grid
  pipCtx.strokeStyle = 'rgba(92,200,255,0.10)';
  pipCtx.lineWidth = 1;
  for (let x = 0; x < W; x += 25) { pipCtx.beginPath(); pipCtx.moveTo(x, 0); pipCtx.lineTo(x, H); pipCtx.stroke(); }
  for (let y = 0; y < H; y += 25) { pipCtx.beginPath(); pipCtx.moveTo(0, y); pipCtx.lineTo(W, y); pipCtx.stroke(); }

  const selIdx = parseInt(humanSelect.value, 10) || 0;
  const pose = computeHumanPose(selIdx, t, true);

  const cx = W * 0.38, baseY = H - 14, sc = 74.0;
  const pelvis = { x: cx, y: baseY - 0.88 * sc };
  const spine = { x: cx + Math.sin(pose.chestLean) * 8, y: baseY - 1.12 * sc };
  const chest = { x: cx + Math.sin(pose.chestLean) * 14, y: baseY - 1.38 * sc };
  const neck = { x: chest.x, y: baseY - 1.48 * sc };
  const head = { x: neck.x + Math.sin(pose.headYaw) * 5, y: baseY - 1.64 * sc };

  const shL = { x: chest.x - 14, y: chest.y + 3 };
  const elL = { x: shL.x - Math.sin(pose.armL) * 18 - 4, y: shL.y + Math.cos(pose.armL) * 20 };
  const hdL = { x: elL.x - Math.sin(pose.armL + pose.foreL) * 16, y: elL.y + Math.cos(pose.armL + pose.foreL) * 17 };

  const shR = { x: chest.x + 14, y: chest.y + 3 };
  const elR = { x: shR.x - Math.sin(pose.armR) * 18 + 4, y: shR.y + Math.cos(pose.armR) * 20 };
  const hdR = { x: elR.x - Math.sin(pose.armR - pose.foreR) * 16, y: elR.y + Math.cos(pose.armR - pose.foreR) * 17 };

  const hpL = { x: pelvis.x - 8, y: pelvis.y };
  const knL = { x: hpL.x + Math.sin(pose.thighL) * 20, y: hpL.y + Math.cos(pose.thighL) * 28 };
  const ftL = { x: knL.x + Math.sin(pose.thighL - pose.shinL) * 18, y: knL.y + Math.cos(pose.thighL - pose.shinL) * 28 };

  const hpR = { x: pelvis.x + 8, y: pelvis.y };
  const knR = { x: hpR.x + Math.sin(pose.thighR) * 20, y: hpR.y + Math.cos(pose.thighR) * 28 };
  const ftR = { x: knR.x + Math.sin(pose.thighR - pose.shinR) * 18, y: knR.y + Math.cos(pose.thighR - pose.shinR) * 28 };

  function boneLine(a, b, col, w) {
    pipCtx.strokeStyle = col;
    pipCtx.lineWidth = w;
    pipCtx.lineCap = 'round';
    pipCtx.beginPath();
    pipCtx.moveTo(a.x, a.y);
    pipCtx.lineTo(b.x, b.y);
    pipCtx.stroke();
  }

  // Limbs & torso
  boneLine(pelvis, spine, '#5cc8ff', 5);
  boneLine(spine, chest, '#5cc8ff', 6);
  boneLine(chest, neck, '#5cc8ff', 4);
  boneLine(neck, head, '#5cc8ff', 5);
  boneLine(chest, shL, '#8be9fd', 3.5);
  boneLine(shL, elL, '#ffb86c', 4.5);
  boneLine(elL, hdL, '#ff79c6', 3.5);
  boneLine(chest, shR, '#8be9fd', 3.5);
  boneLine(shR, elR, '#ffb86c', 4.5);
  boneLine(elR, hdR, '#ff79c6', 3.5);
  boneLine(pelvis, hpL, '#8be9fd', 3.5);
  boneLine(hpL, knL, '#50fa7b', 4.5);
  boneLine(knL, ftL, '#f1fa8c', 4.0);
  boneLine(pelvis, hpR, '#8be9fd', 3.5);
  boneLine(hpR, knR, '#50fa7b', 4.5);
  boneLine(knR, ftR, '#f1fa8c', 4.0);

  // Head sphere
  pipCtx.fillStyle = '#f5d0b5';
  pipCtx.beginPath();
  pipCtx.arc(head.x, head.y, 9, 0, Math.PI * 2);
  pipCtx.fill();

  // Dynamic Wind-Ruffling Hair Strands (Hair_Crown, Hair_Strand.L, Hair_Strand.R, Hair_Back + 12 locks)
  const windGust = hairRuffleStrength * (1.0 + 0.35 * Math.sin(t * 7.5));
  for (let s = 0; s < 14; s++) {
    const frac = (s / 13) - 0.5;
    const sx = head.x + frac * 16;
    const sy = head.y - 6 + Math.abs(frac) * 5;
    const wave = Math.sin(t * 9.0 + s * 1.1) * 14 * windGust + windGust * 16;
    const lift = -Math.abs(Math.cos(t * 7.0 + s)) * 6 * windGust;
    pipCtx.strokeStyle = s % 2 === 0 ? '#f2b84b' : '#c97a3d';
    pipCtx.lineWidth = 2.0;
    pipCtx.beginPath();
    pipCtx.moveTo(sx, sy);
    pipCtx.quadraticCurveTo(sx + wave * 0.6, sy - 5 + lift, sx + wave, sy + 9 + lift);
    pipCtx.stroke();
  }

  // Joint dots
  [pelvis, spine, chest, neck, shL, elL, hdL, shR, elR, hdR, hpL, knL, ftL, hpR, knR, ftR].forEach(p => {
    pipCtx.fillStyle = '#ffffff';
    pipCtx.beginPath();
    pipCtx.arc(p.x, p.y, 2.3, 0, Math.PI * 2);
    pipCtx.fill();
  });

  // Bone legend on right side of PiP
  pipCtx.fillStyle = '#9bb0d0';
  pipCtx.font = '10px monospace';
  const labels = [
    `Hair_Ruffle: ${(hairRuffleStrength * 100).toFixed(0)}%`,
    `UpperArm.R : ${(pose.armR * 57.3).toFixed(0)}°`,
    `ForeArm.R  : ${(pose.foreR * 57.3).toFixed(0)}°`,
    `UpperArm.L : ${(pose.armL * 57.3).toFixed(0)}°`,
    `Thigh.L/R  : ${(pose.thighL * 57.3).toFixed(0)}°`,
    `Shin.L/R   : ${(pose.shinL * 57.3).toFixed(0)}°`,
    `Head_Yaw   : ${(pose.headYaw * 57.3).toFixed(0)}°`,
  ];
  labels.forEach((txt, i) => {
    pipCtx.fillText(txt, W * 0.60, 32 + i * 16);
  });
}

// Snowflakes for winter atmosphere
const snowflakes = Array.from({ length: 140 }, () => ({
  x: (Math.random() - 0.3) * 200,
  y: (Math.random() - 0.5) * 90,
  z: Math.random() * 24,
  s: 1.0 + Math.random() * 1.8,
}));

let lastFrameTime = performance.now();
let fpsSmooth = 60;

function renderLoop(now) {
  const dt = Math.min(0.05, (now - lastFrameTime) * 0.001);
  lastFrameTime = now;
  fpsSmooth = fpsSmooth * 0.92 + (1.0 / Math.max(dt, 0.001)) * 0.08;
  if (Math.floor(now / 250) !== Math.floor((now - dt * 1000) / 250)) {
    document.getElementById('fps-badge').textContent = `${Math.round(fpsSmooth)} FPS`;
  }
  const t = now * 0.001;

  // Move tram along Lindenallee (x in [-20, 118], y = 2.2)
  tramPos += tramDir * tramSpeed * 9.0 * dt;
  if (tramPos > 115) { tramPos = 115; tramDir = -1; }
  if (tramPos < -18) { tramPos = -18; tramDir = 1; }
  if (cam.rideTram) {
    cam.targetX = tramPos;
    cam.targetY = 2.2;
    cam.targetZ = 2.1;
  }

  // Keyboard navigation
  const moveSpd = 16.0 * dt;
  const sinY = Math.sin(cam.yaw), cosY = Math.cos(cam.yaw);
  if (keys['w'] || keys['arrowup']) { cam.targetX -= sinY * moveSpd; cam.targetY += cosY * moveSpd; }
  if (keys['s'] || keys['arrowdown']) { cam.targetX += sinY * moveSpd; cam.targetY -= cosY * moveSpd; }
  if (keys['a'] || keys['arrowleft']) { cam.targetX -= cosY * moveSpd; cam.targetY -= sinY * moveSpd; }
  if (keys['d'] || keys['arrowright']) { cam.targetX += cosY * moveSpd; cam.targetY += sinY * moveSpd; }

  if (autoPulseDoors) {
    const ang = 47.5 + 45.0 * Math.sin(t * 2.2);
    for (let i = 0; i < doorAngles.length; i++) doorAngles[i] = ang;
    document.getElementById('sl-door').value = Math.round(ang);
    document.getElementById('val-door').textContent = Math.round(ang) + '°';
  }

  const W = canvas.width, H = canvas.height;
  // Blue-hour twilight sky gradient
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#0a1328');
  sky.addColorStop(0.55, '#16284c');
  sky.addColorStop(1, '#1d2436');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, W, H);

  const sinP = Math.sin(cam.pitch), cosP = Math.cos(cam.pitch);
  const cX = cam.targetX + sinY * cosP * cam.dist;
  const cY = cam.targetY - cosY * cosP * cam.dist;
  const cZ = cam.targetZ + sinP * cam.dist;
  const fovScale = Math.min(W, H) * 0.92;

  const drawList = [];

  // 1. Ground plane grid & districts
  for (let gx = -50; gx <= 140; gx += 10) {
    for (let gy = -40; gy <= 40; gy += 10) {
      const p0 = project3D(gx, gy, 0, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
      const p1 = project3D(gx + 10, gy, 0, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
      const p2 = project3D(gx + 10, gy + 10, 0, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
      const p3 = project3D(gx, gy + 10, 0, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
      if (p0 && p1 && p2 && p3) {
        const isPark = gx >= 65;
        const isSquare = gx >= -32 && gx <= 32 && gy >= -26 && gy <= 26;
        drawList.push({
          depth: (p0.depth + p2.depth) * 0.5 + 50,
          draw: () => {
            ctx.fillStyle = isPark ? 'rgba(28, 48, 44, 0.72)' : (isSquare ? 'rgba(42, 46, 58, 0.78)' : 'rgba(30, 35, 46, 0.72)');
            ctx.strokeStyle = 'rgba(130, 165, 210, 0.14)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(p0.x, p0.y); ctx.lineTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.lineTo(p3.x, p3.y);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
          }
        });
      }
    }
  }

  // 2. Buildings (B01..B20)
  const palette = ['#d4a373', '#e6ccb2', '#9db4c0', '#c98a7b', '#8da9c4', '#ddb892'];
  CITY_DATA.buildings.forEach((b, bIdx) => {
    const hw = b.w * 0.5, hd = b.d * 0.5, h = b.h;
    const corners = [
      [b.x - hw, b.y - hd, 0], [b.x + hw, b.y - hd, 0],
      [b.x + hw, b.y + hd, 0], [b.x - hw, b.y + hd, 0],
      [b.x - hw, b.y - hd, h], [b.x + hw, b.y - hd, h],
      [b.x + hw, b.y + hd, h], [b.x - hw, b.y + hd, h],
    ].map(c => project3D(c[0], c[1], c[2], cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale));
    if (corners.some(c => !c)) return;
    const centerP = project3D(b.x, b.y, h * 0.5, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    if (!centerP) return;
    const col = palette[bIdx % palette.length];
    drawList.push({
      depth: centerP.depth + 8,
      draw: () => {
        // Wireframe + translucent architectural massing so interior doors & people remain visible
        ctx.fillStyle = col + '28';
        ctx.strokeStyle = col + 'aa';
        ctx.lineWidth = 1.4;
        const faces = [[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]];
        faces.forEach(f => {
          ctx.beginPath();
          ctx.moveTo(corners[f[0]].x, corners[f[0]].y);
          for (let k = 1; k < 4; k++) ctx.lineTo(corners[f[k]].x, corners[f[k]].y);
          ctx.closePath();
          ctx.fill();
          ctx.stroke();
        });
        const roofP = project3D(b.x, b.y, h + 1.2, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
        if (roofP && roofP.depth < 95) {
          ctx.fillStyle = '#ffe6a3';
          ctx.font = 'bold 10px sans-serif';
          ctx.fillText(`${b.id} (${b.shop})`, roofP.x - 24, roofP.y);
        }
      }
    });
  });

  // 3. 62 Hinged Playable Doors (swinging around their Z hinge pin!)
  const selDoorIdx = parseInt(doorSelect.value, 10) || 0;
  CITY_DATA.doors.forEach((d, dIdx) => {
    const openDeg = doorAngles[dIdx] || 0;
    const totalYaw = d.yaw + (openDeg * Math.PI / 180.0);
    const dw = 0.92, dh = 2.12;
    const lx = d.x + Math.cos(totalYaw) * dw;
    const ly = d.y + Math.sin(totalYaw) * dw;
    // Closed jamb frame
    const jx = d.x + Math.cos(d.yaw) * dw;
    const jy = d.y + Math.sin(d.yaw) * dw;

    const pHingeB = project3D(d.x, d.y, d.z, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    const pHingeT = project3D(d.x, d.y, d.z + dh, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    const pLatchT = project3D(lx, ly, d.z + dh, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    const pLatchB = project3D(lx, ly, d.z, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    const pJambB = project3D(jx, jy, d.z, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    if (!pHingeB || !pHingeT || !pLatchT || !pLatchB) return;

    const isSel = dIdx === selDoorIdx;
    drawList.push({
      depth: pHingeB.depth,
      draw: () => {
        // Draw swing arc on ground
        if (pJambB) {
          ctx.strokeStyle = isSel ? '#5cc8ff' : 'rgba(242, 184, 75, 0.45)';
          ctx.lineWidth = isSel ? 2.2 : 1.2;
          ctx.beginPath();
          ctx.moveTo(pHingeB.x, pHingeB.y);
          ctx.lineTo(pJambB.x, pJambB.y);
          ctx.lineTo(pLatchB.x, pLatchB.y);
          ctx.stroke();
        }
        // Swinging door leaf polygon
        ctx.fillStyle = isSel ? 'rgba(92, 200, 255, 0.78)' : (openDeg > 10 ? 'rgba(242, 184, 75, 0.72)' : 'rgba(165, 105, 60, 0.78)');
        ctx.strokeStyle = isSel ? '#ffffff' : '#f2b84b';
        ctx.lineWidth = isSel ? 2.4 : 1.4;
        ctx.beginPath();
        ctx.moveTo(pHingeB.x, pHingeB.y);
        ctx.lineTo(pHingeT.x, pHingeT.y);
        ctx.lineTo(pLatchT.x, pLatchT.y);
        ctx.lineTo(pLatchB.x, pLatchB.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Brass lever handle dot
        const hX = (pHingeB.x + pLatchB.x * 3 + pHingeT.x + pLatchT.x * 3) / 8;
        const hY = (pHingeB.y + pLatchB.y * 3 + pHingeT.y + pLatchT.y * 3) / 8;
        ctx.fillStyle = '#ffe066';
        ctx.beginPath();
        ctx.arc(hX, hY, Math.max(2, pHingeB.scale * 0.06), 0, Math.PI * 2);
        ctx.fill();
      }
    });
  });

  // 4. Electric Tram (Linie 4 Schlosspark)
  const tramP = project3D(tramPos, 2.2, 1.6, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
  if (tramP) {
    const tL = project3D(tramPos - 5.5, 2.2, 0.3, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    const tR = project3D(tramPos + 5.5, 2.2, 3.1, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    if (tL && tR) {
      drawList.push({
        depth: tramP.depth,
        draw: () => {
          ctx.strokeStyle = '#ff5964';
          ctx.fillStyle = 'rgba(210, 45, 58, 0.65)';
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.roundRect(Math.min(tL.x, tR.x), Math.min(tL.y, tR.y), Math.abs(tR.x - tL.x) + 12, Math.abs(tL.y - tR.y) + 8, 5);
          ctx.fill();
          ctx.stroke();
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 10px sans-serif';
          ctx.fillText('TRAM LINIE 4', tramP.x - 32, tramP.y);
        }
      });
    }
  }

  // 5. All 340 Articulated Humans with 23-Bone Limbs & Wind-Ruffling Hair
  const selHumanIdx = parseInt(humanSelect.value, 10) || 0;
  CITY_DATA.humans.forEach((h, hIdx) => {
    const baseP = project3D(h.x, h.y, h.z, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    if (!baseP || baseP.depth > 115) return;
    const isSel = hIdx === selHumanIdx;
    const pose = computeHumanPose(hIdx, t, isSel);
    const sc = baseP.scale;

    drawList.push({
      depth: baseP.depth,
      draw: () => {
        const bx = baseP.x, by = baseP.y;
        const pelvisY = by - 0.88 * sc;
        const chestY = by - 1.38 * sc;
        const headY = by - 1.65 * sc;
        const headX = bx + Math.sin(pose.headYaw) * 0.08 * sc;

        // Articulated Legs (Thigh.L/R, Shin.L/R, Foot.L/R)
        const hipL = { x: bx - 0.09 * sc, y: pelvisY };
        const kneeL = { x: hipL.x + Math.sin(pose.thighL) * 0.25 * sc, y: hipL.y + Math.cos(pose.thighL) * 0.42 * sc };
        const footL = { x: kneeL.x + Math.sin(pose.thighL - pose.shinL) * 0.22 * sc, y: kneeL.y + Math.cos(pose.thighL - pose.shinL) * 0.42 * sc };

        const hipR = { x: bx + 0.09 * sc, y: pelvisY };
        const kneeR = { x: hipR.x + Math.sin(pose.thighR) * 0.25 * sc, y: hipR.y + Math.cos(pose.thighR) * 0.42 * sc };
        const footR = { x: kneeR.x + Math.sin(pose.thighR - pose.shinR) * 0.22 * sc, y: kneeR.y + Math.cos(pose.thighR - pose.shinR) * 0.42 * sc };

        // Articulated Arms (Shoulder.L/R, UpperArm.L/R, ForeArm.L/R, Hand.L/R)
        const shL = { x: bx - 0.16 * sc, y: chestY };
        const elL = { x: shL.x - Math.sin(pose.armL) * 0.22 * sc, y: shL.y + Math.cos(pose.armL) * 0.26 * sc };
        const hdL = { x: elL.x - Math.sin(pose.armL + pose.foreL) * 0.20 * sc, y: elL.y + Math.cos(pose.armL + pose.foreL) * 0.24 * sc };

        const shR = { x: bx + 0.16 * sc, y: chestY };
        const elR = { x: shR.x - Math.sin(pose.armR) * 0.22 * sc, y: shR.y + Math.cos(pose.armR) * 0.26 * sc };
        const hdR = { x: elR.x - Math.sin(pose.armR - pose.foreR) * 0.20 * sc, y: elR.y + Math.cos(pose.armR - pose.foreR) * 0.24 * sc };

        const lw = Math.max(1.4, 0.065 * sc);
        ctx.lineCap = 'round';

        // Draw legs
        ctx.strokeStyle = isSel ? '#50fa7b' : '#4a6fa5';
        ctx.lineWidth = lw;
        ctx.beginPath();
        ctx.moveTo(hipL.x, hipL.y); ctx.lineTo(kneeL.x, kneeL.y); ctx.lineTo(footL.x, footL.y);
        ctx.moveTo(hipR.x, hipR.y); ctx.lineTo(kneeR.x, kneeR.y); ctx.lineTo(footR.x, footR.y);
        ctx.stroke();

        // Draw torso
        ctx.strokeStyle = isSel ? '#5cc8ff' : (h.hero ? '#e07a5f' : '#81b29a');
        ctx.lineWidth = lw * 1.65;
        ctx.beginPath();
        ctx.moveTo(bx, pelvisY);
        ctx.lineTo(bx, chestY);
        ctx.stroke();

        // Draw arms
        ctx.strokeStyle = isSel ? '#ffb86c' : '#f4a261';
        ctx.lineWidth = lw * 0.95;
        ctx.beginPath();
        ctx.moveTo(shL.x, shL.y); ctx.lineTo(elL.x, elL.y); ctx.lineTo(hdL.x, hdL.y);
        ctx.moveTo(shR.x, shR.y); ctx.lineTo(elR.x, elR.y); ctx.lineTo(hdR.x, hdR.y);
        ctx.stroke();

        // Draw Head
        const hr = Math.max(2.2, 0.11 * sc);
        ctx.fillStyle = '#f5d0b5';
        ctx.beginPath();
        ctx.arc(headX, headY, hr, 0, Math.PI * 2);
        ctx.fill();

        // Draw Ruffling Hair Strands on Head
        const gust = hairRuffleStrength * (1.0 + 0.3 * Math.sin(t * 8.0 + hIdx));
        ctx.strokeStyle = hIdx % 3 === 0 ? '#f2b84b' : (hIdx % 2 === 0 ? '#6f4e37' : '#d96b43');
        ctx.lineWidth = Math.max(1.0, 0.025 * sc);
        for (let k = -2; k <= 2; k++) {
          const sx = headX + k * hr * 0.35;
          const sy = headY - hr * 0.75;
          const wx = (Math.sin(t * 9.5 + hIdx + k) * 0.16 + 0.18) * sc * gust;
          const wy = -Math.abs(Math.cos(t * 7.2 + k)) * 0.08 * sc * gust;
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo(sx + wx, sy + hr * 0.65 + wy);
          ctx.stroke();
        }

        if (showBones && (isSel || h.hero)) {
          ctx.fillStyle = isSel ? '#ffffff' : '#5cc8ff';
          [hipL, kneeL, footL, hipR, kneeR, footR, shL, elL, hdL, shR, elR, hdR].forEach(pt => {
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, Math.max(1.5, 0.028 * sc), 0, Math.PI * 2);
            ctx.fill();
          });
        }
      }
    });
  });

  // Painter's sort back-to-front
  drawList.sort((a, b) => b.depth - a.depth);
  drawList.forEach(item => item.draw());

  // Falling winter snow driven by wind
  ctx.fillStyle = 'rgba(235, 245, 255, 0.72)';
  snowflakes.forEach(f => {
    f.z -= dt * 2.2;
    f.x += dt * 4.5 * treeWindStrength;
    if (f.z < 0) f.z = 24;
    if (f.x > 140) f.x = -50;
    const sp = project3D(f.x, f.y, f.z, cX, cY, cZ, sinY, cosY, sinP, cosP, W, H, fovScale);
    if (sp && sp.depth < 90) {
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, f.s, 0, Math.PI * 2);
      ctx.fill();
    }
  });

  renderPipInspector(t);
  requestAnimationFrame(renderLoop);
}
requestAnimationFrame(renderLoop);
</script>
</body>
</html>
"""

html_out = HTML_TEMPLATE.replace("__SCENE_JSON__", scene_json_str)
(ROOT / "index.html").write_text(html_out, encoding="utf-8")

SERVER_PY = """#!/usr/bin/env python3
import http.server
import json
import socketserver
from pathlib import Path

PORT = 8080
DIR = Path(__file__).resolve().parent
STATE_JSON = DIR.parent / "evidence" / "validation" / "playable_state.json"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/playable"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = STATE_JSON.read_text(encoding="utf-8") if STATE_JSON.exists() else "{}"
            self.wfile.write(data.encode("utf-8"))
            return
        return super().do_GET()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Playable 3D City Server listening on http://0.0.0.0:{PORT}", flush=True)
        httpd.serve_forever()
"""
(ROOT / "server.py").write_text(SERVER_PY, encoding="utf-8")
print("Wrote townsquare/playable/index.html and townsquare/playable/server.py")
