"use strict";

const COLOR_NAME = { blue: "Blue", red: "Red", yellow: "Yellow", green: "Green" };
const COLOR_ID = { blue: 1, red: 2, yellow: 3, green: 4 };
const GRID = 20;

let ws = null;
let myToken = localStorage.getItem("blokus_token") || null;
let state = null;
let lastEventId = 0;
let toastTimer = null;

// current piece selection + pending (chosen-but-unconfirmed) placement
const sel = {
	color: null, piece: null, pieceData: null,
	byOrientation: {}, keyMap: {}, curO: null, curGrid: null,
};
let pending = null;               // {move_id, cells} awaiting confirmation
let anchors = new Map();          // "r,c" -> placement
let previewCells = [];

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const hintEl = document.getElementById("hint");
const previewEl = document.getElementById("preview");
const toastEl = document.getElementById("toast");
const rotCwBtn = document.getElementById("rot-cw");
const rotCcwBtn = document.getElementById("rot-ccw");
const flipBtn = document.getElementById("flip");
const clearBtn = document.getElementById("clear");
const confirmBtn = document.getElementById("confirm");
const cancelBtn = document.getElementById("cancel");
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
	if (pending) return;
	const key = anchorKey(e.target);
	if (key && anchors.has(key)) showHover(anchors.get(key).cells);
});
boardEl.addEventListener("mouseout", (e) => { if (!pending && anchorKey(e.target)) clearHover(); });
boardEl.addEventListener("click", (e) => {
	const key = anchorKey(e.target);
	if (key && anchors.has(key)) choosePending(anchors.get(key));
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
function send(obj) { if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj)); }

function handle(msg) {
	if (msg.type === "welcome") {
		myToken = msg.token;
		localStorage.setItem("blokus_token", myToken);
	} else if (msg.type === "state") {
		state = msg;
		maybeToast(msg.last_event);
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
	renderScoreboard();
	renderSeatCards();
	renderGameOver();
}

function renderScoreboard() {
	const el = document.getElementById("scoreboard");
	const teams = state.teams || [];
	// only show the team scoreboard when colors are grouped (e.g. Phase 2: You vs Bot)
	if (teams.length === 0 || teams.length >= 4) { el.classList.add("hidden"); return; }
	el.innerHTML = "";
	for (const t of teams) {
		const you = t.colors.some((c) => (state.your_colors || []).includes(c));
		const sw = t.members.map((m) => `<span class="swatch c${m.color_id}"></span>`).join("");
		const box = document.createElement("div");
		box.className = "team" + (you ? " you" : "");
		box.innerHTML = `<span class="team-swatches">${sw}</span>`
			+ `<span class="team-label">${you ? "You" : t.label}</span>`
			+ `<span class="team-score">${t.score}</span>`;
		el.appendChild(box);
	}
	el.classList.remove("hidden");
}

function renderGameOver() {
	const overlay = document.getElementById("gameover");
	if (state.status !== "game_over" || !state.teams) {
		overlay.classList.add("hidden");
		return;
	}
	const isYours = (t) => t.colors.some((c) => (state.your_colors || []).includes(c));
	const rows = state.teams.slice().sort((a, b) => b.score - a.score);
	const top = rows[0].score;
	const winners = rows.filter((r) => r.score === top);
	const youWon = winners.some(isYours);

	const card = overlay.querySelector(".overlay-card");
	const titleEl = document.getElementById("go-title");
	if (winners.length > 1) {
		card.style.setProperty("--win", "var(--ink)");
		titleEl.textContent = youWon ? "You tie for the win!" : winners.map((w) => teamName(w)).join(" & ") + " tie!";
	} else {
		card.style.setProperty("--win", `var(--c${winners[0].members[0].color_id})`);
		titleEl.textContent = youWon ? "You win! 🎉" : `${teamName(winners[0])} wins!`;
	}
	document.getElementById("go-sub").textContent = `Top score: ${top}`;

	const standings = document.getElementById("go-standings");
	standings.innerHTML = "";
	for (const t of rows) {
		const rank = rows.filter((x) => x.score > t.score).length + 1;
		const sw = t.members.map((m) => `<span class="swatch c${m.color_id}"></span>`).join("");
		const detail = t.members.length > 1
			? t.members.map((m) => `${COLOR_NAME[m.color]} ${m.score}`).join(" + ")
			: t.label;
		const row = document.createElement("div");
		row.className = "go-row" + (t.score === top ? " winner" : "");
		row.style.setProperty("--win", `var(--c${t.members[0].color_id})`);
		row.innerHTML =
			`<span class="go-rank">#${rank}</span>`
			+ `<span class="go-swatches">${sw}</span>`
			+ `<span class="go-name">${isYours(t) ? "You" : teamName(t)} <small>${detail}</small></span>`
			+ `<span class="go-score">${t.score}</span>`;
		standings.appendChild(row);
	}
	overlay.classList.remove("hidden");
}

function teamName(t) {
	// single-color teams (free-for-all) read better as the color name
	return t.members.length === 1 ? COLOR_NAME[t.members[0].color] : t.label;
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
		const order = Object.entries(state.final_scores).sort((a, b) => b[1] - a[1]);
		statusEl.textContent = `Game over — ${COLOR_NAME[order[0][0]]} wins with ${order[0][1]}.`;
		return;
	}
	if (state.your_turn) {
		statusEl.textContent = `Your turn — place a ${COLOR_NAME[state.current_color]} piece, then Confirm.`;
		statusEl.classList.add("your-turn");
		return;
	}
	const cur = (state.seats || []).find((s) => s.color === state.current_color);
	if (state.status === "bot_thinking" && cur) statusEl.textContent = `${cur.label} (${COLOR_NAME[cur.color]}) is thinking…`;
	else if (state.current_color) statusEl.textContent = `Waiting for ${COLOR_NAME[state.current_color]}…`;
	else statusEl.textContent = "Starting…";
}

