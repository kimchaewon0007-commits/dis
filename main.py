import streamlit as st
import streamlit.components.v1 as components
import json

# =========================================================
# 1. STREAMLIT 기본 설정
# =========================================================

st.set_page_config(
    page_title="BADMINTON 3D",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PLAYERS = [
    "도예슬",
    "전주연",
    "이보윤",
    "이효민",
    "방서영",
    "이주은",
    "김지아",
    "방민채",
    "김채원",
    "설하은",
    "김성원",
    "고지민"
]

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(
            135deg,
            #e8f7ee,
            #f6fff9
        );
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1rem;
        max-width: 1500px;
    }

    h1 {
        color: #176b45;
        text-align: center;
        font-weight: 800;
    }

    .subtitle {
        text-align: center;
        color: #54816a;
        font-size: 17px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏸 BADMINTON 3D")
st.markdown(
    '<div class="subtitle">'
    '친구들과 함께하는 3D 배드민턴 복식 게임'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# 2. 3D 게임 HTML
# =========================================================

game_html = r"""
<!DOCTYPE html>
<html lang="ko">

<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #eaf7ef;
    font-family: Arial, sans-serif;
    color: #174d35;
}

#topPanel {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    background: white;
    border-radius: 15px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

#topPanel h2 {
    margin: 0;
    font-size: 20px;
}

button, select {
    padding: 10px 14px;
    border-radius: 9px;
    border: 1px solid #b6d9c4;
    font-size: 14px;
}

button {
    background: #176b45;
    color: white;
    cursor: pointer;
    font-weight: bold;
}

button:hover {
    background: #259664;
}

button:disabled {
    background: #9bb9aa;
    cursor: not-allowed;
}

#gameContainer {
    width: 100%;
    height: 570px;
    position: relative;
    background: #dceee3;
    overflow: hidden;
    border-radius: 16px;
    border: 3px solid #b4d8c2;
}

#gameContainer canvas {
    display: block;
}

#scorePanel {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 12px;
}

.scoreCard {
    background: white;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    border: 2px solid #d3e9da;
    cursor: pointer;
}

.scoreCard.active {
    border-color: #176b45;
    background: #f0fff5;
}

.scoreTitle {
    font-weight: bold;
    color: #176b45;
    margin-bottom: 7px;
}

.scoreNumber {
    font-size: 25px;
    font-weight: bold;
}

.teamNames {
    font-size: 12px;
    margin-top: 6px;
    color: #60776b;
    line-height: 1.6;
}

#message {
    background: white;
    padding: 12px;
    margin-top: 10px;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
}

#help {
    text-align: center;
    padding: 12px;
    color: #426b54;
    font-size: 14px;
}

#loading {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eaf7ef;
    font-weight: bold;
    z-index: 10;
}

@media (max-width: 700px) {
    #scorePanel {
        grid-template-columns: 1fr;
    }

    #gameContainer {
        height: 450px;
    }
}
</style>

</head>

<body>

<div id="topPanel">
    <h2>🏸 BADMINTON ARENA</h2>

    <div>
        <label for="playerSelect">내 캐릭터</label>
        <select id="playerSelect"></select>
    </div>

    <div>
        <button id="randomButton">🎲 랜덤 팀 배정</button>
        <button id="startButton">▶ 경기 시작</button>
        <button id="pauseButton">⏸ 일시정지</button>
        <button id="resetButton">↻ 초기화</button>
    </div>
</div>

<div id="gameContainer">
    <div id="loading">3D 체육관을 불러오는 중...</div>
</div>

<div id="scorePanel"></div>

<div id="message">
    캐릭터를 선택하고 랜덤 팀 배정을 눌러주세요!
</div>

<div id="help">
    WASD / 방향키 : 이동 |
    SPACE : 타격 |
    1 : 클리어 |
    2 : 드롭 |
    3 : 스매시 |
    V : 카메라 전환
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<script>

// =========================================================
// 3. 선수 명단
// =========================================================

const PLAYER_NAMES = __PLAYERS_JSON__;

const COURT_COUNT = 3;
const COURT_WIDTH = 6.1;
const COURT_LENGTH = 13.4;
const COURT_SPACING = 8.5;

let selectedPlayer = PLAYER_NAMES[0];
let assignments = [];
let courts = [];
let characters = [];

let running = false;
let paused = false;
let cameraMode = "all";

let currentShot = "clear";
let swingRequested = false;

const keys = {};

const container = document.getElementById("gameContainer");
const messageBox = document.getElementById("message");
const select = document.getElementById("playerSelect");

// =========================================================
// 4. 선수 선택 메뉴
// =========================================================

PLAYER_NAMES.forEach(name => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
});

select.addEventListener("change", () => {
    selectedPlayer = select.value;
    running = false;
    paused = false;
    randomTeams();
});

// =========================================================
// 5. THREE.JS 기본 환경
// =========================================================

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe5f2e9);

const camera = new THREE.PerspectiveCamera(
    55,
    1,
    0.1,
    200
);

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setPixelRatio(
    Math.min(window.devicePixelRatio || 1, 2)
);

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

container.appendChild(renderer.domElement);

const clock = new THREE.Clock();

function resizeGame() {
    const width = container.clientWidth;
    const height = container.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
}

window.addEventListener("resize", resizeGame);
resizeGame();

document.getElementById("loading").style.display = "none";

// =========================================================
// 6. 조명
// =========================================================

const ambientLight = new THREE.AmbientLight(
    0xffffff,
    0.65
);
scene.add(ambientLight);

const sunlight = new THREE.DirectionalLight(
    0xffffff,
    1.0
);

sunlight.position.set(10, 25, 12);
sunlight.castShadow = true;

sunlight.shadow.mapSize.width = 2048;
sunlight.shadow.mapSize.height = 2048;

sunlight.shadow.camera.left = -25;
sunlight.shadow.camera.right = 25;
sunlight.shadow.camera.top = 25;
sunlight.shadow.camera.bottom = -25;

scene.add(sunlight);

// =========================================================
// 7. 재질 생성
// =========================================================

function material(color) {
    return new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.75
    });
}

const floorMaterial = material(0xd4b995);
const wallMaterial = material(0xf4f8f5);
const courtMaterial = material(0x258b66);
const lineMaterial = material(0xffffff);
const netMaterial = material(0xe8eeee);

// =========================================================
// 8. 기본 3D 물체 생성
// =========================================================

function createBox(w, h, d, mat, x, y, z, parent=scene) {
    const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(w, h, d),
        mat
    );

    mesh.position.set(x, y, z);
    mesh.receiveShadow = true;
    mesh.castShadow = true;

    parent.add(mesh);

    return mesh;
}

function createSphere(radius, mat, x, y, z, parent=scene) {
    const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(radius, 16, 12),
        mat
    );

    mesh.position.set(x, y, z);
    mesh.castShadow = true;

    parent.add(mesh);

    return mesh;
}

// =========================================================
// 9. 체육관 생성
// =========================================================

function createGym() {

    createBox(
        34, 0.3, 23,
        floorMaterial,
        0, -0.2, 0
    );

    createBox(
        34, 12, 0.3,
        wallMaterial,
        0, 6, -11.5
    );

    createBox(
        34, 12, 0.3,
        wallMaterial,
        0, 6, 11.5
    );

    createBox(
        0.3, 12, 23,
        wallMaterial,
        -17, 6, 0
    );

    createBox(
        0.3, 12, 23,
        wallMaterial,
        17, 6, 0
    );

    for (let i = -2; i <= 2; i++) {
        const light = new THREE.PointLight(
            0xffffff,
            0.35,
            25
        );

        light.position.set(i * 6, 9, 0);
        scene.add(light);
    }
}

createGym();

// =========================================================
// 10. 코트 생성
// =========================================================

function createCourt(index) {

    const centerX = (index - 1) * COURT_SPACING;

    const group = new THREE.Group();
    group.position.x = centerX;
    scene.add(group);

    createBox(
        COURT_WIDTH,
        0.04,
        COURT_LENGTH,
        courtMaterial,
        0, 0.02, 0,
        group
    );

    // 코트 외곽선
    createBox(
        COURT_WIDTH,
        0.015,
        0.055,
        lineMaterial,
        0, 0.055, -COURT_LENGTH / 2,
        group
    );

    createBox(
        COURT_WIDTH,
        0.015,
        0.055,
        lineMaterial,
        0, 0.055, COURT_LENGTH / 2,
        group
    );

    for (const x of [-COURT_WIDTH / 2, COURT_WIDTH / 2]) {
        createBox(
            0.055,
            0.015,
            COURT_LENGTH,
            lineMaterial,
            x, 0.055, 0,
            group
        );
    }

    // 복식 서비스 라인
    for (const z of [-1.98, 1.98, -5.94, 5.94]) {
        createBox(
            COURT_WIDTH,
            0.015,
            0.045,
            lineMaterial,
            0, 0.055, z,
            group
        );
    }

    // 중앙 서비스 라인
    for (const side of [-1, 1]) {
        createBox(
            0.045,
            0.015,
            3.96,
            lineMaterial,
            0,
            0.055,
            side * 3.96,
            group
        );
    }

    // 네트 기둥
    for (const x of [-3.05, 3.05]) {
        createBox(
            0.08,
            1.55,
            0.08,
            material(0x333333),
            x, 0.775, 0,
            group
        );
    }

    // 네트
    const net = createBox(
        6.1,
        0.76,
        0.025,
        new THREE.MeshStandardMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.48,
            side: THREE.DoubleSide
        }),
        0, 1.14, 0,
        group
    );

    // 네트 상단 테이프
    createBox(
        6.1,
        0.055,
        0.055,
        lineMaterial,
        0, 1.53, 0,
        group
    );

    return {
        index: index,
        centerX: centerX,
        group: group,
        score: [0, 0],
        rally: null,
        finished: false,
        players: [],
        shuttle: null,
        lastHitter: null
    };
}

for (let i = 0; i < COURT_COUNT; i++) {
    courts.push(createCourt(i));
}

// =========================================================
// 11. 이름표 생성
// =========================================================

function createNameLabel(name) {

    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 64;

    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "rgba(255,255,255,0.92)";
    ctx.fillRect(0, 0, 256, 64);

    ctx.fillStyle = "#174d35";
    ctx.font = "bold 30px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(name, 128, 32);

    const texture = new THREE.CanvasTexture(canvas);

    const sprite = new THREE.Sprite(
        new THREE.SpriteMaterial({
            map: texture,
            transparent: true,
            depthTest: false
        })
    );

    sprite.scale.set(1.6, 0.4, 1);

    return sprite;
}

// =========================================================
// 12. 3D 사람 캐릭터
// =========================================================

function createCharacter(name, team, courtIndex, slot) {

    const court = courts[courtIndex];
    const group = new THREE.Group();

    const shirtColor = team === 0
        ? 0x3478e5
        : 0xf05b59;

    const shirtMaterial = material(shirtColor);
    const skinMaterial = material(0xf0c49c);
    const pantsMaterial = material(0x263b45);
    const shoeMaterial = material(0xffffff);

    // 몸통
    createBox(
        0.42, 0.65, 0.25,
        shirtMaterial,
        0, 1.05, 0,
        group
    );

    // 머리
    createSphere(
        0.22,
        skinMaterial,
        0, 1.65, 0,
        group
    );

    // 머리카락
    createSphere(
        0.225,
        material(0x30251e),
        0, 1.76, -0.025,
        group
    );

    // 팔
    createBox(
        0.16, 0.55, 0.16,
        skinMaterial,
        -0.32, 1.08, 0,
        group
    );

    createBox(
        0.16, 0.55, 0.16,
        skinMaterial,
        0.32, 1.08, 0,
        group
    );

    // 다리
    createBox(
        0.18, 0.65, 0.2,
        pantsMaterial,
        -0.13, 0.42, 0,
        group
    );

    createBox(
        0.18, 0.65, 0.2,
        pantsMaterial,
        0.13, 0.42, 0,
        group
    );

    // 신발
    createBox(
        0.22, 0.13, 0.36,
        shoeMaterial,
        -0.13, 0.07, 0.08,
        group
    );

    createBox(
        0.22, 0.13, 0.36,
        shoeMaterial,
        0.13, 0.07, 0.08,
        group
    );

    // 라켓
    const racket = new THREE.Group();

    createBox(
        0.045, 0.7, 0.045,
        material(0x333333),
        0, 0.35, 0,
        racket
    );

    const racketHead = new THREE.Mesh(
        new THREE.TorusGeometry(
            0.22, 0.025, 8, 24
        ),
        material(0xd8e4e8)
    );

    racketHead.position.y = 0.85;
    racket.add(racketHead);

    racket.position.set(0.43, 1.05, 0);
    group.add(racket);

    // 이름표
    const label = createNameLabel(name);
    label.position.y = 2.2;
    group.add(label);

    // 기본 위치
    const side = team === 0 ? 1 : -1;
    const lane = slot % 2 === 0 ? -1.25 : 1.25;

    group.position.set(
        court.centerX + lane,
        0,
        side * 3.6
    );

    if (team === 1) {
        group.rotation.y = Math.PI;
    }

    scene.add(group);

    return {
        name: name,
        team: team,
        courtIndex: courtIndex,
        group: group,
        racket: racket,
        speed: 4.0,
        isHuman: name === selectedPlayer,
        swingTime: 0,
        hitCooldown: 0,
        homeX: group.position.x,
        homeZ: group.position.z
    };
}

// =========================================================
// 13. 셔틀콕 생성
// =========================================================

function createShuttle(courtIndex) {

    const group = new THREE.Group();

    const cork = createSphere(
        0.09,
        material(0xf3d38b),
        0, 0, 0,
        group
    );

    const featherMaterial = material(0xffffff);

    for (let i = 0; i < 8; i++) {

        const angle = i * Math.PI / 4;

        const feather = new THREE.Mesh(
            new THREE.ConeGeometry(0.06, 0.28, 5),
            featherMaterial
        );

        feather.position.set(
            Math.cos(angle) * 0.11,
            0.15,
            Math.sin(angle) * 0.11
        );

        feather.rotation.z = Math.cos(angle) * 0.35;
        feather.rotation.x = Math.sin(angle) * 0.35;

        group.add(feather);
    }

    group.position.set(
        courts[courtIndex].centerX,
        2,
        0
    );

    scene.add(group);

    return {
        group: group,
        vx: 0,
        vy: 0,
        vz: 0,
        active: false,
        hitterTeam: null
    };
}

// =========================================================
// 14. 랜덤 팀 편성
// =========================================================

function shuffleArray(array) {

    const result = [...array];

    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));

        [result[i], result[j]] = [
            result[j], result[i]
        ];
    }

    return result;
}

function clearCharacters() {

    characters.forEach(character => {
        scene.remove(character.group);

        character.group.traverse(obj => {
            if (obj.geometry) obj.geometry.dispose();

            if (obj.material) {
                const mats = Array.isArray(obj.material)
                    ? obj.material
                    : [obj.material];

                mats.forEach(mat => {
                    if (mat.map) mat.map.dispose();
                    mat.dispose();
                });
            }
        });
    });

    characters = [];

    courts.forEach(court => {

        if (court.shuttle) {
            scene.remove(court.shuttle.group);
        }

        court.players = [];
        court.shuttle = null;
        court.score = [0, 0];
        court.finished = false;
        court.rally = null;
        court.lastHitter = null;
    });
}

function randomTeams() {

    running = false;
    paused = false;

    clearCharacters();

    const others = PLAYER_NAMES.filter(
        name => name !== selectedPlayer
    );

    const shuffled = shuffleArray(others);

    // 선택한 선수는 항상 1번 코트 첫 번째 팀
    const ordered = [
        selectedPlayer,
        ...shuffled
    ];

    assignments = [];

    for (let c = 0; c < 3; c++) {

        const names = ordered.slice(c * 4, c * 4 + 4);

        const assignment = {
            court: c,
            teamA: names.slice(0, 2),
            teamB: names.slice(2, 4)
        };

        assignments.push(assignment);

        names.forEach((name, i) => {

            const team = i < 2 ? 0 : 1;

            const character = createCharacter(
                name,
                team,
                c,
                i
            );

            characters.push(character);
            courts[c].players.push(character);
        });

        courts[c].shuttle = createShuttle(c);
    }

    updateScorePanel();

    setMessage(
        "🎲 랜덤 팀 배정 완료! 경기 시작을 눌러주세요."
    );

    setCamera("all");
}

// =========================================================
// 15. 점수판
// =========================================================

function updateScorePanel() {

    const panel = document.getElementById("scorePanel");
    panel.innerHTML = "";

    courts.forEach((court, index) => {

        const data = assignments[index];

        const card = document.createElement("div");
        card.className = "scoreCard";

        if (cameraMode === index) {
            card.classList.add("active");
        }

        const title = document.createElement("div");
        title.className = "scoreTitle";
        title.textContent = `${index + 1}번 코트`;

        const score = document.createElement("div");
        score.className = "scoreNumber";
        score.textContent =
            `${court.score[0]} : ${court.score[1]}`;

        const names = document.createElement("div");
        names.className = "teamNames";

        names.textContent =
            `${data.teamA.join(" · ")} VS ${data.teamB.join(" · ")}`;

        card.appendChild(title);
        card.appendChild(score);
        card.appendChild(names);

        card.addEventListener("click", () => {
            setCamera(index);
        });

        panel.appendChild(card);
    });
}

// =========================================================
// 16. 카메라
// =========================================================

function setCamera(mode) {

    cameraMode = mode;

    if (mode === "all") {

        camera.position.set(0, 28, 28);
        camera.lookAt(0, 0, 0);

    } else {

        const court = courts[mode];

        camera.position.set(
            court.centerX,
            13,
            14
        );

        camera.lookAt(
            court.centerX,
            0,
            0
        );
    }

    updateScorePanel();
}

// =========================================================
// 17. 키보드 조작
// =========================================================

document.addEventListener("keydown", event => {

    const key = event.key.toLowerCase();
    keys[key] = true;

    if (
        ["ArrowUp", "ArrowDown", "ArrowLeft",
         "ArrowRight", "Space"].includes(event.code)
    ) {
        event.preventDefault();
    }

    if (event.repeat) return;

    if (event.code === "Space") {
        swingRequested = true;
    }

    if (event.code === "Digit1") {
        currentShot = "clear";
        setMessage("🏸 클리어 선택");
    }

    if (event.code === "Digit2") {
        currentShot = "drop";
        setMessage("🏸 드롭 선택");
    }

    if (event.code === "Digit3") {
        currentShot = "smash";
        setMessage("💥 스매시 선택");
    }

    if (event.code === "KeyV") {
        setCamera(cameraMode === "all" ? 0 : "all");
    }
});

document.addEventListener("keyup", event => {
    keys[event.key.toLowerCase()] = false;
});

// =========================================================
// 18. 플레이어 이동
// =========================================================

function moveHuman(character, dt) {

    let dx = 0;
    let dz = 0;

    if (keys["w"] || keys["arrowup"]) dz -= 1;
    if (keys["s"] || keys["arrowdown"]) dz += 1;
    if (keys["a"] || keys["arrowleft"]) dx -= 1;
    if (keys["d"] || keys["arrowright"]) dx += 1;

    const length = Math.hypot(dx, dz);

    if (length > 0) {
        dx /= length;
        dz /= length;
    }

    const speed = character.speed * dt;

    character.group.position.x += dx * speed;
    character.group.position.z += dz * speed;

    const court = courts[character.courtIndex];

    character.group.position.x = THREE.MathUtils.clamp(
        character.group.position.x,
        court.centerX - 2.85,
        court.centerX + 2.85
    );

    character.group.position.z = THREE.MathUtils.clamp(
        character.group.position.z,
        0.45,
        6.4
    );

    if (swingRequested) {
        character.swingTime = 0.25;
    }
}

// =========================================================
// 19. AI 이동
// =========================================================

function moveAI(character, dt) {

    const court = courts[character.courtIndex];
    const shuttle = court.shuttle;

    let targetX = character.homeX;
    let targetZ = character.homeZ;

    if (shuttle && shuttle.active) {

        const shuttleZ = shuttle.group.position.z;

        const shuttleOnSide =
            character.team === 0
                ? shuttleZ > 0
                : shuttleZ < 0;

        if (shuttleOnSide) {

            const teammates = court.players.filter(
                p => p.team === character.team
            );

            const nearest = teammates.reduce((best, p) => {

                const d = Math.hypot(
                    p.group.position.x - shuttle.group.position.x,
                    p.group.position.z - shuttleZ
                );

                if (!best || d < best.distance) {
                    return {
                        player: p,
                        distance: d
                    };
                }

                return best;

            }, null);

            if (
                nearest &&
                nearest.player === character
            ) {
                targetX = shuttle.group.position.x;
                targetZ = shuttleZ;
            }
        }
    }

    const position = character.group.position;

    const dx = targetX - position.x;
    const dz = targetZ - position.z;

    const distance = Math.hypot(dx, dz);

    if (distance > 0.05) {

        const step = Math.min(
            character.speed * 0.72 * dt,
            distance
        );

        position.x += dx / distance * step;
        position.z += dz / distance * step;
    }

    position.x = THREE.MathUtils.clamp(
        position.x,
        court.centerX - 2.85,
        court.centerX + 2.85
    );

    if (character.team === 0) {
        position.z = THREE.MathUtils.clamp(
            position.z, 0.45, 6.4
        );
    } else {
        position.z = THREE.MathUtils.clamp(
            position.z, -6.4, -0.45
        );
    }
}

// =========================================================
// 20. 타격 애니메이션
// =========================================================

function animateCharacter(character, dt) {

    if (character.hitCooldown > 0) {
        character.hitCooldown -= dt;
    }

    if (character.swingTime > 0) {

        character.swingTime -= dt;

        const progress =
            1 - character.swingTime / 0.25;

        character.racket.rotation.z =
            Math.sin(progress * Math.PI) * -1.4;

    } else {
        character.racket.rotation.z = 0;
    }
}

// =========================================================
// 21. 셔틀콕 타격
// =========================================================

function hitShuttle(character, shotType) {

    const court = courts[character.courtIndex];
    const shuttle = court.shuttle;

    if (!shuttle || !shuttle.active) return;

    if (character.hitCooldown > 0) return;

    if (shuttle.hitterTeam === character.team) return;

    const p = character.group.position;
    const s = shuttle.group.position;

    const horizontalDistance = Math.hypot(
        p.x - s.x,
        p.z - s.z
    );

    if (horizontalDistance > 1.25) return;
    if (s.y > 2.6 || s.y < 0.3) return;

    character.hitCooldown = 0.6;
    character.swingTime = 0.25;

    const direction = character.team === 0 ? -1 : 1;

    let speedZ;
    let speedY;

    if (shotType === "smash") {
        speedZ = 13;
        speedY = 1.5;
    } else if (shotType === "drop") {
        speedZ = 5.5;
        speedY = 4.2;
    } else {
        speedZ = 8.5;
        speedY = 8.0;
    }

    shuttle.vz = direction * speedZ;
    shuttle.vy = speedY;

    const targetX =
        court.centerX + (Math.random() - 0.5) * 3.8;

    shuttle.vx = (targetX - s.x) * 1.5;

    shuttle.hitterTeam = character.team;
    court.lastHitter = character.name;
}

// =========================================================
// 22. AI 타격
// =========================================================

function aiHit(character) {

    const court = courts[character.courtIndex];
    const shuttle = court.shuttle;

    if (!shuttle || !shuttle.active) return;

    if (shuttle.hitterTeam === character.team) return;

    const p = character.group.position;
    const s = shuttle.group.position;

    const distance = Math.hypot(
        p.x - s.x,
        p.z - s.z
    );

    if (
        distance < 1.1 &&
        s.y > 0.4 &&
        s.y < 2.5
    ) {

        const random = Math.random();

        let shot = "clear";

        if (random < 0.25) {
            shot = "smash";
        } else if (random < 0.5) {
            shot = "drop";
        }

        hitShuttle(character, shot);
    }
}

// =========================================================
// 23. 서브
// =========================================================

function serve(court, team) {

    if (court.finished) return;

    const shuttle = court.shuttle;

    const direction = team === 0 ? -1 : 1;

    shuttle.group.position.set(
        court.centerX,
        1.5,
        team === 0 ? 3.0 : -3.0
    );

    shuttle.vx = (Math.random() - 0.5) * 1.5;
    shuttle.vy = 4.5;
    shuttle.vz = direction * 6.5;

    shuttle.active = true;
    shuttle.hitterTeam = team;

    court.rally = true;
}

// =========================================================
// 24. 점수 계산
// =========================================================

function addPoint(court, team) {

    if (!court.rally) return;

    court.rally = false;
    court.shuttle.active = false;

    court.score[team]++;

    updateScorePanel();

    const a = court.score[0];
    const b = court.score[1];

    const maxScore = Math.max(a, b);
    const difference = Math.abs(a - b);

    if (
        (maxScore >= 21 && difference >= 2) ||
        maxScore === 30
    ) {

        court.finished = true;

        const winner = team === 0
            ? assignments[court.index].teamA
            : assignments[court.index].teamB;

        setMessage(
            `🏆 ${court.index + 1}번 코트 승리: ${winner.join(" & ")}`
        );

        if (courts.every(c => c.finished)) {
            running = false;
            setMessage("🏆 모든 코트의 경기가 종료되었습니다!");
        }

        return;
    }

    serve(court, team);
}

// =========================================================
// 25. 셔틀콕 물리
// =========================================================

function updateShuttle(court, dt) {

    const shuttle = court.shuttle;

    if (!shuttle || !shuttle.active) return;

    const p = shuttle.group.position;

    shuttle.vy -= 9.8 * dt;

    p.x += shuttle.vx * dt;
    p.y += shuttle.vy * dt;
    p.z += shuttle.vz * dt;

    shuttle.group.rotation.x += dt * 8;

    // 네트 충돌 단순 판정
    if (
        Math.abs(p.z) < 0.12 &&
        p.y < 1.55
    ) {
        addPoint(court, 1 - shuttle.hitterTeam);
        return;
    }

    // 바닥 착지
    if (p.y <= 0.1) {

        let winner;

        if (p.z > 0) {
            winner = 1;
        } else {
            winner = 0;
        }

        // 코트 밖이면 마지막 타격 팀의 상대가 득점
        if (
            Math.abs(p.x - court.centerX) > 3.05 ||
            Math.abs(p.z) > 6.7
        ) {
            winner = 1 - shuttle.hitterTeam;
        }

        addPoint(court, winner);
    }
}

// =========================================================
// 26. 경기 시작 / 정지 / 초기화
// =========================================================

function startGame() {

    if (running && paused) {
        paused = false;
        setMessage("▶ 경기를 재개했습니다.");
        return;
    }

    if (running) return;

    running = true;
    paused = false;

    courts.forEach(court => {
        court.score = [0, 0];
        court.finished = false;
        court.rally = null;
        serve(court, Math.random() < 0.5 ? 0 : 1);
    });

    setCamera(0);
    updateScorePanel();

    setMessage(
        `🏸 경기 시작! ${selectedPlayer} 캐릭터를 조작하세요.`
    );
}

function pauseGame() {

    if (!running) return;

    paused = !paused;

    setMessage(
        paused
            ? "⏸ 경기가 일시정지되었습니다."
            : "▶ 경기가 재개되었습니다."
    );
}

function resetGame() {

    running = false;
    paused = false;

    randomTeams();

    setMessage("↻ 게임이 초기화되었습니다.");
}

// =========================================================
// 27. 메시지
// =========================================================

function setMessage(text) {
    messageBox.textContent = text;
}

// =========================================================
// 28. 버튼 연결
// =========================================================

document.getElementById("randomButton")
    .addEventListener("click", randomTeams);

document.getElementById("startButton")
    .addEventListener("click", startGame);

document.getElementById("pauseButton")
    .addEventListener("click", pauseGame);

document.getElementById("resetButton")
    .addEventListener("click", resetGame);

// =========================================================
// 29. 게임 업데이트
// =========================================================

function update(dt) {

    if (!running || paused) return;

    characters.forEach(character => {

        const court = courts[character.courtIndex];

        if (court.finished) return;

        if (character.isHuman) {

            moveHuman(character, dt);

            if (swingRequested) {
                hitShuttle(character, currentShot);
            }

        } else {

            moveAI(character, dt);
            aiHit(character);
        }

        animateCharacter(character, dt);
    });

    courts.forEach(court => {

        if (!court.finished) {
            updateShuttle(court, dt);
        }
    });

    swingRequested = false;
}

// =========================================================
// 30. 애니메이션 루프
// =========================================================

function animate() {

    requestAnimationFrame(animate);

    const dt = Math.min(clock.getDelta(), 0.05);

    update(dt);

    renderer.render(scene, camera);
}

// =========================================================
// 31. 게임 최초 실행
// =========================================================

randomTeams();
setCamera("all");
animate();

</script>

</body>
</html>
"""

# =========================================================
# 32. Python 선수 데이터 전달
# =========================================================

game_html = game_html.replace(
    "__PLAYERS_JSON__",
    json.dumps(PLAYERS, ensure_ascii=False)
)

# =========================================================
# 33. 게임 화면 출력
# =========================================================

components.html(
    game_html,
    height=850,
    scrolling=True
)
