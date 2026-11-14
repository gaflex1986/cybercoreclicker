/**
 * CYBER CORE: QUANTUM OVERDRIVE — CLIENT APPLICATION ENGINE
 * Web Audio Procedural Synthesizer, Canvas Reactor Simulator,
 * Hacker Card Terminal, and Cyberpunk Telemetry.
 */

// ============================================================================
// 1. PROCEDURAL SOUND ENGINE (Replicates sound_manager.py via Web Audio API)
// ============================================================================
class CyberAudioEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  _initContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  // 1. Crisp sci-fi click tap
  playClick(freq = 720) {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(freq * 0.7, now + 0.04);

      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.045);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.05);
    } catch (e) {
      // Audio fallback silent
    }
  }

  // 2. Bright energetic crit zap (triad chord)
  playCrit() {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    const freqs = [880, 1320, 1760];
    const now = this.ctx.currentTime;

    freqs.forEach(f => {
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(f, now);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.15);
      } catch (e) {}
    });
  }

  // 3. Upbeat purchase chime
  playBuy() {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    const freqs = [523.25, 659.25, 783.99, 1046.50];
    const now = this.ctx.currentTime;

    freqs.forEach((f, i) => {
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, now + i * 0.04);

        gain.gain.setValueAtTime(0.1, now + i * 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.04 + 0.18);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + i * 0.04);
        osc.stop(now + i * 0.04 + 0.2);
      } catch (e) {}
    });
  }

  // 4. Anomaly spawn sweep
  playAnomalySpawn() {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(350, now);
      osc.frequency.exponentialRampToValueAtTime(900, now + 0.28);

      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.3);
    } catch (e) {}
  }

  // 5. Anomaly capture chord
  playAnomalyCatch() {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    const freqs = [600, 900, 1200, 1500];
    const now = this.ctx.currentTime;

    freqs.forEach(f => {
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, now);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        osc.stop(now + 0.35);
      } catch (e) {}
    });
  }

  // 6. Cash / Hacker credit card intercepted chord
  playCash() {
    if (!this.enabled) return;
    this._initContext();
    if (!this.ctx) return;

    const freqs = [1046.50, 1318.51, 1567.98, 2093.0];
    const now = this.ctx.currentTime;

    freqs.forEach((f, idx) => {
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(f, now + idx * 0.03);

        gain.gain.setValueAtTime(0.14, now + idx * 0.03);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.03 + 0.22);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now + idx * 0.03);
        osc.stop(now + idx * 0.03 + 0.25);
      } catch (e) {}
    });
  }
}

const audio = new CyberAudioEngine();

// ============================================================================
// 2. FAKE CREDIT CARDS DATABASE (From core_engine.py)
// ============================================================================
const FAKE_CARDS = [
  {
    id: 'card_junior',
    name: 'Карта Стажера CyberCorp',
    type: 'CYBERCORP CLASSIC',
    number: '4276 3811 9024 1337',
    holder: 'ALEX_JUNIOR',
    exp: '09/28',
    cvv: '404',
    balance: 150.0,
    gradient: 'linear-gradient(135deg, #183058 0%, #0d1b32 60%, #081120 100%)',
    accent: '#00b4d8'
  },
  {
    id: 'card_gold_corpo',
    name: 'Золотая Карта Нео-Олигарха',
    type: 'NEO-MASTERCARD GOLD',
    number: '5412 7534 8819 2048',
    holder: 'VIKTOR CORPO',
    exp: '11/29',
    cvv: '777',
    balance: 1200.0,
    gradient: 'linear-gradient(135deg, #503c10 0%, #2b2009 60%, #150f04 100%)',
    accent: '#ffb700'
  },
  {
    id: 'card_platinum',
    name: 'Платиновая Карта Кибер-Магната',
    type: 'CYBER PLATINUM VIP',
    number: '4111 5678 9012 4096',
    holder: 'ELON CYBER',
    exp: '04/30',
    cvv: '321',
    balance: 5000.0,
    gradient: 'linear-gradient(135deg, #283448 0%, #161e2c 60%, #0d131c 100%)',
    accent: '#bedcff'
  },
  {
    id: 'card_syndicate',
    name: 'Черная Карта Синдиката',
    type: 'SHADOW SYNDICATE BLACK',
    number: '4000 0012 3456 9999',
    holder: 'SHADOW SYNDICATE',
    exp: '01/31',
    cvv: '666',
    balance: 15000.0,
    gradient: 'linear-gradient(135deg, #1f0b24 0%, #0f0512 60%, #050207 100%)',
    accent: '#ff007f'
  },
  {
    id: 'card_streamer',
    name: 'Карта Стримера-Миллионника',
    type: 'HYPER-STREAM VIP',
    number: '5500 2341 6789 7777',
    holder: 'MR_BEAST_TECH',
    exp: '07/31',
    cvv: '999',
    balance: 50000.0,
    gradient: 'linear-gradient(135deg, #41122a 0%, #240917 60%, #0f030a 100%)',
    accent: '#ff508c'
  },
  {
    id: 'card_matrix',
    name: 'Секретный Счет Архитектора',
    type: 'QUANTUM INFINITY',
    number: '7777 8888 9999 0001',
    holder: 'NEO ARCHITECT',
    exp: '12/35',
    cvv: '101',
    balance: 250000.0,
    gradient: 'linear-gradient(135deg, #0e2a20 0%, #061812 60%, #020a07 100%)',
    accent: '#00ffb4'
  },
  {
    id: 'card_ai_offshore',
    name: 'Офшор Сверхразума ИИ',
    type: 'AI VOID ZERO',
    number: '9999 0101 1010 4242',
    holder: 'OVERMIND AI',
    exp: '99/99',
    cvv: '000',
    balance: 1000000.0,
    gradient: 'linear-gradient(135deg, #141424 0%, #080812 60%, #000000 100%)',
    accent: '#ffd700'
  }
];

