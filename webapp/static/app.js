"use strict";

const COLOR_NAME = { blue: "Blue", red: "Red", yellow: "Yellow", green: "Green" };
const GRID = 20;

let ws = null;
let myToken = localStorage.getItem("blokus_token") || null;
let state = null;                 // last 'state' message
const sel = {                     // current piece selection
	color: null, piece: null, pieceData: null,
	byOrientation: {}, orients: [], orientIdx: 0,
};
let anchors = new Map();          // "r,c" -> {move_id, cells}
let previewCells = [];

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const scoresEl = document.getElementById("scores");
const trayEl = document.getElementById("tray");
const hintEl = document.getElementById("hint");
const rotateBtn = document.getElementById("rotate");
const clearBtn = document.getElementById("clear");
const cells = [];

// ---- board scaffold (built once) -------------------------------------------

for (let r = 0; r < GRID; r++) {
	for (let c = 0; c < GRID; c++) {
		const el = document.createElement("div");
		el.className = "cell";
		el.dataset.r = r;
		el.dataset.c = c;
		boardEl.appendChild(el);
		cells.push(el);
	}
}
const cellAt = (r, c) => cells[r * GRID + c];

boardEl.addEventListener("mouseover", (e) => {
	const key = anchorKey(e.target);
	if (key && anchors.has(key)) showPreview(anchors.get(key).cells);
});
boardEl.addEventListener("mouseout", (e) => {
	if (anchorKey(e.target)) clearPreview();
});
boardEl.addEventListener("click", (e) => {
	const key = anchorKey(e.target);
	if (key && anchors.has(key)) send({ type: "make_move", move_id: anchors.get(key).move_id });
});

function anchorKey(el) {
	if (!el.classList || !el.classList.contains("anchor")) return null;
	return el.dataset.r + "," + el.dataset.c;
}

// ---- websocket -------------------------------------------------------------

function connect() {
	ws = new WebSocket(`ws://${location.host}/ws`);
	ws.onopen = () => send({ type: "join", token: myToken });
	ws.onclose = () => { statusEl.textContent = "Disconnected — retrying…"; setTimeout(connect, 1500); };
	ws.onmessage = (ev) => handle(JSON.parse(ev.data));
}

function send(obj) {
	if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj));
}

function handle(msg) {
	if (msg.type === "welcome") {
		myToken = msg.token;
		localStorage.setItem("blokus_token", myToken);
	} else if (msg.type === "state") {
		state = msg;
		clearSelection();
		render();
	} else if (msg.type === "placements") {
		onPlacements(msg);
	} else if (msg.type === "error") {
		hintEl.textContent = msg.message;
		hintEl.classList.add("error");
	}
}

// ---- rendering -------------------------------------------------------------

function render() {
	renderBoard();
	renderStatus();
	renderScores();
	renderTray();
}

function renderBoard() {
	const grid = state.grid;
	for (let r = 0; r < GRID; r++) {
		for (let c = 0; c < GRID; c++) {
			const v = grid[r][c];
			cellAt(r, c).className = "cell" + (v ? " c" + v : "");
		}
	}
	anchors.clear();
	previewCells = [];
}

function renderStatus() {
	statusEl.classList.remove("your-turn");
	if (state.status === "game_over") {
		const best = Object.entries(state.final_scores).sort((a, b) => b[1] - a[1])[0];
		statusEl.textContent = `Game over — ${COLOR_NAME[best[0]]} wins (${best[1]}).`;
		return;
	}
	if (state.your_turn) {
		statusEl.textContent = "Your turn — pick a piece.";
		statusEl.classList.add("your-turn");
		return;
	}
	const cur = (state.seats || []).find((s) => s.color === state.current_color);
	if (state.status === "bot_thinking" && cur) {
		statusEl.textContent = `${cur.label} is thinking…`;
	} else if (state.current_color) {
		statusEl.textContent = `Waiting for ${COLOR_NAME[state.current_color]}…`;
	} else {
		statusEl.textContent = "Starting…";
	}
}

function renderScores() {
	scoresEl.innerHTML = "";
	for (const s of state.seats) {
		const row = document.createElement("div");
		row.className = "score-row"
			+ (s.color === state.current_color ? " current" : "")
			+ (s.done ? " done" : "");
		row.innerHTML =
			`<span class="swatch c${s.color_id}"></span>`
			+ `<span class="who">${COLOR_NAME[s.color]} · ${s.label}</span>`
			+ `<span class="pts">${s.score}</span>`;
		scoresEl.appendChild(row);
	}
}

