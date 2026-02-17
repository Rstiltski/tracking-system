/**
 * Rewards Module - UI for Variable Reward Scheduling
 * Phase 3.3 Implementation
 * 
 * Based on B.F. Skinner's Operant Conditioning - Variable Ratio Schedule
 * Features:
 * - Animated reward reveals
 * - Reward collection/gallery
 * - Reward history and stats
 */

const Rewards = {
    // Rarity colors and configurations
    rarityConfig: {
        common: {
            color: '#6b7280',
            bgGradient: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
            glow: '0 0 20px rgba(107, 114, 128, 0.5)',
            animation: 'commonReveal 0.5s ease-out'
        },
        uncommon: {
            color: '#10b981',
            bgGradient: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
            glow: '0 0 30px rgba(16, 185, 129, 0.6)',
            animation: 'uncommonReveal 0.7s ease-out'
        },
        rare: {
            color: '#3b82f6',
            bgGradient: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
            glow: '0 0 40px rgba(59, 130, 246, 0.7)',
            animation: 'rareReveal 1s ease-out'
        },
        legendary: {
            color: '#f59e0b',
            bgGradient: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)',
            glow: '0 0 60px rgba(245, 158, 11, 0.8)',
            animation: 'legendaryReveal 1.5s ease-out'
        }
    },

    // Reward type icons
    typeIcons: {
        tribe: '👥',
        hunt: '💎',
        self: '🏆'
    },

    // Initialize module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('rollRewardBtn')?.addEventListener('click', () => {
            this.rollReward();
        });
    },

    // Main render function
    render() {
        this.renderRewardCollection();
        this.renderRewardHistory();
        this.renderRewardStats();
    },

    // Render reward collection/gallery
    renderRewardCollection() {
        const container = document.getElementById('rewardsCollection');
        if (!container) return;

        const allRewards = Storage.getRewards();
        const userRewards = Storage.getUserRewards();
        
        // Group user rewards by reward_id
        const earnedCounts = {};
        userRewards.forEach(ur => {
            earnedCounts[ur.reward_id] = (earnedCounts[ur.reward_id] || 0) + 1;
        });

        container.innerHTML = `
            <div class="rewards-grid">
                ${allRewards.map(reward => {
                    const earned = earnedCounts[reward.id] || 0;
                    const config = this.rarityConfig[reward.rarity];
                    
                    return `
                        <div class="reward-card ${earned > 0 ? 'earned' : 'locked'}" data-reward-id="${reward.id}">
                            <div class="reward-card-inner" style="background: ${earned > 0 ? config.bgGradient : '#374151'}">
                                <div class="reward-card-icon">${reward.icon}</div>
                                <div class="reward-card-name">${reward.name}</div>
                                <div class="reward-card-rarity" style="color: ${config.color}">${reward.rarity.toUpperCase()}</div>
                                ${earned > 0 ? `
                                    <div class="reward-card-count">×${earned}</div>
                                ` : `
                                    <div class="reward-card-locked">🔒</div>
                                `}
                            </div>
                            <div class="reward-card-tooltip">
                                <p class="tooltip-description">${reward.description}</p>
                                <p class="tooltip-value">+${reward.value} XP</p>
                                <p class="tooltip-type">${this.typeIcons[reward.reward_type]} ${reward.reward_type}</p>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    // Render reward history
    renderRewardHistory() {
        const container = document.getElementById('rewardHistory');
        if (!container) return;

        const userRewards = Storage.getUserRewards();
        
        if (userRewards.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎁</div>
                    <div class="empty-state-text">No rewards earned yet. Complete habits to earn rewards!</div>
                </div>
            `;
            return;
        }

        // Show last 20 rewards
        const recentRewards = userRewards.slice(-20).reverse();

        container.innerHTML = `
            <div class="reward-history-list">
                ${recentRewards.map(reward => {
                    const config = this.rarityConfig[reward.rarity];
                    const date = new Date(reward.receivedAt);
                    
                    return `
                        <div class="history-item ${reward.rarity}">
                            <div class="history-icon" style="background: ${config.bgGradient}">
                                ${reward.icon || '🎁'}
                            </div>
                            <div class="history-info">
                                <div class="history-name">${reward.reward_name}</div>
                                <div class="history-date">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</div>
                            </div>
                            <div class="history-value" style="color: ${config.color}">+${reward.value} XP</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    // Render reward statistics
    renderRewardStats() {
        const container = document.getElementById('rewardStats');
        if (!container) return;

        const history = Storage.getRewardHistory();
        const userRewards = Storage.getUserRewards();

        const totalXP = userRewards.reduce((sum, r) => sum + (r.value || 0), 0);
        const rewardRate = history.total_rolls > 0 
            ? Math.round((history.total_rewards / history.total_rolls) * 100)
            : 0;

        container.innerHTML = `
            <div class="stats-grid reward-stats-grid">
                <div class="stat-card reward-stat">
                    <div class="stat-icon">🎁</div>
                    <div class="stat-info">
                        <div class="stat-value">${history.total_rewards}</div>
                        <div class="stat-label">Rewards Earned</div>
                    </div>
                </div>
                <div class="stat-card reward-stat">
                    <div class="stat-icon">🎲</div>
                    <div class="stat-info">
                        <div class="stat-value">${history.total_rolls}</div>
                        <div class="stat-label">Total Rolls</div>
                    </div>
                </div>
                <div class="stat-card reward-stat">
                    <div class="stat-icon">📊</div>
                    <div class="stat-info">
                        <div class="stat-value">${rewardRate}%</div>
                        <div class="stat-label">Reward Rate</div>
                    </div>
                </div>
                <div class="stat-card reward-stat">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-info">
                        <div class="stat-value">${totalXP}</div>
                        <div class="stat-label">XP from Rewards</div>
                    </div>
                </div>
            </div>
            
            <div class="rarity-breakdown">
                <h4>Rarity Breakdown</h4>
                <div class="rarity-bars">
                    ${this.renderRarityBar('common', history.common_count || 0, history.total_rewards)}
                    ${this.renderRarityBar('uncommon', history.uncommon_count || 0, history.total_rewards)}
                    ${this.renderRarityBar('rare', history.rare_count || 0, history.total_rewards)}
                    ${this.renderRarityBar('legendary', history.legendary_count || 0, history.total_rewards)}
                </div>
            </div>
        `;
    },

    // Render rarity progress bar
    renderRarityBar(rarity, count, total) {
        const config = this.rarityConfig[rarity];
        const percentage = total > 0 ? Math.round((count / total) * 100) : 0;

        return `
            <div class="rarity-bar-item">
                <div class="rarity-bar-header">
                    <span class="rarity-bar-label" style="color: ${config.color}">${rarity.toUpperCase()}</span>
                    <span class="rarity-bar-count">${count}</span>
                </div>
                <div class="rarity-bar-track">
                    <div class="rarity-bar-fill" style="width: ${percentage}%; background: ${config.bgGradient}"></div>
                </div>
            </div>
        `;
    },

    // Roll for a reward (manual trigger)
    rollReward() {
        const reward = Storage.rollForReward();
        this.showRewardRevealAnimation(reward);
    },

    // Show reward reveal animation
    showRewardRevealAnimation(reward) {
        const overlay = document.createElement('div');
        overlay.className = 'reward-reveal-overlay';
        overlay.innerHTML = `
            <div class="reward-reveal-container">
                ${reward ? `
                    <div class="reward-reveal-card ${reward.rarity}">
                        <div class="reveal-particles"></div>
                        <div class="reveal-content">
                            <div class="reveal-icon">${reward.icon}</div>
                            <div class="reveal-name">${reward.name}</div>
                            <div class="reveal-rarity">${reward.rarity.toUpperCase()}</div>
                            <div class="reveal-description">${reward.description}</div>
                            <div class="reveal-value">+${reward.value} XP</div>
                        </div>
                    </div>
                ` : `
                    <div class="reward-reveal-card empty">
                        <div class="reveal-content">
                            <div class="reveal-icon">💨</div>
                            <div class="reveal-name">No Reward</div>
                            <div class="reveal-description">Better luck next time!</div>
                        </div>
                    </div>
                `}
            </div>
        `;

        document.body.appendChild(overlay);

        // Add animation class
        requestAnimationFrame(() => {
            overlay.classList.add('active');
        });

        // Create particles for legendary rewards
        if (reward && reward.rarity === 'legendary') {
            this.createLegendaryParticles(overlay.querySelector('.reveal-particles'));
            App.celebrate();
        }

        // Close on click
        overlay.addEventListener('click', () => {
            overlay.classList.remove('active');
            setTimeout(() => overlay.remove(), 300);
            this.render();
            App.updateUserStats();
        });

        // Auto close after 3 seconds
        setTimeout(() => {
            if (document.body.contains(overlay)) {
                overlay.classList.remove('active');
                setTimeout(() => overlay.remove(), 300);
                this.render();
                App.updateUserStats();
            }
        }, 3000);
    },

    // Create particle effects for legendary rewards
    createLegendaryParticles(container) {
        if (!container) return;

        const colors = ['#fbbf24', '#f59e0b', '#d97706', '#ffffff'];
        
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'legendary-particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: 50%;
                left: 50%;
                top: 50%;
                animation: particleFly ${Math.random() * 1 + 0.5}s ease-out forwards;
                --tx: ${(Math.random() - 0.5) * 300}px;
                --ty: ${(Math.random() - 0.5) * 300}px;
            `;
            container.appendChild(particle);
        }
    },

    // Show near-miss feedback
    showNearMiss() {
        App.showToast('So close! Almost got a reward! 😮', 'warning');
    },

    // Check for reward on habit completion
    checkRewardOnHabitCompletion() {
        // 30% base chance
        if (Math.random() < 0.3) {
            const reward = Storage.rollForReward();
            if (reward) {
                this.showRewardRevealAnimation(reward);
                return reward;
            }
        }
        
        // Check for near-miss (5% below threshold)
        if (Math.random() < 0.05) {
            this.showNearMiss();
        }
        
        return null;
    },

    // Get reward summary for dashboard
    getRewardSummary() {
        const history = Storage.getRewardHistory();
        const userRewards = Storage.getUserRewards();
        
        return {
            totalRewards: history.total_rewards,
            totalXP: userRewards.reduce((sum, r) => sum + (r.value || 0), 0),
            legendaryCount: history.legendary_count || 0,
            recentRewards: userRewards.slice(-5).reverse()
        };
    },

    // Render mini reward display for dashboard
    renderMiniRewardDisplay() {
        const summary = this.getRewardSummary();
        
        return `
            <div class="mini-rewards-display">
                <div class="mini-reward-stat">
                    <span class="mini-icon">🎁</span>
                    <span class="mini-value">${summary.totalRewards}</span>
                </div>
                <div class="mini-reward-stat">
                    <span class="mini-icon">⭐</span>
                    <span class="mini-value">${summary.totalXP} XP</span>
                </div>
                ${summary.legendaryCount > 0 ? `
                    <div class="mini-reward-stat legendary">
                        <span class="mini-icon">👑</span>
                        <span class="mini-value">${summary.legendaryCount}</span>
                    </div>
                ` : ''}
            </div>
        `;
    }
};

// Export for use in other modules
window.Rewards = Rewards;