const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// UI Elements
const startScreen = document.getElementById('startScreen');
const gameOverScreen = document.getElementById('gameOverScreen');
const highestScoreDisplay = document.getElementById('highestScoreDisplay');
const finalScoreDisplay = document.getElementById('finalScore');
const bestScoreDisplay = document.getElementById('bestScore');
const restartBtn = document.getElementById('restartBtn');

// Game Constants
const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const GRAVITY = 0.5;
const FLAP_STRENGTH = -8;
const PIPE_SPEED = 3;
const PIPE_WIDTH = 60;
const PIPE_GAP = 150;
const GROUND_HEIGHT = 50;

// Colors
const SKY_COLOR = '#71c5cf';
const GROUND_COLOR = '#ded895';
const GROUND_LINE = '#73bf2e';
const BIRD_COLOR = '#ffcc00';
const BIRD_OUTLINE = '#000000';
const WING_COLOR = '#ffffff';
const BEAK_COLOR = '#ff6600';
const PIPE_COLOR = '#74bf2e';
const PIPE_OUTLINE = '#543847';

// Game State
let state = 'START'; // START, PLAYING, GAME_OVER
let score = 0;
let highestScore = 0;
let frames = 0;

// Fetch initial highest score from backend
fetch('/api/score')
    .then(response => response.json())
    .then(data => {
        highestScore = data.highest_score;
        highestScoreDisplay.innerText = highestScore;
    });

// Classes
class Bird {
    constructor() {
        this.x = 100;
        this.y = HEIGHT / 2;
        this.vel = 0;
        this.radius = 15;
        this.wingDir = 1;
        this.wingAngle = 0;
        this.alive = true;
    }

    jump() {
        if (this.alive) {
            this.vel = FLAP_STRENGTH;
            this.wingAngle = -30;
        }
    }

    update() {
        this.vel += GRAVITY;
        this.y += this.vel;

        // Ceiling collision
        if (this.y < 0) {
            this.y = 0;
            this.vel = 0;
        }

        // Ground collision
        if (this.y >= HEIGHT - GROUND_HEIGHT - this.radius) {
            this.y = HEIGHT - GROUND_HEIGHT - this.radius;
            this.alive = false;
        }

        // Wing animation
        if (this.alive) {
            this.wingAngle += 5 * this.wingDir;
            if (this.wingAngle > 30 || this.wingAngle < -30) {
                this.wingDir *= -1;
            }
        }
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);

        // Rotation based on velocity
        let angle = Math.max(-Math.PI/2, Math.min(Math.PI/6, (this.vel * 3) * (Math.PI/180)));
        if (!this.alive) angle = Math.PI/2;
        ctx.rotate(angle);

        // Body
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = BIRD_COLOR;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = BIRD_OUTLINE;
        ctx.stroke();

        // Eye
        ctx.beginPath();
        ctx.arc(5, -5, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(7, -5, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#000';
        ctx.fill();

        // Beak
        ctx.beginPath();
        ctx.moveTo(13, 0);
        ctx.lineTo(20, 2);
        ctx.lineTo(13, 6);
        ctx.closePath();
        ctx.fillStyle = BEAK_COLOR;
        ctx.fill();
        ctx.stroke();

        // Wing
        ctx.save();
        ctx.translate(-5, 2);
        ctx.rotate(this.wingAngle * Math.PI / 180);
        
        ctx.beginPath();
        ctx.ellipse(0, 0, 10, 5, 0, 0, Math.PI*2);
        ctx.fillStyle = WING_COLOR;
        ctx.fill();
        ctx.stroke();
        
        ctx.restore();

        ctx.restore();
    }
}

class Pipe {
    constructor() {
        this.x = WIDTH;
        // Gap y-position between 150 and HEIGHT - GROUND_HEIGHT - 150
        this.gapY = Math.floor(Math.random() * (HEIGHT - GROUND_HEIGHT - 300)) + 150;
        this.passed = false;
    }

    update() {
        this.x -= PIPE_SPEED;
    }

    draw() {
        ctx.fillStyle = PIPE_COLOR;
        ctx.strokeStyle = PIPE_OUTLINE;
        ctx.lineWidth = 3;

        // Top Pipe
        const topHeight = this.gapY - PIPE_GAP/2;
        ctx.fillRect(this.x, 0, PIPE_WIDTH, topHeight);
        ctx.strokeRect(this.x, 0, PIPE_WIDTH, topHeight);
        
        // Top Cap
        ctx.fillRect(this.x - 4, topHeight - 20, PIPE_WIDTH + 8, 20);
        ctx.strokeRect(this.x - 4, topHeight - 20, PIPE_WIDTH + 8, 20);

        // Bottom Pipe
        const bottomY = this.gapY + PIPE_GAP/2;
        const bottomHeight = HEIGHT - bottomY - GROUND_HEIGHT;
        ctx.fillRect(this.x, bottomY, PIPE_WIDTH, bottomHeight);
        ctx.strokeRect(this.x, bottomY, PIPE_WIDTH, bottomHeight);

        // Bottom Cap
        ctx.fillRect(this.x - 4, bottomY, PIPE_WIDTH + 8, 20);
        ctx.strokeRect(this.x - 4, bottomY, PIPE_WIDTH + 8, 20);
    }
}

class Background {
    constructor() {
        this.bgX = 0;
        this.clouds = [];
        for (let i=0; i<10; i++) {
            this.clouds.push({
                x: Math.random() * WIDTH * 2,
                y: Math.random() * (HEIGHT / 2) + 50
            });
        }
    }

