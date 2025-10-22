class BlackjackGame {
    constructor() {
        this.apiUrl = '/bj/api';
        this.gameStarted = false;
        this.currentBet = 10;
        this.initializeEventListeners();
        this.loadGameState();
    }

    initializeEventListeners() {
        document.getElementById('betAmount').addEventListener('input', (e) => {
            this.currentBet = parseInt(e.target.value) || 10;
        });

        document.querySelectorAll('.quick-bet').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentBet = parseInt(e.target.dataset.bet);
                document.getElementById('betAmount').value = this.currentBet;
                this.startNewGame();
            });
        });

        document.getElementById('hitButton').addEventListener('click', () => this.hit());
        document.getElementById('standButton').addEventListener('click', () => this.stand());
        document.getElementById('newGameButton').addEventListener('click', () => this.startNewGame());
        document.getElementById('startBetButton').addEventListener('click', () => this.startNewGame());
    }

    async loadGameState() {
        try {
            const response = await fetch(`${this.apiUrl}/state`);
            const data = await response.json();
            if (data.success) {
                this.updateDisplay(data.game_state);
            } else {
                this.updateControls(true);
                this.displayMessage("Начните новую игру, сделав ставку.");
            }
        } catch (error) {
            console.error('Error loading game state:', error);
            this.displayMessage("Ошибка загрузки игры. Пожалуйста, начните новую игру.");
        }
    }

    async startNewGame() {
        const bet = this.currentBet;
        if (bet <= 0) {
            this.displayMessage("Ставка должна быть больше нуля.");
            return;
        }

        this.displayMessage("Начинаем новую игру...");
        this.updateControls(false);

        try {
            const response = await fetch(`${this.apiUrl}/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bet: bet })
            });
            const data = await response.json();

            if (data.success) {
                this.updateDisplay(data.game_state);
            } else {
                this.displayMessage(`Ошибка: ${data.error}`);
                this.updateControls(true); // Re-enable new game button on error
            }
        } catch (error) {
            console.error('Error starting new game:', error);
            this.displayMessage("Ошибка при начале новой игры.");
            this.updateControls(true); // Re-enable new game button on error
        }
    }

    async hit() {
        this.updateControls(false);
        try {
            const response = await fetch(`${this.apiUrl}/hit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();

            if (data.success) {
                this.updateDisplay(data.game_state);
            } else {
                this.displayMessage(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            console.error('Error on hit action:', error);
            this.displayMessage("Ошибка при взятии карты.");
        }
    }

    async stand() {
        this.updateControls(false);
        try {
            const response = await fetch(`${this.apiUrl}/stand`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();

            if (data.success) {
                this.updateDisplay(data.game_state);
            } else {
                this.displayMessage(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            console.error('Error on stand action:', error);
            this.displayMessage("Ошибка при остановке.");
        }
    }

    updateDisplay(state) {
        document.getElementById('dealer-hand').innerHTML = this.renderHand(state.dealer_hand);
        document.getElementById('player-hand').innerHTML = this.renderHand(state.player_hand);

        document.getElementById('dealer-score').textContent = state.dealer_score;
        document.getElementById('player-score').textContent = state.player_score;

        document.getElementById('currentBalance').textContent = `$${parseFloat(state.new_balance).toFixed(2)}`;
        document.getElementById('currentBetDisplay').textContent = `$${parseFloat(state.bet_amount).toFixed(2)}`;
        this.currentBet = state.bet_amount;
        document.getElementById('betAmount').value = state.bet_amount;

        this.displayMessage(state.message);

        this.updateControls(state.game_over);
    }

    renderHand(hand) {
        if (!hand || hand.length === 0) return '';
        return hand.map(card => {
            if (card === '???') {
                return `<div class="card-item card-back"></div>`;
            }

            const parts = card.split(' ');
            const rank = parts[0];
            const suit = parts[parts.length - 1];
            const suitClass = `card-${suit.toLowerCase()}`;

            let suitSymbol = '';
            switch(suit.toLowerCase()) {
                case 'hearts': suitSymbol = '♥'; break;
                case 'diamonds': suitSymbol = '♦'; break;
                case 'spades': suitSymbol = '♠'; break;
                case 'clubs': suitSymbol = '♣'; break;
            }

            return `
            <div class="card-item ${suitClass}">
                <div class="corner top-left">
                    ${rank}<span class="corner-suit">${suitSymbol}</span>
                </div>
                <div class="card-rank">${rank}</div>
                <div class="corner bottom-right">
                    ${rank}<span class="corner-suit">${suitSymbol}</span>
                </div>
            </div>
        `;
    }).join('');
    }

    displayMessage(message) {
        const messageDiv = document.getElementById('game-message');
        if (message) {
            messageDiv.innerHTML = `<h4>${message}</h4>`;
            messageDiv.style.display = 'block';
            if (message.includes("Вы выиграли") || message.includes("Блэкджек")) {
                messageDiv.className = 'alert alert-success mt-3';
            } else if (message.includes("проиграли") || message.includes("Дилер выиграл")) {
                messageDiv.className = 'alert alert-danger mt-3';
            } else if (message.includes("Ничья")) {
                messageDiv.className = 'alert alert-warning mt-3';
            } else {
                messageDiv.className = 'alert alert-info mt-3';
            }
        } else {
            messageDiv.style.display = 'none';
        }
    }

    updateControls(gameOver) {
        const hitButton = document.getElementById('hitButton');
        const standButton = document.getElementById('standButton');
        const newGameButton = document.getElementById('newGameButton');
        const actionControls = document.getElementById('actionControls');
        const newGameControls = document.getElementById('newGameControls');
        const betControls = document.getElementById('betControls');
        
        if (gameOver) {
            actionControls.style.display = 'none';
            newGameControls.style.display = 'block';
            betControls.style.display = 'block';
        } else if (actionControls.style.display === 'none') {
            // Game is in progress, show action buttons
            actionControls.style.display = 'flex';
            newGameControls.style.display = 'none';
            betControls.style.display = 'none';
        } else {
            // Game is in progress, just ensure buttons are enabled
            hitButton.disabled = false;
            standButton.disabled = false;
            newGameControls.style.display = 'none';
            betControls.style.display = 'none';
        }
        
        // On initial load (no game state), show new game controls
        if (actionControls.style.display === 'none' && newGameControls.style.display === 'none') {
            newGameControls.style.display = 'block';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we are on the blackjack page
    if (document.getElementById('blackjack-game-container')) {
        new BlackjackGame();
    }
});

