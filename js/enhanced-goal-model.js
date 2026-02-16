/**
 * Enhanced Goal Model - Advanced goal tracking with conditions and variables
 * Extends the basic goal model with perfice-inspired features
 */

class EnhancedGoal {
    /**
     * Create an enhanced goal
     * @param {Object} options - Goal configuration options
     * @param {string} options.id - Unique identifier
     * @param {string} options.title - Goal title
     * @param {string} options.description - Goal description
     * @param {string} options.target - Target value or description
     * @param {number} options.progress - Current progress percentage (0-100)
     * @param {number} options.streak - Current streak count
     * @param {Array} options.conditions - Array of goal conditions
     * @param {string} options.deadline - Deadline date (ISO string)
     * @param {*} options.currentValue - Current value toward the goal
     * @param {string} options.color - Color for display
     * @param {string} options.createdAt - Creation timestamp
     * @param {string} options.updatedAt - Last update timestamp
     */
    constructor(options = {}) {
        this.id = options.id || this.generateId();
        this.title = options.title || '';
        this.description = options.description || '';
        this.target = options.target || '';
        this.progress = options.progress || 0;
        this.streak = options.streak || 0;
        this.conditions = options.conditions || [];
        this.deadline = options.deadline || null;
        this.currentValue = options.currentValue || 0;
        this.color = options.color || '#6366f1';
        this.createdAt = options.createdAt || new Date().toISOString();
        this.updatedAt = options.updatedAt || new Date().toISOString();
    }

    /**
     * Generate a unique ID
     * @returns {string} Unique identifier
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Add a condition to the goal
     * @param {string} type - Condition type (COMPARISON, GOAL_MET, etc.)
     * @param {Object} value - Condition value/data
     * @returns {Object} Added condition
     */
    addCondition(type, value) {
        const condition = {
            id: 'cond_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            type,
            value
        };
        
        this.conditions.push(condition);
        return condition;
    }

    /**
     * Remove a condition by ID
     * @param {string} conditionId - ID of condition to remove
     * @returns {boolean} True if condition was removed
     */
    removeCondition(conditionId) {
        const initialLength = this.conditions.length;
        this.conditions = this.conditions.filter(cond => cond.id !== conditionId);
        return initialLength > this.conditions.length;
    }

    /**
     * Check if all conditions are met
     * @returns {boolean} True if all conditions are met
     */
    areAllConditionsMet() {
        if (!this.conditions || this.conditions.length === 0) {
            // If no conditions, check if progress is 100%
            return this.progress >= 100;
        }

        // Evaluate each condition
        for (const condition of this.conditions) {
            if (!this.evaluateCondition(condition)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Evaluate a single condition
     * @param {Object} condition - Condition to evaluate
     * @returns {boolean} True if condition is met
     */
    evaluateCondition(condition) {
        if (condition.type === 'COMPARISON') {
            return this.evaluateComparisonCondition(condition.value);
        } else if (condition.type === 'GOAL_MET') {
            return this.evaluateGoalMetCondition(condition.value);
        }
        return false;
    }

    /**
     * Evaluate a comparison condition
     * @param {Object} conditionValue - Comparison condition value
     * @returns {boolean} True if condition is met
     */
    evaluateComparisonCondition(conditionValue) {
        const targetValue = this.parseValue(conditionValue.target);
        const actualValue = this.parseValue(this.currentValue);

        if (targetValue === null || actualValue === null) {
            return false; // Can't evaluate
        }

        switch (conditionValue.operator) {
            case 'EQUAL':
                return actualValue === targetValue;
            case 'NOT_EQUAL':
                return actualValue !== targetValue;
            case 'GREATER_THAN':
                return actualValue > targetValue;
            case 'GREATER_THAN_EQUAL':
                return actualValue >= targetValue;
            case 'LESS_THAN':
                return actualValue < targetValue;
            case 'LESS_THAN_EQUAL':
                return actualValue <= targetValue;
            default:
                return false;
        }
    }

    /**
     * Evaluate a goal-met condition
     * @param {Object} conditionValue - Goal-met condition value
     * @returns {boolean} True if condition is met
     */
    evaluateGoalMetCondition(conditionValue) {
        // This would typically check if another goal is met
        // For now, we'll return false as this requires cross-goal evaluation
        // which would be handled by the goal manager
        return false;
    }

    /**
     * Parse a value from string to number
     * @param {*} value - Value to parse
     * @returns {number|null} Parsed number or null if invalid
     */
    parseValue(value) {
        if (typeof value === 'number') {
            return value;
        }
        if (typeof value === 'string') {
            const parsed = parseFloat(value);
            return isNaN(parsed) ? null : parsed;
        }
        return null;
    }

    /**
     * Update progress based on conditions
     */
    updateProgressFromConditions() {
        if (!this.conditions || this.conditions.length === 0) {
            // If no conditions, progress remains as is
            return;
        }

        // Calculate progress based on how many conditions are met
        let metConditions = 0;
        for (const condition of this.conditions) {
            if (this.evaluateCondition(condition)) {
                metConditions++;
            }
        }

        // Set progress as percentage of conditions met
        this.progress = Math.min(100, Math.round((metConditions / this.conditions.length) * 100));
        this.updatedAt = new Date().toISOString();
    }

    /**
     * Update streak based on conditions
     */
    updateStreakFromConditions() {
        if (this.areAllConditionsMet()) {
            this.streak = (this.streak || 0) + 1;
        } else {
            this.streak = 0; // Reset streak if conditions not met
        }
        this.updatedAt = new Date().toISOString();
    }

    /**
     * Check if goal is completed
     * @returns {boolean} True if goal is completed
     */
    isCompleted() {
        return this.progress >= 100 || this.areAllConditionsMet();
    }

    /**
     * Convert to plain object for storage
     * @returns {Object} Plain object representation
     */
    toObject() {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            target: this.target,
            progress: this.progress,
            streak: this.streak,
            conditions: this.conditions,
            deadline: this.deadline,
            currentValue: this.currentValue,
            color: this.color,
            createdAt: this.createdAt,
            updatedAt: this.updatedAt
        };
    }

    /**
     * Create instance from plain object
     * @param {Object} obj - Plain object to convert
     * @returns {EnhancedGoal} New EnhancedGoal instance
     */
    static fromObject(obj) {
        return new EnhancedGoal(obj);
    }
}

// Export for use in other modules
window.EnhancedGoal = EnhancedGoal;