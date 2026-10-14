// CYBER SMASH ARENA - Navegador Web Client
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let currentRoom = null;
let myPlayerNum = 1;
let selectedChar = 'NEXUS';
let gameActive = false;
let isOnline = false;

// Estado del juego
const STAGE = { x: 180, y: 390, w: 600, h: 36 };
const CHAR_DATA = {
  NEXUS: { color: '#00e5ff', speed: 6.5, jump: 13.5 },
  VALKYRIE: { color: '#ff2d65', speed: 7.8, jump: 14.5 },
  GOLIATH: { color: '#aa3cff', speed: 5.2, jump: 12.0 },
  PHANTOM: { color: '#28ff96', speed: 7.0, jump: 14.0 }
};

let p1 = {
  x: 320, y: 320, vx: 0, vy: 0, pct: 0, stocks: 3, facing: 1,
  color: '#00e5ff', char: 'NEXUS', onGround: false, hitstun: 0
};

let p2 = {
  x: 640, y: 320, vx: 0, vy: 0, pct: 0, stocks: 3, facing: -1,
  color: '#ff2d65', char: 'VALKYRIE', onGround: false, hitstun: 0
};

let particles = [];
let keys = {};

window.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if ([' ', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(e.key.toLowerCase())) {
    e.preventDefault();
  }
});

window.addEventListener('keyup', e => {
  keys[e.key.toLowerCase()] = false;
});

// Selector de personaje
document.querySelectorAll('.char-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.char-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedChar = btn.dataset.char;
    p1.char = selectedChar;
    p1.color = CHAR_DATA[selectedChar].color;
  });
});

// Pestañas
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    const target = btn.id.replace('tab-', 'panel-');
    document.getElementById(target).classList.add('active');
  });
});

// API Calls
async function createRoom() {
  try {
    const res = await fetch('/api/create_room', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stocks: 3 })
    });
    const data = await res.json();
    if (data.success) {
      currentRoom = data.room_id;
      myPlayerNum = 1;
      isOnline = true;
      document.getElementById('room-display').innerText = `Sala: ${currentRoom} (P1)`;
      document.getElementById('input-room').value = currentRoom;
      startOnlinePoll();
    }
  } catch (err) {
    alert("Error al conectar con el servidor: " + err);
  }
}

async function joinRoom() {
  const code = document.getElementById('input-room').value.trim().toUpperCase();
  if (!code) return alert("Introduce un código de sala.");
  try {
    const res = await fetch('/api/join_room', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room_id: code })
    });
    const data = await res.json();
    if (data.success) {
      currentRoom = data.room_id;
      myPlayerNum = 2;
      isOnline = true;
      document.getElementById('room-display').innerText = `Sala: ${currentRoom} (P2)`;
      startOnlinePoll();
    } else {
      alert(data.error);
    }
  } catch (err) {
    alert("Error al unirse: " + err);
  }
}

document.getElementById('btn-create').addEventListener('click', createRoom);
document.getElementById('btn-join').addEventListener('click', joinRoom);
document.getElementById('btn-start-game').addEventListener('click', () => {
  document.getElementById('game-overlay').style.display = 'none';
  gameActive = true;
});

