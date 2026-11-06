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
        background: #e9f6ef;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0.5rem 1rem !important;
    }

    h1 {
        color: #176b45;
        text-align: center;
        font-weight: 800;
        font-size: 2rem !important;
    }

    .subtitle {
        text-align: center;
        color: #54816a;
        font-size: 17px;
        margin-bottom: 12px;
    }

    iframe {
        width: 100% !important;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

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
    height: 800px;
    position: relative;
    background: #b9d6ca;
    overflow: hidden;
    border-radius: 16px;
    border: 3px solid #88bca0;
}

#gameContainer:focus {
    outline: 3px solid #176b45;
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

<div id="gameContainer" tabindex="0">
    <div id="loading">3D 체육관을 불러오는 중...</div>
</div>

<div id="scorePanel"></div>

<div id="message">
    캐릭터를 선택하고 랜덤 팀 배정을 눌러주세요!
</div>

<div id="help">
    🎮 WASD : 이동 |
    🦘 SPACE : 점프 |
    🏸 왼쪽 마우스 드래그 : 라켓 휘두르기 |
    📷 오른쪽 마우스 드래그 : 카메라 회전 |
    🔍 마우스 휠 : 확대·축소 |
    ENTER : 보조 타격 |
    1 : 클리어 |
    2 : 드롭 |
    3 : 스매시 |
    V : 카메라 전환
</div>

<script>
window.addEventListener("error", function(event) {
    const loading = document.getElementById("loading");

    if (loading) {
        loading.style.display = "flex";
        loading.style.color = "red";
        loading.style.padding = "30px";
        loading.style.textAlign = "center";

        loading.textContent =
            "게임 오류: " + event.message;
    }
});
</script>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>

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
let jumpRequested = false;

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
    if (mode !== "all") {

        cameraYaw = 0;
        cameraPitch = 0.65;
        cameraDistance = 14;
    }

    camera.updateProjectionMatrix();

    updateScorePanel();
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

    // 체육관 바닥
    createBox(
        34, 0.3, 23,
        floorMaterial,
        0, -0.2, 0
    );

    // 체육관 뒤쪽 벽
    createBox(
        34, 8, 0.3,
        wallMaterial,
        0, 4, -11.5
    );

    // 양쪽 벽
    createBox(
        0.3, 8, 23,
        wallMaterial,
        -17, 4, 0
    );

    createBox(
        0.3, 8, 23,
        wallMaterial,
        17, 4, 0
    );

    // 앞쪽 벽은 카메라 시야 확보를 위해 제거

    // 체육관 조명
    for (let i = -2; i <= 2; i++) {

        const light = new THREE.PointLight(
            0xffffff,
            0.7,
            30
        );

        light.position.set(i * 6, 7.5, 0);

        scene.add(light);

        // 천장 조명 모형
        createBox(
            2.5,
            0.08,
            0.6,
            material(0xffffff),
            i * 6,
            8,
            0
        );
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

    // 왼팔: 어깨를 중심으로 회전
    const leftShoulder = new THREE.Group();
    leftShoulder.position.set(-0.30, 1.32, 0);
    group.add(leftShoulder);

    createBox(
        0.15, 0.42, 0.15,
        skinMaterial,
        0, -0.21, 0,
        leftShoulder
    );

    // 오른팔: 어깨 관절
    const rightShoulder = new THREE.Group();
    rightShoulder.position.set(0.30, 1.32, 0);
    group.add(rightShoulder);

    createBox(
        0.15, 0.38, 0.15,
        skinMaterial,
        0, -0.19, 0,
        rightShoulder
    );

    // 오른쪽 팔꿈치 관절
    const rightElbow = new THREE.Group();
    rightElbow.position.set(0, -0.38, 0);
    rightShoulder.add(rightElbow);

    createSphere(
        0.09,
        skinMaterial,
        0, 0, 0,
        rightElbow
    );

    // 아래팔
    createBox(
        0.13, 0.36, 0.13,
        skinMaterial,
        0, -0.18, 0,
        rightElbow
    );

    // 손목 관절
    const rightWrist = new THREE.Group();
    rightWrist.position.set(0, -0.36, 0);
    rightElbow.add(rightWrist);

    createSphere(
        0.10,
        skinMaterial,
        0, 0, 0,
        rightWrist
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

    racket.position.set(0, -0.08, 0);
    rightWrist.add(racket);

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

        leftShoulder: leftShoulder,
        rightShoulder: rightShoulder,
        rightElbow: rightElbow,
        rightWrist: rightWrist,

        armAngle: 0,
        armVelocity: 0,
        targetArmAngle: 0,

        elbowAngle: 0,
        elbowVelocity: 0,

        wristAngle: 0,
        wristVelocity: 0,

        speed: name === selectedPlayer ? 8.0 : 4.0,
        isHuman: name === selectedPlayer,

        swingTime: 0,
        hitCooldown: 0,

        isJumping: false,
        jumpVelocity: 0,

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

        // 3개 코트를 한눈에 볼 수 있는 시점
        camera.position.set(
            0,
            22,
            19
        );

        camera.lookAt(
            0,
            0,
            0
        );

        camera.fov = 65;

    } else {

        const court = courts[mode];

        // 선택한 코트 확대
        camera.position.set(
            court.centerX,
            9,
            10
        );

        camera.lookAt(
            court.centerX,
            0.8,
            0
        );

        camera.fov = 50;
    }

    camera.updateProjectionMatrix();

    updateScorePanel();
}