function renderSeatCards() {
	for (const seat of state.seats) {
		const card = document.getElementById("card-" + seat.color);
		const active = seat.color === state.current_color && state.status !== "game_over";
		card.className = "seat-card" + (active ? " active" : "") + (seat.done ? " out" : "");
		card.style.setProperty("--acc", `var(--c${seat.color_id})`);

		const isYou = (state.your_colors || []).includes(seat.color);
		let sub;
		if (seat.done) sub = seat.pieces_left === 0 ? "Finished — all pieces placed" : "Out — no legal moves left";
		else sub = `${seat.pieces_left} piece${seat.pieces_left === 1 ? "" : "s"} left`;

		card.innerHTML =
			`<div class="card-head">`
			+ `<span class="swatch c${seat.color_id}"></span>`
			+ `<span class="card-name">${COLOR_NAME[seat.color]}${isYou ? " · You" : ""} <small>${seat.label}</small></span>`
			+ `<span class="card-score">${seat.score}</span>`
			+ `</div><div class="card-sub">${sub}</div><div class="card-pieces"></div>`;

		const piecesEl = card.querySelector(".card-pieces");
		const clickable = isYou && state.your_turn && seat.color === state.current_color && !seat.done;
		const yourMap = clickable ? byName(state.your_pieces[seat.color] || []) : null;
		for (const p of (state.players_pieces[seat.color] || [])) {
			const mini = miniPiece(p.grid, seat.color_id, clickable && sel.piece === p.name);
			mini.title = `${p.name} (${p.block_count})`;
			if (clickable) {
				mini.classList.add("clickable");
				mini.addEventListener("click", () => selectPiece(yourMap[p.name], seat.color));
			}
			piecesEl.appendChild(mini);
		}
	}
}

function byName(list) { const m = {}; for (const p of list) m[p.name] = p; return m; }

