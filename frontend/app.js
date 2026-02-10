// Game State
const TOTAL_LEVELS = 10;
const TIME_PER_LEVEL = 60; // seconds

let gameState = {
    currentLevel: 1,
    score: 0,
    correctAnswers: 0,
    skippedAnswers: 0,
    timeLeft: TIME_PER_LEVEL,
    timerInterval: null,
    currentWordIndex: 0,
    levelWords: []
};

// Word Database - Organized by difficulty/level
const wordsByLevel = [
    // Level 1 - Easy words
    [
        'AVION', 'VOITURE', 'CHAT', 'CHIEN', 'MAISON',
        'SOLEIL', 'LUNE', 'EAU', 'FEU', 'ARBRE',
        'FLEUR', 'PAIN', 'POMME', 'LIVRE', 'TABLE'
    ],
    // Level 2
    [
        'ORDINATEUR', 'TÉLÉPHONE', 'CHOCOLAT', 'RESTAURANT', 'CINÉMA',
        'MUSIQUE', 'DANSE', 'PLAGE', 'MONTAGNE', 'JARDIN',
        'FENÊTRE', 'PORTE', 'CHAISE', 'STYLO', 'CAHIER'
    ],
    // Level 3
    [
        'PARAPLUIE', 'LUNETTES', 'CHEMISE', 'PANTALON', 'CHAUSSURE',
        'MONTRE', 'COLLIER', 'BRACELET', 'PARFUM', 'SAVON',
        'BROSSE', 'MIROIR', 'SERVIETTE', 'COUTEAU', 'FOURCHETTE'
    ],
    // Level 4
    [
        'BIBLIOTHÈQUE', 'UNIVERSITÉ', 'HÔPITAL', 'PHARMACIE', 'BOULANGERIE',
        'SUPERMARCHÉ', 'BANQUE', 'POSTE', 'GARE', 'AÉROPORT',
        'MUSÉE', 'THÉÂTRE', 'STADE', 'PISCINE', 'GYMNASE'
    ],
    // Level 5
    [
        'PAPILLON', 'ABEILLE', 'OISEAU', 'POISSON', 'ÉLÉPHANT',
        'GIRAFE', 'LION', 'TIGRE', 'SINGE', 'KANGOUROU',
        'TORTUE', 'SERPENT', 'GRENOUILLE', 'SOURIS', 'LAPIN'
    ],
    // Level 6
    [
        'ORDINATEUR', 'CLAVIER', 'SOURIS', 'ÉCRAN', 'IMPRIMANTE',
        'SCANNER', 'WEBCAM', 'MICROPHONE', 'CASQUE', 'ENCEINTE',
        'TABLETTE', 'SMARTPHONE', 'CHARGEUR', 'CÂBLE', 'BATTERIE'
    ],
    // Level 7
    [
        'RÉVOLUTION', 'DÉMOCRATIE', 'RÉPUBLIQUE', 'PRÉSIDENT', 'MINISTRE',
        'DÉPUTÉ', 'SÉNATEUR', 'ÉLECTION', 'VOTE', 'CITOYEN',
        'JUSTICE', 'LIBERTÉ', 'ÉGALITÉ', 'FRATERNITÉ', 'DRAPEAU'
    ],
    // Level 8
    [
        'ASTRONAUTE', 'PLANÈTE', 'ÉTOILE', 'GALAXIE', 'UNIVERS',
        'SATELLITE', 'FUSÉE', 'COMÈTE', 'MÉTÉORITE', 'CRATÈRE',
        'TELESCOPE', 'OBSERVATOIRE', 'CONSTELLATION', 'ORBITE', 'GRAVITÉ'
    ],
    // Level 9
    [
        'PHOTOSYNTHÈSE', 'CHROMOSOME', 'MOLÉCULE', 'ATOME', 'ÉLECTRON',
        'NEUTRON', 'PROTON', 'CELLULE', 'MEMBRANE', 'NOYAU',
        'ENZYME', 'PROTÉINE', 'GÉNÉTIQUE', 'ÉVOLUTION', 'MUTATION'
    ],
    // Level 10 - Hardest
    [
        'ANTICONSTITUTIONNELLEMENT', 'INTERDISCIPLINARITÉ', 'EXTRATERRITORIALITÉ',
        'CONSTITUTIONNELLEMENT', 'INCOMPRÉHENSIBLE', 'INVRAISEMBLABLE',
        'EXTRAORDINAIRE', 'RÉVOLUTIONNAIRE', 'INDISPENSABLE', 'INCONTOURNABLE',
        'PERPENDICULAIRE', 'RECTANGULAIRE', 'TRIANGULAIRE', 'QUADRILATÈRE', 'PARALLÉLÉPIPÈDE'
    ]
];

// DOM Elements
const screens = {
    start: document.getElementById('startScreen'),
    game: document.getElementById('gameScreen'),
    end: document.getElementById('endScreen')
};