// =========================================================
// 17. 키보드 조작
// =========================================================
const gameArea = document.getElementById("gameContainer");

gameArea.addEventListener("pointerdown", () => {
    gameArea.focus();
});

gameArea.addEventListener("keydown", event => {

    const key = event.key.toLowerCase();
    keys[key] = true;

    const blockedKeys = [
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "Space",
        "Enter"
    ];

    if (blockedKeys.includes(event.code)) {
        event.preventDefault();
    }

    if (event.repeat) return;

    // ENTER = 셔틀콕 치기
    if (event.code === "Enter") {
        swingRequested = true;
    }

    // SPACE = 점프
    if (event.code === "Space") {
        jumpRequested = true;
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
        setCamera(
            cameraMode === "all" ? 0 : "all"
        );
    }
});

gameArea.addEventListener("keyup", event => {
    keys[event.key.toLowerCase()] = false;
});

gameArea.addEventListener("blur", () => {

    Object.keys(keys).forEach(key => {
        keys[key] = false;
    });

    swingRequested = false;
});

// =========================================================
// 마우스 라켓 조작 + 카메라 조작
// =========================================================

let racketDragging = false;
let cameraDragging = false;

let lastMouseX = 0;
let lastMouseY = 0;

let racketPower = 0;
let racketDirection = 0;

let cameraYaw = 0;
let cameraPitch = 0.65;
let cameraDistance = 14;

let cameraTargetX = courts[0].centerX;

const clamp = THREE.MathUtils.clamp;

// 마우스 오른쪽 버튼 메뉴 방지
gameArea.addEventListener("contextmenu", event => {
    event.preventDefault();
});

// 마우스 버튼 누르기
gameArea.addEventListener("pointerdown", event => {

    gameArea.focus();

    lastMouseX = event.clientX;
    lastMouseY = event.clientY;

    if (event.button === 0) {
        racketDragging = true;
        racketPower = 0;
    }

    if (event.button === 2) {
        cameraDragging = true;
    }

    if (event.target.setPointerCapture) {
        event.target.setPointerCapture(event.pointerId);
    }
});

// 마우스 움직이기
gameArea.addEventListener("pointermove", event => {

    const dx = event.clientX - lastMouseX;
    const dy = event.clientY - lastMouseY;

    lastMouseX = event.clientX;
    lastMouseY = event.clientY;

    // 왼쪽 드래그: 라켓 움직이기
    if (racketDragging) {

        const player = characters.find(p => p.isHuman);

        if (player) {

            player.targetArmAngle = clamp(
                player.targetArmAngle + dx * 0.015,
                -2.2,
                2.2
            );

            racketDirection = dx;

            racketPower += Math.hypot(dx, dy) * 0.025;

            racketPower = clamp(
                racketPower,
                0,
                10
            );
        }
    }

    // 오른쪽 드래그: 카메라 회전
    if (cameraDragging) {

        cameraYaw -= dx * 0.006;

        cameraPitch = clamp(
            cameraPitch + dy * 0.005,
            0.2,
            1.35
        );
    }
});

