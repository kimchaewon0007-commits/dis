import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="BADMINTON GAME",
    page_icon="🏸",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: #eaf7ef;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1rem;
        max-width: 1100px;
    }

    h1 {
        text-align: center;
        color: #176b45;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏸 BADMINTON GAME")
st.markdown(
    "<p style='text-align:center;'>AI와 함께하는 배드민턴 대결!</p>",
    unsafe_allow_html=True
)

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    text-align: center;
    background: #eaf7ef;
}

#score {
    font-size: 26px;
    font-weight: bold;
    margin: 12px;
    color: #176b45;
}

canvas {
    background: #32956c;
    border: 5px solid #176b45;
    border-radius: 12px;
    max-width: 95%;
}

button {
    padding: 12px 25px;
    margin: 12px;
    background: #176b45;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background: #249c66;
}

#message {
    font-size: 18px;
    font-weight: bold;
    color: #176b45;
}
</style>
</head>

<body>

<div id="score">PLAYER 0 : 0 AI</div>

<canvas id="game" width="800" height="500" tabindex="0"></canvas>

<p id="message">시작 버튼을 눌러주세요!</p>

<button onclick="startGame()">게임 시작 / 다시 시작</button>

<p>🎮 방향키 또는 WASD 이동 | SPACE 스윙</p>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let running = false;
let playerScore = 0;
let aiScore = 0;

const keys = {};

const player = {
    x: 170,
    y: 250,
    radius: 22,
    speed: 5
};

const ai = {
    x: 630,
    y: 250,
    radius: 22,
    speed: 3.1
};

const shuttle = {
    x: 400,
    y: 250,
    vx: 0,
    vy: 0,
    radius: 9
};

let lastHit = null;
let swingRequested = false;
let rallyActive = false;

document.addEventListener("keydown", e => {
    keys[e.key.toLowerCase()] = true;

    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
        e.preventDefault();
    }

    if (e.code === "Space" && !e.repeat) {
        swingRequested = true;
    }
});

document.addEventListener("keyup", e => {
    keys[e.key.toLowerCase()] = false;
});

function startGame() {
    playerScore = 0;
    aiScore = 0;
    running = true;

    player.x = 170;
    player.y = 250;
    ai.x = 630;
    ai.y = 250;

    updateScore();
    serve("player");
    document.getElementById("message").innerText = "경기 시작!";
    canvas.focus();
}

function serve(side) {
    shuttle.x = 400;
    shuttle.y = 250;
    shuttle.vx = side === "player" ? 4 : -4;
    shuttle.vy = (Math.random() - 0.5) * 3;
    lastHit = side;
    rallyActive = true;
}

function updateScore() {
    document.getElementById("score").innerText =
        `PLAYER ${playerScore} : ${aiScore} AI`;
}

function checkWinner() {
    const maxScore = Math.max(playerScore, aiScore);
    const difference = Math.abs(playerScore - aiScore);

    if ((maxScore >= 21 && difference >= 2) || maxScore === 30) {
        running = false;
        rallyActive = false;

        document.getElementById("message").innerText =
            playerScore > aiScore
            ? "🏆 승리했습니다!"
            : "😢 AI가 승리했습니다!";

        return true;
    }

    return false;
}

function point(winner) {
    if (!rallyActive) return;

    rallyActive = false;

    if (winner === "player") {
        playerScore++;
    } else {
        aiScore++;
    }

    updateScore();

    if (!checkWinner()) {
        serve(winner);
    }
}

function movePlayer() {
    if (keys["arrowup"] || keys["w"]) player.y -= player.speed;
    if (keys["arrowdown"] || keys["s"]) player.y += player.speed;
    if (keys["arrowleft"] || keys["a"]) player.x -= player.speed;
    if (keys["arrowright"] || keys["d"]) player.x += player.speed;

    player.x = Math.max(35, Math.min(365, player.x));
    player.y = Math.max(35, Math.min(465, player.y));
}

function moveAI() {
    if (shuttle.vx > 0) {
        if (ai.y < shuttle.y - 8) ai.y += ai.speed;
        if (ai.y > shuttle.y + 8) ai.y -= ai.speed;

        if (ai.x < shuttle.x - 35) ai.x += ai.speed * 0.5;
        if (ai.x > shuttle.x + 35) ai.x -= ai.speed * 0.5;
    } else {
        ai.x += (630 - ai.x) * 0.025;
        ai.y += (250 - ai.y) * 0.025;
    }

    ai.x = Math.max(435, Math.min(765, ai.x));
    ai.y = Math.max(35, Math.min(465, ai.y));
}

function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
}

function updateShuttle() {
    if (!rallyActive) return;

    shuttle.x += shuttle.vx;
    shuttle.y += shuttle.vy;

    if (shuttle.y < 20 || shuttle.y > 480) {
        point(shuttle.x < 400 ? "ai" : "player");
        return;
    }

    if (shuttle.x < 15) {
        point("ai");
        return;
    }

    if (shuttle.x > 785) {
        point("player");
        return;
    }

    if (
        swingRequested &&
        lastHit !== "player" &&
        distance(player, shuttle) < 75
    ) {
        shuttle.vx = 5.5;
        shuttle.vy = (shuttle.y - player.y) * 0.055;
        lastHit = "player";
    }

    if (
        lastHit !== "ai" &&
        shuttle.vx > 0 &&
        distance(ai, shuttle) < 58
    ) {
        shuttle.vx = -4.5 - Math.random() * 1.5;
        shuttle.vy = (Math.random() - 0.5) * 5;
        lastHit = "ai";
    }
}

function drawCourt() {
    ctx.fillStyle = "#32956c";
    ctx.fillRect(0, 0, 800, 500);

    ctx.strokeStyle = "white";
    ctx.lineWidth = 3;

    ctx.strokeRect(20, 20, 760, 460);

    ctx.beginPath();
    ctx.moveTo(400, 20);
    ctx.lineTo(400, 480);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(20, 250);
    ctx.lineTo(780, 250);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(260, 20);
    ctx.lineTo(260, 480);
    ctx.moveTo(540, 20);
    ctx.lineTo(540, 480);
    ctx.stroke();

    ctx.fillStyle = "rgba(255,255,255,0.15)";
    ctx.fillRect(392, 20, 16, 460);
}

function drawPlayer(obj, color, label) {
    ctx.beginPath();
    ctx.arc(obj.x, obj.y, obj.radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

    ctx.fillStyle = "white";
    ctx.font = "bold 13px Arial";
    ctx.textAlign = "center";
    ctx.fillText(label, obj.x, obj.y + 5);
}

function drawShuttle() {
    ctx.save();
    ctx.translate(shuttle.x, shuttle.y);

    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.ellipse(0, 0, 12, 7, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#f5d76e";
    ctx.beginPath();
    ctx.arc(-8, 0, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
}

function draw() {
    drawCourt();
    drawPlayer(player, "#2775e7", "YOU");
    drawPlayer(ai, "#ef5350", "AI");
    drawShuttle();
}

function gameLoop() {
    if (running) {
        movePlayer();
        moveAI();
        updateShuttle();
    }

    swingRequested = false;
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>

</body>
</html>
"""

components.html(game_html, height=680)