// Number formatter with suffixes
function formatNumber(num) {
  if (num < 1000) return num.toFixed(1);
  const suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx'];
  const i = Math.floor(Math.log10(num) / 3);
  if (i >= suffixes.length) return num.toExponential(2);
  const formatted = (num / Math.pow(10, i * 3)).toFixed(2);
  return `${formatted} ${suffixes[i]}`;
}

// ============================================================================
// 3. TOAST NOTIFICATION SYSTEM
// ============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'cyber-toast';
  toast.innerHTML = `
    <span style="color: var(--cyan); font-weight: bold;">//</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ============================================================================
// 4. INTERACTIVE CANVAS REACTOR CORE ENGINE
// ============================================================================
class ReactorSimulator {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    
    // Virtual Dimensions
    this.width = canvas.width;
    this.height = canvas.height;
    this.cx = this.width / 2;
    this.cy = this.height / 2;
    this.baseRadius = 90;

    // Game State
    this.energy = 0.0;
    this.clickPower = 1.0;
    this.combo = 1.0;
    this.comboHeat = 0.0;
    this.passiveEps = 0.0;
    this.anomaliesCaught = 0;
    
    // Upgrades
    this.hasGlove = false;
    this.hasNano = false;
    this.hasPlasma = false;

    // Visual Entities
    this.corePulse = 0.0;
    this.scalePunch = 1.0;
    this.ringAngle1 = 0;
    this.ringAngle2 = 0;
    this.particles = [];
    this.floatingTexts = [];
    this.shockwaves = [];
    this.activeAnomaly = null;
    this.anomalyTimer = 0;

    // Input
    this._bindEvents();
    this.lastTime = performance.now();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  _bindEvents() {
    this.canvas.addEventListener('mousedown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.width / rect.width;
      const scaleY = this.height / rect.height;
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;
      this.handleClick(x, y);
    });

    // Touch support
    this.canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
      if (e.touches.length > 0) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.width / rect.width;
        const scaleY = this.height / rect.height;
        const x = (e.touches[0].clientX - rect.left) * scaleX;
        const y = (e.touches[0].clientY - rect.top) * scaleY;
        this.handleClick(x, y);
      }
    }, { passive: false });

    // Keyboard spacebar
    window.addEventListener('keydown', (e) => {
      if ((e.code === 'Space' || e.key === ' ') && e.target === document.body) {
        e.preventDefault();
        this.handleClick(this.cx, this.cy);
      }
    });
  }

  handleClick(x, y) {
    // Check if clicked anomaly
    if (this.activeAnomaly) {
      const dx = x - this.activeAnomaly.x;
      const dy = y - this.activeAnomaly.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= this.activeAnomaly.radius + 15) {
        this.catchAnomaly();
        return;
      }
    }

    // Check click distance from core
    const cdx = x - this.cx;
    const cdy = y - this.cy;
    const cdist = Math.sqrt(cdx * cdx + cdy * cdy);

    // Click reactor
    const isCrit = Math.random() < 0.18;
    const critMult = isCrit ? 3.0 : 1.0;
    const gained = this.clickPower * this.combo * critMult;

    this.energy += gained;
    this.comboHeat = Math.min(100.0, this.comboHeat + 14.0);
    this.scalePunch = 0.88;

    // Sound
    if (isCrit) {
      audio.playCrit();
    } else {
      const pitch = 680 + (this.combo - 1.0) * 120;
      audio.playClick(pitch);
    }

    // Visual Shockwave
    this.shockwaves.push({
      x: this.cx,
      y: this.cy,
      radius: this.baseRadius * 0.7,
      maxRadius: this.baseRadius * 2.2,
      color: isCrit ? '#ff007f' : (this.combo >= 4.0 ? '#ffb700' : '#00f3ff'),
      alpha: 1.0
    });

    // Particle Burst
    const count = isCrit ? 24 : 12;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 5 + 2;
      this.particles.push({
        x: this.cx + Math.cos(angle) * (this.baseRadius * 0.5),
        y: this.cy + Math.sin(angle) * (this.baseRadius * 0.5),
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: Math.random() * 4 + 2,
        color: isCrit ? '#ff007f' : (Math.random() > 0.4 ? '#00f3ff' : '#00ff88'),
        alpha: 1.0,
        decay: Math.random() * 0.03 + 0.02
      });
    }

    // Floating text
    this.floatingTexts.push({
      x: x + (Math.random() - 0.5) * 20,
      y: y - 10,
      text: isCrit ? `CRIT! +${formatNumber(gained)}⚡` : `+${formatNumber(gained)}⚡`,
      color: isCrit ? '#ff007f' : (this.combo >= 4.0 ? '#ffb700' : '#00f3ff'),
      size: isCrit ? 18 : 15,
      alpha: 1.0,
      vy: -2.0
    });

    this.updateHUD();
  }

  catchAnomaly() {
    if (!this.activeAnomaly) return;
    const bonus = Math.max(100.0, this.energy * 0.25 + 50.0);
    this.energy += bonus;
    this.anomaliesCaught++;

    audio.playAnomalyCatch();

    // Shockwave
    this.shockwaves.push({
      x: this.activeAnomaly.x,
      y: this.activeAnomaly.y,
      radius: 10,
      maxRadius: 150,
      color: '#00ff88',
      alpha: 1.0
    });

    this.floatingTexts.push({
      x: this.activeAnomaly.x,
      y: this.activeAnomaly.y,
      text: `КВАНТОВЫЙ ДАМП! +${formatNumber(bonus)}⚡`,
      color: '#00ff88',
      size: 18,
      alpha: 1.0,
      vy: -2.5
    });

    // Random card hint toast
    const randomCard = FAKE_CARDS[Math.floor(Math.random() * FAKE_CARDS.length)];
    showToast(`⚡ ДАННЫЕ ПЕРЕХВАЧЕНЫ: [${randomCard.name}] открыта в базе!`);

    this.activeAnomaly = null;
    this.updateHUD();
  }

  updateHUD() {
    const elEnergy = document.getElementById('liveEnergyDisplay');
    const elCombo = document.getElementById('liveComboDisplay');
    const elComboBar = document.getElementById('comboMeterBar');
    const elStatus = document.getElementById('overdriveStatusText');
    const elPower = document.getElementById('clickPowerDisplay');
    const elAnom = document.getElementById('anomaliesCaughtCount');

    if (elEnergy) elEnergy.textContent = `${formatNumber(this.energy)} ⚡`;
    if (elCombo) elCombo.textContent = `${this.combo.toFixed(1)}x`;
    if (elComboBar) elComboBar.style.width = `${this.comboHeat}%`;
    if (elPower) elPower.textContent = `+${formatNumber(this.clickPower)} ⚡`;
    if (elAnom) elAnom.textContent = `Поймано аномалий: ${this.anomaliesCaught}`;

    if (elStatus) {
      if (this.combo >= 4.5) {
        elStatus.textContent = 'СТАТУС: 🔥 HYPERDRIVE 5.0x!';
        elStatus.style.color = 'var(--gold)';
      } else if (this.combo >= 2.5) {
        elStatus.textContent = 'СТАТУС: ⚡ OVERDRIVE АКТИВЕН';
        elStatus.style.color = 'var(--magenta)';
      } else {
        elStatus.textContent = 'СТАТУС: НОМИНАЛ';
        elStatus.style.color = 'var(--cyan)';
      }
    }

    // Refresh upgrade buttons
    const btnNano = document.getElementById('btnBuyNano');
    const btnGlove = document.getElementById('btnBuyGlove');
    const btnPlasma = document.getElementById('btnBuyPlasma');

    if (btnNano) btnNano.disabled = this.energy < 100 || this.hasNano;
    if (btnGlove) btnGlove.disabled = this.energy < 150 || this.hasGlove;
    if (btnPlasma) btnPlasma.disabled = this.energy < 1100 || this.hasPlasma;
  }

  animate(now) {
    const dt = Math.min((now - this.lastTime) / 1000.0, 0.1);
    this.lastTime = now;

    // Passive EPS
    if (this.passiveEps > 0) {
      this.energy += this.passiveEps * dt;
    }

    // Combo Heat Decay
    if (this.comboHeat > 0) {
      this.comboHeat = Math.max(0, this.comboHeat - 18.0 * dt);
    }
    // Combo multiplier: 1.0 + (comboHeat / 100) * 4.0 (1.0x to 5.0x)
    this.combo = 1.0 + (this.comboHeat / 100.0) * 4.0;

    // Rotation and pulse
    this.corePulse += dt * (2.0 + (this.combo - 1.0) * 1.5);
    this.ringAngle1 += dt * (0.6 + (this.combo - 1.0) * 0.4);
    this.ringAngle2 -= dt * (0.8 + (this.combo - 1.0) * 0.5);

    // Scale Punch recovery
    if (this.scalePunch < 1.0) {
      this.scalePunch = Math.min(1.0, this.scalePunch + 2.5 * dt);
    }

    // Anomaly Spawner
    this.anomalyTimer += dt;
    if (this.anomalyTimer > 12.0 && !this.activeAnomaly) {
      this.anomalyTimer = 0;
      this.activeAnomaly = {
        x: Math.random() > 0.5 ? 40 : this.width - 40,
        y: Math.random() * (this.height - 100) + 50,
        vx: (Math.random() * 40 + 20) * (Math.random() > 0.5 ? 1 : -1),
        vy: (Math.random() * 30 - 15),
        radius: 16,
        pulse: 0
      };
      audio.playAnomalySpawn();
      showToast('⚠️ ОБНАРУЖЕНА КВАНТОВАЯ АНОМАЛИЯ! Кликните по ней для перехвата!');
    }

    // Update anomaly
    if (this.activeAnomaly) {
      this.activeAnomaly.x += this.activeAnomaly.vx * dt;
      this.activeAnomaly.y += this.activeAnomaly.vy * dt;
      this.activeAnomaly.pulse += dt * 4;

      if (this.activeAnomaly.x < -30 || this.activeAnomaly.x > this.width + 30) {
        this.activeAnomaly = null;
      }
    }

    // Render Canvas
    this.render();

    // Periodic HUD update for passive energy
    this.updateHUD();

    requestAnimationFrame(this.animate);
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // 1. Cyber grid in canvas background
    ctx.strokeStyle = 'rgba(0, 243, 255, 0.05)';
    ctx.lineWidth = 1;
    const gridSize = 35;
    for (let x = 0; x < this.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.height);
      ctx.stroke();
    }
    for (let y = 0; y < this.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.width, y);
      ctx.stroke();
    }

    // 2. Shockwaves
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const sw = this.shockwaves[i];
      sw.radius += (sw.maxRadius - sw.radius) * 0.12;
      sw.alpha -= 0.035;

      if (sw.alpha <= 0) {
        this.shockwaves.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.beginPath();
      ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI * 2);
      ctx.strokeStyle = sw.color;
      ctx.globalAlpha = sw.alpha;
      ctx.lineWidth = 3;
      ctx.shadowBlur = 15;
      ctx.shadowColor = sw.color;
      ctx.stroke();
      ctx.restore();
    }

    // 3. Particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= 0.96;
      p.vy *= 0.96;
      p.alpha -= p.decay;

      if (p.alpha <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = p.alpha;
      ctx.fillStyle = p.color;
      ctx.shadowBlur = 10;
      ctx.shadowColor = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // 4. Central Reactor Core Drawing
    const currentRadius = (this.baseRadius + Math.sin(this.corePulse) * 4) * this.scalePunch;
    const isOverdrive = this.combo >= 4.0;
    const coreColor = isOverdrive ? '#ffb700' : (this.combo >= 2.5 ? '#ff007f' : '#00f3ff');

    ctx.save();
    ctx.translate(this.cx, this.cy);

    // Ambient radial glow behind core
    const ambientGrad = ctx.createRadialGradient(0, 0, 10, 0, 0, currentRadius * 1.8);
    ambientGrad.addColorStop(0, isOverdrive ? 'rgba(255, 183, 0, 0.4)' : 'rgba(0, 243, 255, 0.35)');
    ambientGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = ambientGrad;
    ctx.beginPath();
    ctx.arc(0, 0, currentRadius * 1.8, 0, Math.PI * 2);
    ctx.fill();

    // Outer Ring 1 (Segmented Arcs)
    ctx.save();
    ctx.rotate(this.ringAngle1);
    ctx.strokeStyle = isOverdrive ? '#ffb700' : '#00f3ff';
    ctx.lineWidth = 3;
    ctx.shadowBlur = 16;
    ctx.shadowColor = coreColor;
    const segments = 6;
    const segAngle = (Math.PI * 2) / segments;
    for (let i = 0; i < segments; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, currentRadius * 1.25, i * segAngle, i * segAngle + segAngle * 0.65);
      ctx.stroke();
    }
    // Ring Ticks
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * Math.PI * 2;
      const r1 = currentRadius * 1.32;
      const r2 = currentRadius * (i % 6 === 0 ? 1.42 : 1.36);
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1);
      ctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
      ctx.stroke();
    }
    ctx.restore();

    // Outer Ring 2 (Inner Reverse Ring)
    ctx.save();
    ctx.rotate(this.ringAngle2);
    ctx.strokeStyle = isOverdrive ? '#ff007f' : 'rgba(255, 0, 127, 0.7)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.setLineDash([12, 10]);
    ctx.arc(0, 0, currentRadius * 1.05, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Core Plasma Ball
    const coreGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, currentRadius * 0.75);
    coreGrad.addColorStop(0, '#ffffff');
    coreGrad.addColorStop(0.3, isOverdrive ? '#ffec99' : '#bbf7d0');
    coreGrad.addColorStop(0.7, coreColor);
    coreGrad.addColorStop(1, 'rgba(8, 14, 28, 0.9)');

    ctx.fillStyle = coreGrad;
    ctx.shadowBlur = 30;
    ctx.shadowColor = coreColor;
    ctx.beginPath();
    ctx.arc(0, 0, currentRadius * 0.75, 0, Math.PI * 2);
    ctx.fill();

    // Core Center Icon
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.round(28 * this.scalePunch)}px 'Orbitron', sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ffffff';
    ctx.fillText('⚡', 0, 0);

    ctx.restore();

    // 5. Draw Anomaly if present
    if (this.activeAnomaly) {
      const anom = this.activeAnomaly;
      const anomPulse = Math.sin(anom.pulse) * 4;

      ctx.save();
      ctx.shadowBlur = 25;
      ctx.shadowColor = '#00ff88';

      // Anomaly Glow
      const aGrad = ctx.createRadialGradient(anom.x, anom.y, 2, anom.x, anom.y, anom.radius + anomPulse + 10);
      aGrad.addColorStop(0, '#ffffff');
      aGrad.addColorStop(0.4, '#00ff88');
      aGrad.addColorStop(1, 'rgba(0, 255, 136, 0)');

      ctx.fillStyle = aGrad;
      ctx.beginPath();
      ctx.arc(anom.x, anom.y, anom.radius + anomPulse + 10, 0, Math.PI * 2);
      ctx.fill();

      // Outer targeting brackets
      ctx.strokeStyle = '#00ff88';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(anom.x, anom.y, anom.radius + 12, 0, Math.PI * 2);
      ctx.stroke();

      ctx.fillStyle = '#ffffff';
      ctx.font = "bold 10px 'JetBrains Mono'";
      ctx.textAlign = 'center';
      ctx.fillText('[DATA]', anom.x, anom.y - anom.radius - 8);

      ctx.restore();
    }

    // 6. Floating Texts
    for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
      const ft = this.floatingTexts[i];
      ft.y += ft.vy;
      ft.alpha -= 0.02;

      if (ft.alpha <= 0) {
        this.floatingTexts.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = ft.alpha;
      ctx.fillStyle = ft.color;
      ctx.shadowBlur = 8;
      ctx.shadowColor = ft.color;
      ctx.font = `bold ${ft.size}px 'JetBrains Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.fillText(ft.text, ft.x, ft.y);
      ctx.restore();
    }
  }
}