// 마우스 버튼 놓기
gameArea.addEventListener("pointerup", event => {

    if (event.button === 0) {

        if (racketDragging) {

            const player = characters.find(p => p.isHuman);

            if (player && running && !paused) {

                // 너무 약하게 휘두르면 헛스윙
                if (racketPower >= 1.8) {

                    swingRequested = true;

                    player.swingTime = 0.25;

                } else {

                    setMessage("🏸 스윙이 너무 약했어요!");
                }
            }
        }

        racketDragging = false;
        racketPower = 0;
    }

    if (event.button === 2) {
        cameraDragging = false;
    }
});

gameArea.addEventListener("pointercancel", () => {
    racketDragging = false;
    cameraDragging = false;
    racketPower = 0;
});

// 마우스 휠: 확대 / 축소
gameArea.addEventListener("wheel", event => {

    event.preventDefault();

    cameraDistance = clamp(
        cameraDistance + event.deltaY * 0.015,
        6,
        32
    );

}, { passive: false });

// 카메라 위치 업데이트
function updateOrbitCamera() {

    if (cameraMode === "all") return;

    const court = courts[cameraMode];

    const target = new THREE.Vector3(
        court.centerX,
        0.8,
        0
    );

    const horizontal =
        cameraDistance * Math.cos(cameraPitch);

    camera.position.set(
        target.x + horizontal * Math.sin(cameraYaw),
        target.y + cameraDistance * Math.sin(cameraPitch),
        target.z + horizontal * Math.cos(cameraYaw)
    );

    camera.lookAt(target);
}

// =========================================================
// 18. 플레이어 이동
// =========================================================

