class RouletteGame {
    constructor() {
        this.balance = parseFloat(document.getElementById('currentBalance').textContent.replace('$', ''));
        this.currentChipValue = 10;
        this.bets = [];
        this.isSpinning = false;
        this.wheelRotation = 0;
        this.canvas = document.getElementById('wheelCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.wheelNumbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
            5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ];
        
        this.redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];
        
        this.initializeEventListeners();
        this.drawWheel();
        this.updateDisplay();
        this.getLastResults();
    }
    
    initializeEventListeners() {
        document.querySelectorAll('.chip-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentChipValue = parseInt(e.target.dataset.value);
            });
        });
        
        document.querySelectorAll('.bet-cell').forEach(cell => {
            if (!cell.classList.contains('empty-cell')) {
                cell.addEventListener('click', (e) => {
                    this.placeBet(e.currentTarget);
                });
            }
        });
        
        document.getElementById('spinButton').addEventListener('click', () => this.spin());
        document.getElementById('clearBetsButton').addEventListener('click', () => this.clearBets());
        document.getElementById('undoButton').addEventListener('click', () => this.undoLastBet());
    }
    
    drawWheel() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 180;
        const segmentAngle = (2 * Math.PI) / this.wheelNumbers.length;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#8B4513';
        this.ctx.fill();
        this.ctx.strokeStyle = '#FFD700';
        this.ctx.lineWidth = 8;
        this.ctx.stroke();
        
        this.wheelNumbers.forEach((num, index) => {
            const startAngle = index * segmentAngle + this.wheelRotation;
            const endAngle = startAngle + segmentAngle;
            
            let color;
            if (num === 0) {
                color = '#00AA00';
            } else if (this.redNumbers.includes(num)) {
                color = '#CC0000';
            } else {
                color = '#000000';
            }
            
            this.ctx.beginPath();
            this.ctx.moveTo(centerX, centerY);
            this.ctx.arc(centerX, centerY, radius - 10, startAngle, endAngle);
            this.ctx.closePath();
            this.ctx.fillStyle = color;
            this.ctx.fill();
            this.ctx.strokeStyle = '#FFD700';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            const textAngle = startAngle + segmentAngle / 2;
            const textRadius = radius - 35;
            const textX = centerX + Math.cos(textAngle) * textRadius;
            const textY = centerY + Math.sin(textAngle) * textRadius;
            
            this.ctx.save();
            this.ctx.translate(textX, textY);
            this.ctx.rotate(textAngle + Math.PI / 2);
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(num.toString(), 0, 0);
            this.ctx.restore();
        });
        
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 30, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#FFD700';
        this.ctx.fill();
        this.ctx.strokeStyle = '#8B4513';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
    }
    
    placeBet(cell) {
        if (this.isSpinning) return;
        
        const betType = cell.dataset.betType;
        const betValue = cell.dataset.betValue;
        
        if (this.balance < this.currentChipValue) {
            alert('Недостаточно денег!');
            return;
        }
        
        const existingBetIndex = this.bets.findIndex(
            bet => bet.type === betType && bet.value === betValue
        );
        
        if (existingBetIndex >= 0) {
            this.bets[existingBetIndex].amount += this.currentChipValue;
        } else {
            this.bets.push({
                type: betType,
                value: betValue,
                amount: this.currentChipValue,
                cell: cell
            });
        }
        
        this.updateBetDisplay(cell, betType, betValue);
        this.updateDisplay();
    }
    
    updateBetDisplay(cell, betType, betValue) {
        const chipContainer = cell.querySelector('.chip-container');
        if (!chipContainer) return;
        
        const bet = this.bets.find(b => b.type === betType && b.value === betValue);
        if (bet) {
            chipContainer.innerHTML = `<div class="chip chip-${this.getChipClass(bet.amount)}">$${bet.amount}</div>`;
            chipContainer.style.display = 'block';
        }
    }
    
    getChipClass(amount) {
        if (amount >= 100) return '100';
        if (amount >= 50) return '50';
        if (amount >= 25) return '25';
        if (amount >= 10) return '10';
        if (amount >= 5) return '5';
        return '1';
    }
    
    clearBets() {
        if (this.isSpinning) return;
        
        this.bets = [];
        document.querySelectorAll('.chip-container').forEach(container => {
            container.innerHTML = '';
            container.style.display = 'none';
        });
        this.updateDisplay();
    }
    
    undoLastBet() {
        if (this.isSpinning || this.bets.length === 0) return;
        
        const lastBet = this.bets.pop();
        const chipContainer = lastBet.cell.querySelector('.chip-container');
        if (chipContainer) {
            chipContainer.innerHTML = '';
            chipContainer.style.display = 'none';
        }
        this.updateDisplay();
    }
    
    updateDisplay() {
        const totalBet = this.bets.reduce((sum, bet) => sum + bet.amount, 0);
        document.getElementById('totalBet').textContent = `$${totalBet.toFixed(2)}`;
        
        const betsContainer = document.getElementById('currentBets');
        if (this.bets.length === 0) {
            betsContainer.innerHTML = '<p class="text-muted text-center">Вы не сделали ставку</p>';
        } else {
            betsContainer.innerHTML = this.bets.map(bet => `
                <div class="bet-item d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                    <span class="bet-description">${this.getBetDescription(bet)}</span>
                    <span class="badge bg-primary">$${bet.amount}</span>
                </div>
            `).join('');
        }
    }
    
    getBetDescription(bet) {
        switch(bet.type) {
            case 'straight':
                return `Number ${bet.value}`;
            case 'color':
                return bet.value.charAt(0).toUpperCase() + bet.value.slice(1);
            case 'even_odd':
                return bet.value.toUpperCase();
            case 'low_high':
                return bet.value === 'low' ? '1-18' : '19-36';
            case 'dozen':
                return `${bet.value}${this.getOrdinalSuffix(bet.value)} Dozen`;
            case 'column':
                return `Column ${bet.value}`;
            default:
                return 'Unknown';
        }
    }
    
    getOrdinalSuffix(num) {
        const j = num % 10;
        const k = num % 100;
        if (j === 1 && k !== 11) return 'st';
        if (j === 2 && k !== 12) return 'nd';
        if (j === 3 && k !== 13) return 'rd';
        return 'th';
    }

    async getLastResults() {
        try {
            const response = await fetch('/roulette/history', {
                method: 'GET',
            });

            const result = await response.json();

            if (result.error) {
            }
            this.updateLastResults(result.history);
        } catch (error) {}
    }
    
    async spin() {
        if (this.isSpinning) return;
        
        if (this.bets.length === 0) {
            alert('Сделай хотя бы одну ставку!');
            return;
        }
        
        const totalBet = this.bets.reduce((sum, bet) => sum + bet.amount, 0);
        if (this.balance < totalBet) {
            alert('Недостаточно денег!');
            return;
        }
        
        this.isSpinning = true;
        this.disableControls();
        
        try {
            const response = await fetch('/roulette/spin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ bets: this.bets })
            });
            
            const result = await response.json();
            
            if (result.error) {
                alert('Error: ' + result.error);
                this.isSpinning = false;
                this.enableControls();
                return;
            }
            
            await this.animateSpin(result.winning_number);
            this.showResult(result);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Ошибка при вращении колеса');
            this.isSpinning = false;
            this.enableControls();
        }
    }
    
    async animateSpin(winningNumber) {
        const ball = document.getElementById('wheelBall');
        ball.style.display = 'block';
        
        const numberIndex = this.wheelNumbers.indexOf(winningNumber);
        const segmentAngle = (2 * Math.PI) / this.wheelNumbers.length;
        const targetAngle = numberIndex * segmentAngle;
        
        const totalRotations = 5 + Math.random() * 2;
        const totalAngle = totalRotations * 2 * Math.PI + targetAngle;
        
        const duration = 4000;
        const startTime = Date.now();
        const startRotation = this.wheelRotation;
        
        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                const easeOut = 1 - Math.pow(1 - progress, 3);
                
                this.wheelRotation = startRotation + totalAngle * easeOut;
                this.drawWheel();
                
                const ballAngle = -this.wheelRotation + Math.PI / 2;
                const ballRadius = 160;
                const ballX = 200 + Math.cos(ballAngle) * ballRadius;
                const ballY = 200 + Math.sin(ballAngle) * ballRadius;
                ball.style.left = ballX + 'px';
                ball.style.top = ballY + 'px';
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    ball.style.display = 'none';
                    resolve();
                }
            };
            animate();
        });
    }
    
    showResult(result) {
        this.balance = result.new_balance;
        document.getElementById('currentBalance').textContent = `$${this.balance.toFixed(2)}`;
        
        const winningNumberEl = document.getElementById('winningNumber');
        winningNumberEl.textContent = result.winning_number;
        winningNumberEl.className = 'winning-number ' + result.winning_color;
        
        this.updateLastResults(result.last_results);
        
        const modalBody = document.getElementById('resultModalBody');
        const netResult = result.net_result;
        
        if (netResult > 0) {
            modalBody.innerHTML = `
                <div class="result-win">
                    <h2 class="text-success mb-3">🎉 ТЫ ПОБЕДИЛ! 🎉</h2>
                    <div class="winning-number-large ${result.winning_color} mb-3">
                        ${result.winning_number}
                    </div>
                    <h4 class="text-success">+$${netResult.toFixed(2)}</h4>
                    <p class="text-muted">Total Payout: $${result.total_payout.toFixed(2)}</p>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <div class="result-loss">
                    <h2 class="text-danger mb-3">В следующий раз точно повезет!</h2>
                    <div class="winning-number-large ${result.winning_color} mb-3">
                        ${result.winning_number}
                    </div>
                    <h4 class="text-danger">-$${Math.abs(netResult).toFixed(2)}</h4>
                    <p class="text-muted">Ни одна ставка не зашла</p>
                </div>
            `;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('resultModal'));
        modal.show();
        
        setTimeout(() => {
            this.clearBets();
            this.isSpinning = false;
            this.enableControls();
        }, 1000);
    }
    
    updateLastResults(results) {
        const container = document.getElementById('lastResults');
        if (results.length === 0) {
            container.innerHTML = '<span class="text-white-50">Колесо еще не крутили</span>';
            return;
        }
        
        container.innerHTML = results.map(num => {
            let color = 'green';
            if (num !== 0) {
                color = this.redNumbers.includes(num) ? 'red' : 'black';
            }
            return `<span class="result-number ${color}">${num}</span>`;
        }).join('');
    }
    
    disableControls() {
        document.getElementById('spinButton').disabled = true;
        document.getElementById('clearBetsButton').disabled = true;
        document.getElementById('undoButton').disabled = true;
        document.querySelectorAll('.chip-btn').forEach(btn => btn.disabled = true);
        document.querySelectorAll('.bet-cell').forEach(cell => cell.style.pointerEvents = 'none');
    }
    
    enableControls() {
        document.getElementById('spinButton').disabled = false;
        document.getElementById('clearBetsButton').disabled = false;
        document.getElementById('undoButton').disabled = false;
        document.querySelectorAll('.chip-btn').forEach(btn => btn.disabled = false);
        document.querySelectorAll('.bet-cell').forEach(cell => cell.style.pointerEvents = 'auto');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new RouletteGame();
});