const elements = {
    startBtn: document.getElementById('startBtn'),
    currentLevel: document.getElementById('currentLevel'),
    timer: document.getElementById('timer'),
    timeLeft: document.getElementById('timeLeft'),
    score: document.getElementById('score'),
    firstLetter: document.getElementById('firstLetter'),
    wordToGuess: document.getElementById('wordToGuess'),
    skipBtn: document.getElementById('skipBtn'),
    gotItBtn: document.getElementById('gotItBtn'),
    endTitle: document.getElementById('endTitle'),
    finalScore: document.getElementById('finalScore'),
    correctAnswers: document.getElementById('correctAnswers'),
    skippedAnswers: document.getElementById('skippedAnswers'),
    totalWords: document.getElementById('totalWords'),
    nextLevelBtn: document.getElementById('nextLevelBtn'),
    restartBtn: document.getElementById('restartBtn')
};

// Screen Management
function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
}

// Initialize Game
function initGame() {
    gameState = {
        currentLevel: 1,
        score: 0,
        correctAnswers: 0,
        skippedAnswers: 0,
        timeLeft: TIME_PER_LEVEL,
        timerInterval: null,
        currentWordIndex: 0,
        levelWords: []
    };
}

// Start Game
function startGame() {
    initGame();
    startLevel();
}

// Start Level
function startLevel() {
    // Shuffle and select words for this level
    gameState.levelWords = shuffleArray([...wordsByLevel[gameState.currentLevel - 1]]);
    gameState.currentWordIndex = 0;
    gameState.timeLeft = TIME_PER_LEVEL;

    // Update UI
    elements.currentLevel.textContent = gameState.currentLevel;
    elements.score.textContent = gameState.score;

    // Show game screen
    showScreen('game');

    // Show first word
    showNextWord();

    // Start timer
    startTimer();
}

// Shuffle Array
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Show Next Word
function showNextWord() {
    if (gameState.currentWordIndex >= gameState.levelWords.length) {
        // Reshuffle if we run out of words
        gameState.levelWords = shuffleArray(gameState.levelWords);
        gameState.currentWordIndex = 0;
    }

    const word = gameState.levelWords[gameState.currentWordIndex];
    const firstLetter = word.charAt(0);

    elements.firstLetter.textContent = firstLetter;
    elements.wordToGuess.textContent = word;

    // Trigger animation
    elements.firstLetter.style.animation = 'none';
    setTimeout(() => {
        elements.firstLetter.style.animation = 'letterBounce 0.6s ease';
    }, 10);
}

// Timer
function startTimer() {
    // Clear any existing timer
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
    }

    gameState.timerInterval = setInterval(() => {
        gameState.timeLeft--;
        elements.timeLeft.textContent = gameState.timeLeft;

        // Warning state when time is low
        if (gameState.timeLeft <= 10) {
            elements.timer.classList.add('warning');
        } else {
            elements.timer.classList.remove('warning');
        }

        // Time's up
        if (gameState.timeLeft <= 0) {
            endLevel();
        }
    }, 1000);
}

// Stop Timer
function stopTimer() {
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }
}

// Handle "Got It" Button
function handleGotIt() {
    gameState.correctAnswers++;
    gameState.score += 10;
    elements.score.textContent = gameState.score;

    // Move to next word
    gameState.currentWordIndex++;
    showNextWord();
}

// Handle "Skip" Button
function handleSkip() {
    gameState.skippedAnswers++;

    // Move to next word
    gameState.currentWordIndex++;
    showNextWord();
}

// End Level
function endLevel() {
    stopTimer();

    // Calculate total words attempted
    const totalWords = gameState.correctAnswers + gameState.skippedAnswers;

    // Update end screen
    elements.finalScore.textContent = gameState.score;
    elements.correctAnswers.textContent = gameState.correctAnswers;
    elements.skippedAnswers.textContent = gameState.skippedAnswers;
    elements.totalWords.textContent = totalWords;

    // Check if this was the last level
    if (gameState.currentLevel >= TOTAL_LEVELS) {
        elements.endTitle.textContent = 'Félicitations! Jeu Terminé!';
        elements.nextLevelBtn.style.display = 'none';
    } else {
        elements.endTitle.textContent = `Niveau ${gameState.currentLevel} Terminé!`;
        elements.nextLevelBtn.style.display = 'block';
    }

    showScreen('end');
}

// Next Level
function nextLevel() {
    gameState.currentLevel++;
    gameState.correctAnswers = 0;
    gameState.skippedAnswers = 0;
    startLevel();
}

// Restart Game
function restartGame() {
    initGame();
    showScreen('start');
}

// Event Listeners
elements.startBtn.addEventListener('click', startGame);
elements.gotItBtn.addEventListener('click', handleGotIt);
elements.skipBtn.addEventListener('click', handleSkip);
elements.nextLevelBtn.addEventListener('click', nextLevel);
elements.restartBtn.addEventListener('click', restartGame);

// Prevent accidental page navigation
window.addEventListener('beforeunload', (e) => {
    if (gameState.timerInterval) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Touch event optimization for mobile
document.addEventListener('touchstart', function() {}, {passive: true});