function moveHuman(character, dt) {

    let dx = 0;
    let dz = 0;

    // 이동
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

    // SPACE를 누르면 점프
    if (jumpRequested && !character.isJumping) {
        character.isJumping = true;
        character.jumpVelocity = 6.5;
    }

    // 점프 중력 계산
    if (character.isJumping) {

        character.jumpVelocity -= 18 * dt;

        character.group.position.y +=
            character.jumpVelocity * dt;

        // 바닥 착지
        if (character.group.position.y <= 0) {

            character.group.position.y = 0;
            character.jumpVelocity = 0;
            character.isJumping = false;
        }
    }

    // ENTER를 누르면 라켓 휘두르기
    if (swingRequested) {
        character.swingTime = 0.25;
    }

    jumpRequested = false;
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

    // 프레임 변화에 따른 물리 계산 안정화
    const step = Math.min(dt, 0.033);

    // 어깨 관절: 탄성 + 감쇠
    const shoulderSpring = 34;
    const shoulderDamping = 7;

    const shoulderForce =
        (character.targetArmAngle - character.armAngle)
        * shoulderSpring;

    character.armVelocity +=
        shoulderForce * step;

    character.armVelocity *=
        Math.exp(-shoulderDamping * step);

    character.armAngle +=
        character.armVelocity * step;

    // 팔꿈치가 어깨 움직임을 늦게 따라감
    const elbowTarget =
        -0.45 + character.armAngle * 0.65;

    const elbowForce =
        (elbowTarget - character.elbowAngle) * 24;

    character.elbowVelocity += elbowForce * step;

    character.elbowVelocity *=
        Math.exp(-5 * step);

    character.elbowAngle +=
        character.elbowVelocity * step;

    // 손목은 더 부드럽게 흔들림
    const wristTarget =
        character.elbowAngle * -0.55;

    const wristForce =
        (wristTarget - character.wristAngle) * 18;

    character.wristVelocity += wristForce * step;

    character.wristVelocity *=
        Math.exp(-4 * step);

    character.wristAngle +=
        character.wristVelocity * step;

    // 실제 관절에 회전 적용
    character.rightShoulder.rotation.z =
        character.armAngle;

    character.rightElbow.rotation.z =
        character.elbowAngle;

    character.rightWrist.rotation.z =
        character.wristAngle;

    // 왼팔도 살짝 흔들리게
    character.leftShoulder.rotation.z =
        Math.sin(performance.now() * 0.003) * 0.12;

    // 라켓 타격 애니메이션
    if (character.swingTime > 0) {

        character.swingTime -= step;

        const progress = clamp(
            1 - character.swingTime / 0.25,
            0,
            1
        );

        character.rightShoulder.rotation.x =
            -Math.sin(progress * Math.PI) * 1.4;

        character.rightWrist.rotation.x =
            -Math.sin(progress * Math.PI) * 0.9;

    } else {

        character.rightShoulder.rotation.x *= 0.85;
        character.rightWrist.rotation.x *= 0.85;
    }

    // 사용자가 드래그하지 않으면 팔이 원위치로 복귀
    if (character.isHuman && !racketDragging) {
        character.targetArmAngle *=
            Math.exp(-2.5 * step);
    }

    // AI는 자연스럽게 팔 움직이기
    if (!character.isHuman) {

        character.targetArmAngle =
            Math.sin(performance.now() * 0.002
            + character.courtIndex) * 0.15;
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

    // 라켓 타격 범위 축소
    if (horizontalDistance > 0.95) return;

    // 타격 가능한 높이 제한
    if (s.y > 2.8 || s.y < 0.45) return;

    // 사용자가 마우스로 휘두를 때는
    // 스윙 방향과 셔틀콕 위치를 비교
    if (character.isHuman && racketDirection !== 0) {

        const shuttleSide =
            Math.sign(s.x - p.x);

        const swingSide =
            Math.sign(racketDirection);

        if (shuttleSide !== swingSide) {
            setMessage("🏸 스윙 방향이 맞지 않았어요!");
            return;
        }
    }

    character.hitCooldown = 0.6;
    character.swingTime = 0.25;

    // 상대 코트 방향
    const direction = character.team === 0 ? -1 : 1;

    // 목표 착지 위치
    let targetZ;
    let flightTime;

    if (shotType === "smash") {
        // 빠르고 강한 스매시
        targetZ = direction * 4.5;
        flightTime = 0.65;

    } else if (shotType === "drop") {
        // 네트 근처로 짧게 떨어지는 드롭
        targetZ = direction * 2.3;
        flightTime = 0.9;

    } else {
        // 상대 코트 뒤쪽으로 보내는 클리어
        targetZ = direction * 5.3;
        flightTime = 1.4;
    }

    // 좌우 랜덤 목표
    const targetX =
        court.centerX + (Math.random() - 0.5) * 4.0;

    // 목표 위치까지 날아가는 속도
    shuttle.vx = (targetX - s.x) / flightTime;
    shuttle.vz = (targetZ - s.z) / flightTime;

    // 중력을 고려한 초기 수직 속도
    shuttle.vy =
        (0.1 - s.y + 4.9 * flightTime * flightTime)
        / flightTime;

    shuttle.hitterTeam = character.team;
    court.lastHitter = character.name;

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

    // 일시정지 상태에서 다시 시작
    if (running && paused) {

        paused = false;

        gameArea.focus();

        setMessage("▶ 경기를 재개했습니다.");

        return;
    }

    if (running) return;

    running = true;
    paused = false;

    // 3개 코트 경기 초기화 및 시작
    courts.forEach(court => {

        court.score = [0, 0];
        court.finished = false;
        court.rally = null;

        const servingTeam =
            Math.random() < 0.5 ? 0 : 1;

        serve(court, servingTeam);
    });

    // 내가 조작하는 1번 코트 확대
    setCamera(0);

    // 키보드 입력 활성화
    gameArea.focus();

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

    // 마우스 카메라 조작 반영
    updateOrbitCamera();

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
    height=1150,
    scrolling=True
)