// Loop de red online
function startOnlinePoll() {
  setInterval(async () => {
    if (!isOnline || !currentRoom) return;
    try {
      const myObj = myPlayerNum === 1 ? p1 : p2;
      const res = await fetch(`/api/room/${currentRoom}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player: myPlayerNum,
          state: {
            x: myObj.x, y: myObj.y, vx: myObj.vx, vy: myObj.vy,
            pct: myObj.pct, stocks: myObj.stocks, facing: myObj.facing
          }
        })
      });
      const data = await res.json();
      if (data.success && data.opponent_state) {
        const opp = myPlayerNum === 1 ? p2 : p1;
        opp.x = data.opponent_state.x;
        opp.y = data.opponent_state.y;
        opp.pct = data.opponent_state.pct;
        opp.stocks = data.opponent_state.stocks;
        opp.facing = data.opponent_state.facing;
      }
    } catch (e) {
      console.log("Sync error:", e);
    }
  }, 50);
}

// Bucle de Juego Principal en Canvas (60 FPS)
function updateGame() {
  if (!gameActive) return;

  const me = myPlayerNum === 1 ? p1 : p2;
  const cfg = CHAR_DATA[me.char] || CHAR_DATA.NEXUS;

  // Controles del jugador local
  if (keys['a']) { me.vx = -cfg.speed; me.facing = -1; }
  else if (keys['d']) { me.vx = cfg.speed; me.facing = 1; }
  else { me.vx *= 0.8; }

  if ((keys['w'] || keys[' ']) && me.onGround) {
    me.vy = -cfg.jump;
    me.onGround = false;
  }

  // Gravedad
  me.vy += 0.65;
  me.x += me.vx;
  me.y += me.vy;

  // Plataforma sólida
  if (me.x + 20 > STAGE.x && me.x - 20 < STAGE.x + STAGE.w) {
    if (me.y >= STAGE.y - 40 && me.y - me.vy <= STAGE.y - 30) {
      me.y = STAGE.y - 40;
      me.vy = 0;
      me.onGround = true;
    }
  }

  // CPU básica si se juega en solitario en el navegador
  if (!isOnline) {
    const opp = p2;
    if (opp.x < p1.x - 40) opp.vx = 3.5;
    else if (opp.x > p1.x + 40) opp.vx = -3.5;
    else opp.vx = 0;

    opp.vy += 0.65;
    opp.x += opp.vx;
    opp.y += opp.vy;

    if (opp.x + 20 > STAGE.x && opp.x - 20 < STAGE.x + STAGE.w) {
      if (opp.y >= STAGE.y - 40 && opp.y - opp.vy <= STAGE.y - 30) {
        opp.y = STAGE.y - 40;
        opp.vy = 0;
        opp.onGround = true;
      }
    }
  }

  // Comprobar KOs
  [p1, p2].forEach(p => {
    if (p.x < -100 || p.x > canvas.width + 100 || p.y > canvas.height + 100) {
      p.stocks--;
      p.x = 480;
      p.y = 150;
      p.vx = 0;
      p.vy = 0;
      p.pct = 0;
    }
  });
}

function render() {
  ctx.fillStyle = '#0a0d20';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Sol de fondo
  const grad = ctx.createRadialGradient(480, 260, 20, 480, 260, 160);
  grad.addColorStop(0, 'rgba(255, 220, 40, 0.8)');
  grad.addColorStop(0.5, 'rgba(255, 45, 110, 0.4)');
  grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(480, 260, 160, 0, Math.PI * 2);
  ctx.fill();

  // Escenario
  ctx.fillStyle = '#1c2242';
  ctx.fillRect(STAGE.x, STAGE.y, STAGE.w, STAGE.h);
  ctx.strokeStyle = '#7158ff';
  ctx.lineWidth = 4;
  ctx.strokeRect(STAGE.x, STAGE.y, STAGE.w, STAGE.h);

  // Dibujar luchadores
  [p1, p2].forEach(p => {
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y - 10, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Torso y extremidades
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x - 8, p.y + 4, 16, 26);
    ctx.fillStyle = '#fff';
    ctx.fillRect(p.x - 3, p.y + 4, 6, 26);
  });

  // HUD
  ctx.font = 'bold 20px Rajdhani, sans-serif';
  ctx.fillStyle = p1.color;
  ctx.fillText(`P1 (${p1.char}): ${Math.floor(p1.pct)}% [Vidas: ${p1.stocks}]`, 40, 40);

  ctx.fillStyle = p2.color;
  ctx.fillText(`P2 (${p2.char}): ${Math.floor(p2.pct)}% [Vidas: ${p2.stocks}]`, canvas.width - 320, 40);

  updateGame();
  requestAnimationFrame(render);
}

render();