    update(moving) {
        if (moving) {
            this.bgX -= 1;
            if (this.bgX <= -WIDTH) {
                this.bgX = 0;
            }
        }
    }

    draw() {
        // Sky
        ctx.fillStyle = SKY_COLOR;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Clouds
        ctx.fillStyle = '#ffffff';
        for (let c of this.clouds) {
            let xPos = (c.x + this.bgX) % (WIDTH * 2);
            if (xPos < -50) xPos += WIDTH * 2;
            
            ctx.beginPath();
            ctx.arc(xPos, c.y, 20, 0, Math.PI*2);
            ctx.arc(xPos + 15, c.y - 10, 25, 0, Math.PI*2);
            ctx.arc(xPos + 30, c.y, 20, 0, Math.PI*2);
            ctx.fill();
        }

        // Ground
        ctx.fillStyle = GROUND_COLOR;
        ctx.fillRect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT);
        ctx.fillStyle = GROUND_LINE;
        ctx.fillRect(0, HEIGHT - GROUND_HEIGHT, WIDTH, 10);
    }
}

// Game Instances
let bird;
let pipes = [];
let bg;

function init() {
    bird = new Bird();
    pipes = [];
    bg = new Background();
    score = 0;
    frames = 0;
}

function handleCollisions() {
    for (let pipe of pipes) {
        // Check collision
        if (bird.x + bird.radius > pipe.x && bird.x - bird.radius < pipe.x + PIPE_WIDTH) {
            if (bird.y - bird.radius < pipe.gapY - PIPE_GAP/2 || 
                bird.y + bird.radius > pipe.gapY + PIPE_GAP/2) {
                bird.alive = false;
            }
        }

        // Score
        if (!pipe.passed && bird.x > pipe.x + PIPE_WIDTH) {
            score++;
            pipe.passed = true;
        }
    }
}

function gameOver() {
    state = 'GAME_OVER';
    finalScoreDisplay.innerText = score;
    
    // Save score to backend
    fetch('/api/score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ score: score })
    })
    .then(res => res.json())
    .then(data => {
        highestScore = data.highest_score;
        bestScoreDisplay.innerText = highestScore;
        highestScoreDisplay.innerText = highestScore;
        gameOverScreen.classList.add('active');
    });
}

function loop() {
    // Update
    if (state === 'PLAYING') {
        bird.update();
        bg.update(true);

        if (bird.alive) {
            frames++;
            if (frames % 90 === 0) { // Spawn pipe every 1.5 seconds (at 60fps)
                pipes.push(new Pipe());
            }

            pipes.forEach(p => p.update());
            pipes = pipes.filter(p => p.x + PIPE_WIDTH > 0);

            handleCollisions();
            
            if (!bird.alive) {
                // Bird just died
            }
        } else {
            // Falling to ground after hitting pipe
            if (bird.y >= HEIGHT - GROUND_HEIGHT - bird.radius) {
                gameOver();
            }
        }
    } else if (state === 'GAME_OVER') {
        bg.update(false); // Stop background
    }

    // Draw
    bg.draw();
    pipes.forEach(p => p.draw());
    
    if (state !== 'START') {
        bird.draw();
        
        // Draw real-time score
        if (state === 'PLAYING' && bird.alive) {
            ctx.fillStyle = '#fff';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 4;
            ctx.font = '36px "Press Start 2P"';
            ctx.textAlign = 'center';
            ctx.strokeText(score, WIDTH/2, 50);
            ctx.fillText(score, WIDTH/2, 50);
        }
    }

    requestAnimationFrame(loop);
}

// Controls
function jump() {
    if (state === 'START') {
        init();
        state = 'PLAYING';
        bird.jump();
        startScreen.classList.remove('active');
    } else if (state === 'PLAYING' && bird.alive) {
        bird.jump();
    }
}

window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        jump();
        e.preventDefault(); // Prevent scrolling
    }
});

window.addEventListener('mousedown', (e) => {
    if (e.target.tagName !== 'BUTTON') {
        jump();
    }
});

restartBtn.addEventListener('click', () => {
    init();
    state = 'PLAYING';
    bird.jump();
    gameOverScreen.classList.remove('active');
});

// Start loop
init();
bg.draw(); // Draw initial frame
requestAnimationFrame(loop);
