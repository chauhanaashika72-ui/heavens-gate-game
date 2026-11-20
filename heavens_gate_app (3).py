import webview

# ゲームのHTMLコンテンツ
html_content = r"""
<div style="text-align: center; font-family: sans-serif; background-color: #0f172a; padding: 20px; border-radius: 10px; color: #fff;">
    <h2>✨ Heaven's Gate - Playable Game ✨</h2>
    <p>画面をクリック、またはキーを押すと、神秘的な天国のBGMが流れ始めます！<br>マウスやキー（WASD）でプレイヤー（青い光）を動かし、星を避けてゲート（黄色）に入りましょう！</p>
    <canvas id="gameCanvas" width="600" height="400" style="border: 2px solid #38bdf8; background-color: #090d16; cursor: none;"></canvas>
    <div style="margin-top: 10px;">
        <span id="scoreDisplay" style="font-size: 20px; color: #fef08a;">Score: 0</span>
        <button id="restartBtn" style="margin-left: 20px; padding: 8px 16px; background-color: #38bdf8; border: none; border-radius: 5px; color: #000; font-weight: bold; cursor: pointer; display: none;">Restart Game</button>
        <button id="muteBtn" style="margin-left: 10px; padding: 8px 16px; background-color: #475569; border: none; border-radius: 5px; color: #fff; cursor: pointer;">Mute BGM</button>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreDisplay = document.getElementById('scoreDisplay');
const restartBtn = document.getElementById('restartBtn');
const muteBtn = document.getElementById('muteBtn');

let score = 0;
let gameOver = false;

// プレイヤー設定
const player = { 
    x: 300, 
    y: 350, 
    radius: 12, 
    speed: 5, 
    color: '#38bdf8'
};

// 天国のゲート（ゴール）設定
const gate = { 
    x: 300, 
    y: 80, 
    radius: 25, 
    color: '#fef08a', 
    pulse: 0 
};

// 流れ星（障害物）リスト
let shootingStars = [];

// キー入力状態
const keys = {};

// マウス座標
let mouseX = 300;
let mouseY = 350;
let useMouse = true;

// ==========================================
// 🎵 Web Audio API 音楽生成エンジン
// ==========================================
let audioCtx = null;
let mainVolume = null;
let isMuted = false;
let musicInterval = null;

function initAudio() {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    mainVolume = audioCtx.createGain();
    mainVolume.gain.setValueAtTime(0.12, audioCtx.currentTime); // うるさすぎない音量
    mainVolume.connect(audioCtx.destination);
    startHeavenlyBGM();
}

// 神秘的なアルペジオBGMをリアルタイム合成
function startHeavenlyBGM() {
    const scale = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25]; // C5 Pentatonic
    let step = 0;

    musicInterval = setInterval(() => {
        if (isMuted || gameOver || !audioCtx) return;
        
        // コード音（バックグラウンドに広がる和音）
        if (step % 8 === 0) {
            playPadChord([261.63, 329.63, 392.00, 523.25], 3.0); // C Major Pad
        } else if (step % 8 === 4) {
            playPadChord([293.66, 349.23, 440.00, 587.33], 3.0); // D minor Pad
        }

        // 高音のキラキラしたメロディラインをランダムに奏でる
        if (Math.random() < 0.6) {
            const note = scale[Math.floor(Math.random() * scale.length)] * 1.5;
            playPluckNote(note, 1.2);
        }

        step++;
    }, 450); // テンポ
}

// フワッとしたパッド音（和音用）
function playPadChord(frequencies, duration) {
    const now = audioCtx.currentTime;
    frequencies.forEach(freq => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.04, now + 1.0); // アタックを遅く
        gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
        
        osc.connect(gain);
        gain.connect(mainVolume);
        osc.start(now);
        osc.stop(now + duration);
    });
}

// ピカピカした短い金属音（メロディ用）
function playPluckNote(freq, duration) {
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'triangle'; // 少し丸みがありつつクリアな音
    osc.frequency.setValueAtTime(freq, now);
    
    gain.gain.setValueAtTime(0.05, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration); 
    
    osc.connect(gain);
    gain.connect(mainVolume);
    osc.start(now);
    osc.stop(now + duration);
}

// 効果音：ゴールイン
function playGoalSound() {
    if (!audioCtx || isMuted) return;
    const now = audioCtx.currentTime;
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now + i * 0.08);
        gain.gain.setValueAtTime(0.08, now + i * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.08 + 0.3);
        osc.connect(gain);
        gain.connect(mainVolume);
        osc.start(now + i * 0.08);
        osc.stop(now + i * 0.08 + 0.35);
    });
}

// ミュートボタン制御
muteBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    muteBtn.innerText = isMuted ? "Unmute BGM" : "Mute BGM";
    muteBtn.style.backgroundColor = isMuted ? "#ef4444" : "#475569";
});

// ユーザーのアクションでサウンドを初期化
window.addEventListener('keydown', initAudio);
canvas.addEventListener('click', initAudio);
canvas.addEventListener('mousemove', initAudio);

// ==========================================

// キーボードイベント
window.addEventListener('keydown', e => {
    keys[e.key] = true;
    useMouse = false;
});
window.addEventListener('keyup', e => {
    keys[e.key] = false;
});

// マウスイベント
canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
    useMouse = true;
});

// 星背景の初期化 (より多くの輝き、色、明滅パラメータを設定)
const backgroundStars = [];
const starColors = ['#fef08a', '#e0f2fe', '#ffffff', '#fed7aa', '#f472b6'];
for (let i = 0; i < 80; i++) {
    backgroundStars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        baseSize: Math.random() * 2.5 + 0.5, 
        alpha: Math.random(),
        twinkleSpeed: 0.02 + Math.random() * 0.05,
        color: starColors[Math.floor(Math.random() * starColors.length)]
    });
}

function spawnShootingStar() { 
    if (Math.random() < 0.08 && shootingStars.length < 8) {
        shootingStars.push({
            x: Math.random() * canvas.width,
            y: 0,
            vx: (Math.random() - 0.5) * 4,
            vy: 3 + Math.random() * 4,
            length: 15 + Math.random() * 15,
            width: 2 + Math.random() * 2
        });
    }
}

function checkCollision(p, star) {
    const dx = p.x - star.x;
    const dy = p.y - star.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    return dist < (p.radius + star.width);
}

function resetGame() {
    score = 0;
    gameOver = false;
    player.x = 300;
    player.y = 350;
    shootingStars = [];
    restartBtn.style.display = 'none';
    scoreDisplay.innerText = "Score: " + score;
    animate();
}

restartBtn.addEventListener('click', resetGame);

function animate() {
    if (gameOver) {
        restartBtn.style.display = 'inline-block';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ef4444';
        ctx.font = '30px sans-serif';
        ctx.fillText("GAME OVER", 210, 180);
        ctx.fillStyle = '#fff';
        ctx.font = '20px sans-serif';
        ctx.fillText("Touch the shooting star.", 190, 220);
        return;
    }

    // 画面クリア
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 背景のきらめく星を描画 (Glittering effects with custom glow)
    backgroundStars.forEach(star => {
        star.alpha += star.twinkleSpeed;
        if (star.alpha > 1.2 || star.alpha < 0.1) {
            star.twinkleSpeed = -star.twinkleSpeed;
        }
        
        let currentAlpha = Math.max(0.1, Math.min(1.0, star.alpha));
        ctx.shadowBlur = currentAlpha * 8; 
        ctx.shadowColor = star.color;
        
        ctx.fillStyle = star.color;
        let currentSize = star.baseSize * (0.7 + currentAlpha * 0.5);
        
        ctx.beginPath();
        ctx.arc(star.x, star.y, currentSize, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // シャドウ設定を一度リセット
    ctx.shadowBlur = 0;

    // プレイヤーの移動
    if (useMouse) {
        player.x += (mouseX - player.x) * 0.1;
        player.y += (mouseY - player.y) * 0.1;
    } else {
        if (keys['ArrowUp'] || keys['w']) player.y -= player.speed;
        if (keys['ArrowDown'] || keys['s']) player.y += player.speed;
        if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
        if (keys['ArrowRight'] || keys['d']) player.x += player.speed;
    }

    // 画面外防止
    if (player.x < player.radius) player.x = player.radius;
    if (player.x > canvas.width - player.radius) player.x = canvas.width - player.radius;
    if (player.y < player.radius) player.y = player.radius;
    if (player.y > canvas.height - player.radius) player.y = canvas.height - player.radius;

    // ゲート（ゴール）の描画
    gate.pulse += 0.05;
    const glowSize = gate.radius + Math.sin(gate.pulse) * 5;
    ctx.beginPath();
    ctx.arc(gate.x, gate.y, glowSize, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(254, 240, 138, 0.3)';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(gate.x, gate.y, gate.radius, 0, Math.PI * 2);
    ctx.fillStyle = gate.color;
    ctx.fill();

    // プレイヤーの描画
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.radius + 4, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.4)';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
    ctx.fillStyle = player.color;
    ctx.fill();

    // 流れ星の追加と更新
    spawnShootingStar();
    shootingStars.forEach((star, index) => {
        star.x += star.vx;
        star.y += star.vy;

        // 流れ星（尾付き）を描画
        ctx.beginPath();
        ctx.moveTo(star.x - star.vx * 2, star.y - star.vy * 2);
        ctx.lineTo(star.x, star.y);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = star.width;
        ctx.stroke();

        // 衝突判定
        if (checkCollision(player, star)) {
            gameOver = true;
        }

        // 画面外の処理
        if (star.y > canvas.height || star.x < 0 || star.x > canvas.width) {
            shootingStars.splice(index, 1);
        }
    });

    // ゲートへの到達判定（ゴール！）
    const distToGate = Math.hypot(player.x - gate.x, player.y - gate.y);
    if (distToGate < player.radius + gate.radius) {
        score += 100;
        scoreDisplay.innerText = "Score: " + score;
        playGoalSound(); // ゴール時の効果音
        player.x = 300;
        player.y = 350;
    }

    requestAnimationFrame(animate);
}

animate();
</script>
"""

if __name__ == '__main__':
    # デスクトップ専用ウインドウを起動してアプリのように動かす設定
    webview.create_window(
        title="✨ Heaven's Gate Game ✨",
        html=html_content,
        width=650,
        height=520,
        resizable=False
    )
    webview.start()