function miniPiece(grid, colorId, selected) {
	const el = document.createElement("div");
	el.className = "mini" + (selected ? " selected" : "");
	el.style.gridTemplateColumns = `repeat(${grid[0].length}, 5px)`;
	el.style.setProperty("--pcol", `var(--c${colorId})`);
	for (const row of grid) for (const v of row) {
		const pc = document.createElement("div");
		pc.className = "pc " + (v ? "on" : "off");
		el.appendChild(pc);
	}
	return el;
}

// ---- selection + preview ---------------------------------------------------

function selectPiece(p, color) {
	if (!p) return;
	clearPending();
	hintEl.textContent = "";
	hintEl.classList.remove("error");
	sel.color = color;
	sel.piece = p.name;
	sel.pieceData = p;
	sel.byOrientation = {};
	sel.keyMap = {};
	for (const k of Object.keys(p.orientations)) sel.keyMap[gridKey(p.orientations[k])] = k;
	sel.curO = Object.keys(p.orientations)[0];
	sel.curGrid = p.orientations[sel.curO];
	renderPreview();
	setControlsEnabled(true);
	highlightSelectedThumb();
	send({ type: "select_piece", color, piece: p.name });
}

function onPlacements(msg) {
	if (msg.piece !== sel.piece || msg.color !== sel.color) return;
	sel.byOrientation = msg.by_orientation || {};
	const valid = Object.keys(sel.byOrientation);
	if (valid.length === 0) {
		hintEl.textContent = "No legal spot for this piece — pick another.";
		highlightOrientation();
		return;
	}
	if (!(sel.curO in sel.byOrientation)) {
		setOrientation(valid.map(Number).sort((a, b) => a - b)[0].toString());
		return;
	}
	highlightOrientation();
}

function setOrientation(o) {
	if (!sel.pieceData || !(o in sel.pieceData.orientations)) return;
	clearPending();
	sel.curO = o;
	sel.curGrid = sel.pieceData.orientations[o];
	renderPreview();
	highlightOrientation();
}

function renderPreview() {
	previewEl.innerHTML = "";
	if (!sel.curGrid) { previewEl.innerHTML = '<span class="empty">Pick a piece</span>'; return; }
	previewEl.style.gridTemplateColumns = `repeat(${sel.curGrid[0].length}, 16px)`;
	previewEl.style.setProperty("--pcol", `var(--c${COLOR_ID[sel.color] || 1})`);
	for (const row of sel.curGrid) for (const v of row) {
		const pc = document.createElement("div");
		pc.className = "pc " + (v ? "on" : "off");
		previewEl.appendChild(pc);
	}
}

function highlightOrientation() {
	clearAnchors();
	const placements = (sel.curO && sel.byOrientation[sel.curO]) || [];
	for (const pl of placements) {
		const [r, c] = pl.anchor;
		cellAt(r, c).classList.add("anchor");
		anchors.set(r + "," + c, pl);
	}
	if (placements.length) {
		hintEl.textContent = `${placements.length} spot${placements.length === 1 ? "" : "s"} for this orientation — click one to line it up.`;
		hintEl.classList.remove("error");
	} else if (Object.keys(sel.byOrientation).length) {
		hintEl.textContent = "No spot in this orientation — rotate or flip.";
		hintEl.classList.remove("error");
	}
}

function highlightSelectedThumb() {
	for (const el of document.querySelectorAll(".mini.selected")) el.classList.remove("selected");
	// re-render handled by renderSeatCards on next state; mark current eagerly is optional
}

// ---- confirm-before-place --------------------------------------------------

function choosePending(pl) {
	clearHover();
	clearPendingHighlight();
	pending = pl;
	for (const [r, c] of pl.cells) cellAt(r, c).classList.add("pending");
	confirmBtn.classList.remove("hidden");
	cancelBtn.classList.remove("hidden");
	hintEl.textContent = "Confirm this placement?  (Enter to confirm, Esc to cancel)";
	hintEl.classList.remove("error");
}