// ============================================================================
// 5. DOM INITIALIZATION & CARD TERMINAL LOGIC
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Reactor Canvas
  const canvas = document.getElementById('coreCanvas');
  let reactor = null;
  if (canvas) {
    reactor = new ReactorSimulator(canvas);
  }

  // 2. Audio SFX Toggle
  const sfxBtn = document.getElementById('sfxToggle');
  if (sfxBtn) {
    sfxBtn.addEventListener('click', () => {
      const isNowOn = audio.toggle();
      const dot = sfxBtn.querySelector('.sfx-indicator');
      const label = sfxBtn.querySelector('.icon-label');
      if (dot && label) {
        if (isNowOn) {
          dot.className = 'sfx-indicator on';
          label.textContent = 'SFX: ВКЛ';
          audio.playClick(880);
          showToast('🔊 Звуковые эффекты включены');
        } else {
          dot.className = 'sfx-indicator';
          label.textContent = 'SFX: ВЫКЛ';
          showToast('🔇 Звуковые эффекты выключены');
        }
      }
    });
  }

  // 3. CRT Scanlines Toggle
  const crtBtn = document.getElementById('crtToggle');
  if (crtBtn) {
    crtBtn.addEventListener('click', () => {
      document.body.classList.toggle('scanlines-active');
      const isActive = document.body.classList.contains('scanlines-active');
      showToast(isActive ? '📺 CRT-фильтр развертки активирован' : '📺 CRT-фильтр отключен');
      audio.playClick(500);
    });
  }

  // 4. Demo Upgrades
  const btnNano = document.getElementById('btnBuyNano');
  const btnGlove = document.getElementById('btnBuyGlove');
  const btnPlasma = document.getElementById('btnBuyPlasma');

  if (btnNano && reactor) {
    btnNano.addEventListener('click', () => {
      if (reactor.energy >= 100 && !reactor.hasNano) {
        reactor.energy -= 100;
        reactor.passiveEps += 4.0;
        reactor.hasNano = true;
        btnNano.querySelector('.upg-cost').textContent = 'КУПЛЕНО ✔';
        audio.playBuy();
        showToast('🔬 Нано-Конвертер подключен: +4.0 ⚡/сек');
        reactor.updateHUD();
      }
    });
  }

  if (btnGlove && reactor) {
    btnGlove.addEventListener('click', () => {
      if (reactor.energy >= 150 && !reactor.hasGlove) {
        reactor.energy -= 150;
        reactor.clickPower *= 2.0;
        reactor.hasGlove = true;
        btnGlove.querySelector('.upg-cost').textContent = 'КУПЛЕНО ✔';
        audio.playBuy();
        showToast('🧤 Кибер-Перчатка экипирована: Сила клика x2');
        reactor.updateHUD();
      }
    });
  }

  if (btnPlasma && reactor) {
    btnPlasma.addEventListener('click', () => {
      if (reactor.energy >= 1100 && !reactor.hasPlasma) {
        reactor.energy -= 1100;
        reactor.passiveEps += 32.0;
        reactor.hasPlasma = true;
        btnPlasma.querySelector('.upg-cost').textContent = 'КУПЛЕНО ✔';
        audio.playBuy();
        showToast('⚛️ Плазменный Инжектор запущен: +32.0 ⚡/сек');
        reactor.updateHUD();
      }
    });
  }

  // 5. Populate Card Selector
  const cardList = document.getElementById('cardSelectorList');
  let currentSelectedCard = FAKE_CARDS[0];

  function renderCardDetails(card) {
    currentSelectedCard = card;
    const holoCard = document.getElementById('activeHoloCard');
    const holoBank = document.getElementById('holoCardBank');
    const holoNum = document.getElementById('holoCardNumber');
    const holoHolder = document.getElementById('holoCardHolder');
    const holoExp = document.getElementById('holoCardExp');
    const holoCvv = document.getElementById('holoCardCvv');
    const holoBal = document.getElementById('holoCardBalance');

    if (holoCard) {
      holoCard.style.background = card.gradient;
      holoCard.style.borderColor = card.accent;
      holoCard.style.boxShadow = `0 15px 40px ${card.accent}44, inset 0 0 30px ${card.accent}22`;
    }
    if (holoBank) {
      holoBank.textContent = card.type;
      holoBank.style.color = card.accent;
    }
    if (holoNum) holoNum.textContent = card.number;
    if (holoHolder) holoHolder.textContent = card.holder;
    if (holoExp) holoExp.textContent = card.exp;
    if (holoCvv) holoCvv.textContent = card.cvv;
    if (holoBal) {
      holoBal.textContent = `БАЛАНС: $${card.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }
  }

  if (cardList) {
    FAKE_CARDS.forEach((card, index) => {
      const item = document.createElement('div');
      item.className = `card-selector-item ${index === 0 ? 'active' : ''}`;
      item.innerHTML = `
        <div class="card-item-info">
          <span class="card-item-name">${card.name}</span>
          <span class="card-item-holder">${card.holder} • ${card.exp}</span>
        </div>
        <div class="card-item-bal">$${card.balance.toLocaleString('en-US')}</div>
      `;

      item.addEventListener('click', () => {
        document.querySelectorAll('.card-selector-item').forEach(el => el.classList.remove('active'));
        item.classList.add('active');
        renderCardDetails(card);
        audio.playClick(600);
      });

      cardList.appendChild(item);
    });

    renderCardDetails(FAKE_CARDS[0]);
  }

  // 6. Copy Card Details for Game
  const btnCopyCard = document.getElementById('btnCopyCardDetails');
  const tipCopyCard = document.getElementById('copySuccessTip');

  if (btnCopyCard) {
    btnCopyCard.addEventListener('click', () => {
      const textToCopy = `Номер: ${currentSelectedCard.number} | Срок: ${currentSelectedCard.exp} | CVV: ${currentSelectedCard.cvv} | Имя: ${currentSelectedCard.holder}`;
      navigator.clipboard.writeText(textToCopy).then(() => {
        audio.playCash();
        if (tipCopyCard) {
          tipCopyCard.classList.add('show');
          setTimeout(() => tipCopyCard.classList.remove('show'), 2500);
        }
        showToast(`📋 Реквизиты [${currentSelectedCard.name}] скопированы! Введите их в игре.`);
      }).catch(() => {
        // Fallback prompt
        window.prompt('Скопируйте реквизиты карты вручную:', textToCopy);
      });
    });
  }

  // 7. Copy SHA-256 Hash
  const btnCopyHash = document.getElementById('btnCopyHash');
  const sha256Text = document.getElementById('sha256Text');

  if (btnCopyHash && sha256Text) {
    btnCopyHash.addEventListener('click', () => {
      const hash = sha256Text.textContent.trim();
      navigator.clipboard.writeText(hash).then(() => {
        audio.playClick(800);
        btnCopyHash.textContent = 'Скопировано! ✔';
        setTimeout(() => { btnCopyHash.textContent = 'Копировать SHA-256'; }, 2000);
        showToast('🔒 Хэш SHA-256 скопирован в буфер обмена');
      });
    });
  }

  // 8. Hero Download Button SFX
  const heroDownloadBtn = document.getElementById('heroDownloadBtn');
  if (heroDownloadBtn) {
    heroDownloadBtn.addEventListener('click', () => {
      audio.playBuy();
      showToast('⚡ Началась загрузка CyberCoreClicker.exe...');
    });
  }

  const allDownloadLinks = document.querySelectorAll('a[download]');
  allDownloadLinks.forEach(link => {
    link.addEventListener('click', () => {
      audio.playBuy();
    });
  });
});