function renderTray() {
	trayEl.innerHTML = "";
	const color = state.your_turn ? state.current_color : null;
	const pieces = color ? (state.your_pieces[color] || []) : [];
	if (!color) {
		document.getElementById("tray-header").textContent =
			state.your_colors && state.your_colors.length ? "Your pieces (wait for your turn)" : "Spectating";
	} else {
		document.getElementById("tray-header").textContent = "Your pieces";
	}
	for (const p of pieces) {
		const firstO = Object.keys(p.orientations)[0];
		trayEl.appendChild(pieceThumb(p, firstO, color));
	}
}

function pieceThumb(p, oIndex, color) {
	const grid = p.orientations[oIndex];
	const el = document.createElement("div");
	el.className = "piece" + (sel.piece === p.name ? " selected" : "");
	el.style.gridTemplateColumns = `repeat(${grid[0].length}, 10px)`;
	el.style.setProperty("--sel", `var(--c${colorId(color)})`);
	for (const row of grid) {
		for (const v of row) {
			const pc = document.createElement("div");
			pc.className = "pc " + (v ? "on" : "off");
			el.appendChild(pc);
		}
	}
	el.title = `${p.name} (${p.block_count})`;
	el.addEventListener("click", () => selectPiece(p, color));
	return el;
}

function colorId(color) {
	const seat = state.seats.find((s) => s.color === color);
	return seat ? seat.color_id : 1;
}

// ---- selection + placement -------------------------------------------------

function selectPiece(p, color) {
	hintEl.textContent = "";
	hintEl.classList.remove("error");
	sel.color = color;
	sel.piece = p.name;
	sel.pieceData = p;
	sel.byOrientation = {};
	sel.orients = [];
	sel.orientIdx = 0;
	renderTray();   // highlight selected
	send({ type: "select_piece", color, piece: p.name });
}

function onPlacements(msg) {
	if (msg.piece !== sel.piece || msg.color !== sel.color) return;
	sel.byOrientation = msg.by_orientation || {};
	sel.orients = Object.keys(sel.byOrientation).map(Number).sort((a, b) => a - b);
	sel.orientIdx = 0;
	if (sel.orients.length === 0) {
		hintEl.textContent = "No legal spot for that piece — try another.";
		rotateBtn.disabled = true;
		clearBtn.disabled = false;
		clearAnchors();
		return;
	}
	rotateBtn.disabled = sel.orients.length <= 1;
	clearBtn.disabled = false;
	highlightCurrentOrientation();
}

function highlightCurrentOrientation() {
	clearAnchors();
	const o = sel.orients[sel.orientIdx];
	const placements = sel.byOrientation[o] || [];
	for (const pl of placements) {
		const [r, c] = pl.anchor;
		cellAt(r, c).classList.add("anchor");
		anchors.set(r + "," + c, pl);
	}
	hintEl.textContent = `${placements.length} spot${placements.length === 1 ? "" : "s"}`
		+ (sel.orients.length > 1 ? ` · orientation ${sel.orientIdx + 1}/${sel.orients.length}` : "")
		+ ". Hover to preview, click to place.";
}

rotateBtn.addEventListener("click", () => {
	if (sel.orients.length <= 1) return;
	sel.orientIdx = (sel.orientIdx + 1) % sel.orients.length;
	highlightCurrentOrientation();
});

clearBtn.addEventListener("click", clearSelection);

function clearSelection() {
	sel.color = null; sel.piece = null; sel.pieceData = null;
	sel.byOrientation = {}; sel.orients = []; sel.orientIdx = 0;
	rotateBtn.disabled = true;
	clearBtn.disabled = true;
	clearAnchors();
	hintEl.textContent = "";
	hintEl.classList.remove("error");
	const selectedEl = trayEl.querySelector(".piece.selected");
	if (selectedEl) selectedEl.classList.remove("selected");
}

function clearAnchors() {
	clearPreview();
	for (const el of cells) el.classList.remove("anchor");
	anchors.clear();
}

function showPreview(cellsList) {
	clearPreview();
	for (const [r, c] of cellsList) {
		cellAt(r, c).classList.add("preview");
		previewCells.push([r, c]);
	}
}

function clearPreview() {
	for (const [r, c] of previewCells) cellAt(r, c).classList.remove("preview");
	previewCells = [];
}

// ---- controls --------------------------------------------------------------

document.getElementById("new-game").addEventListener("click", () => send({ type: "new_game" }));

connect();