function clearPending() { clearPendingHighlight(); pending = null; confirmBtn.classList.add("hidden"); cancelBtn.classList.add("hidden"); }
function clearPendingHighlight() { for (const el of cells) el.classList.remove("pending"); }

confirmBtn.addEventListener("click", () => {
	if (pending) { send({ type: "make_move", move_id: pending.move_id }); clearPending(); }
});
cancelBtn.addEventListener("click", () => { clearPending(); highlightOrientation(); });

// ---- transforms (rotate / flip) --------------------------------------------

function rotateCW(g) { const R = g.length, C = g[0].length, o = Array.from({ length: C }, () => Array(R).fill(0)); for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) o[c][R - 1 - r] = g[r][c]; return o; }
function rotateCCW(g) { const R = g.length, C = g[0].length, o = Array.from({ length: C }, () => Array(R).fill(0)); for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) o[C - 1 - c][r] = g[r][c]; return o; }
function flipH(g) { return g.map((row) => row.slice().reverse()); }
function gridKey(g) { return g.map((r) => r.join("")).join("/"); }

function applyTransform(fn) {
	if (!sel.curGrid) return;
	const o = sel.keyMap[gridKey(fn(sel.curGrid))];
	if (o !== undefined) setOrientation(o);
}
rotCwBtn.addEventListener("click", () => applyTransform(rotateCW));
rotCcwBtn.addEventListener("click", () => applyTransform(rotateCCW));
flipBtn.addEventListener("click", () => applyTransform(flipH));
clearBtn.addEventListener("click", clearSelection);

function setControlsEnabled(on) {
	rotCwBtn.disabled = !on; rotCcwBtn.disabled = !on; flipBtn.disabled = !on; clearBtn.disabled = !on;
}

// ---- clearing / hover ------------------------------------------------------

function clearSelection() {
	clearPending();
	sel.color = null; sel.piece = null; sel.pieceData = null;
	sel.byOrientation = {}; sel.keyMap = {}; sel.curO = null; sel.curGrid = null;
	setControlsEnabled(false);
	clearAnchors();
	renderPreview();
	hintEl.textContent = "";
	hintEl.classList.remove("error");
}
function clearAnchors() { clearHover(); for (const el of cells) el.classList.remove("anchor"); anchors.clear(); }
function showHover(list) { clearHover(); for (const [r, c] of list) { cellAt(r, c).classList.add("preview"); previewCells.push([r, c]); } }
function clearHover() { for (const [r, c] of previewCells) cellAt(r, c).classList.remove("preview"); previewCells = []; }

// ---- toast -----------------------------------------------------------------

function maybeToast(ev) {
	if (!ev || ev.id === lastEventId) return;
	lastEventId = ev.id;
	toastEl.innerHTML = `<span class="dot c${COLOR_ID[ev.color]}"></span>${ev.message}`;
	toastEl.classList.remove("hidden");
	if (toastTimer) clearTimeout(toastTimer);
	toastTimer = setTimeout(() => toastEl.classList.add("hidden"), 3600);
}

// ---- keyboard --------------------------------------------------------------

document.addEventListener("keydown", (e) => {
	if (e.key === "Enter" && pending) { confirmBtn.click(); }
	else if (e.key === "Escape") { if (pending) cancelBtn.click(); else clearSelection(); }
	else if ((e.key === "r" || e.key === "R") && sel.curGrid) { applyTransform(rotateCW); }
	else if ((e.key === "f" || e.key === "F") && sel.curGrid) { applyTransform(flipH); }
});

document.getElementById("new-game").addEventListener("click", () => send({ type: "new_game" }));
document.getElementById("go-newgame").addEventListener("click", () => send({ type: "new_game" }));

renderPreview();
connect();
