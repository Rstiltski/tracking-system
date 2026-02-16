/**
 * Variable-based Goal Tracking System
 * Inspired by perfice's variable and goal system
 */

const VariableGoalTracker = {
    // Variable types
    VariableType: {
        LIST: "LIST",
        AGGREGATE: "AGGREGATE",
        GOAL: "GOAL",
        CALCULATION: "CALCULATION",
        TAG: "TAG",
        LATEST: "LATEST",
        GROUP: "GROUP",
        GOAL_STREAK: "GOAL_STREAK"
    },

    // Comparison operators
    ComparisonOperator: {
        EQUAL: "EQUAL",
        NOT_EQUAL: "NOT_EQUAL",
        GREATER_THAN: "GREATER_THAN",
        GREATER_THAN_EQUAL: "GREATER_THAN_EQUAL",
        LESS_THAN: "LESS_THAN",
        LESS_THAN_EQUAL: "LESS_THAN_EQUAL"
    },

    // Goal condition types
    GoalConditionType: {
        COMPARISON: "COMPARISON",
        GOAL_MET: "GOAL_MET"
    },

    // Primitive value types
    PrimitiveValueType: {
        STRING: "STRING",
        NUMBER: "NUMBER",
        BOOLEAN: "BOOLEAN",
        LIST: "LIST",
        MAP: "MAP",
        JOURNAL_ENTRY: "JOURNAL_ENTRY",
        TAG_ENTRY: "TAG_ENTRY",
        DISPLAY: "DISPLAY",
        COMPARISON_RESULT: "COMPARISON_RESULT",
        NULL: "NULL"
    },

    // Create a primitive value
    createPrimitiveValue(type, value) {
        return { type, value };
    },

    // Create a number primitive
    pNumber(value) {
        return this.createPrimitiveValue(this.PrimitiveValueType.NUMBER, value);
    },

    // Create a boolean primitive
    pBoolean(value) {
        return this.createPrimitiveValue(this.PrimitiveValueType.BOOLEAN, value);
    },

    // Create a map primitive
    pMap(value) {
        return this.createPrimitiveValue(this.PrimitiveValueType.MAP, value);
    },

    // Create a comparison result primitive
    pComparisonResult(source, target, result) {
        return this.createPrimitiveValue(this.PrimitiveValueType.COMPARISON_RESULT, {
            source,
            target,
            met: result
        });
    },

    // Create a goal condition
    createGoalCondition(type, value) {
        return {
            id: 'cond_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            type,
            value
        };
    },

    // Create a comparison goal condition
    createComparisonCondition(source, operator, target) {
        return {
            source: source ? { value: source, constant: true } : null,
            operator,
            target: target ? { value: target, constant: true } : null
        };
    },

    // Create a goal-met condition
    createGoalMetCondition(goalVariableId) {
        return {
            goalVariableId
        };
    },

    // Evaluate a comparison condition
    async evaluateComparisonCondition(condition, evaluator) {
        let sourceValue = condition.source ? 
            (condition.source.constant ? condition.source.value : 
             await evaluator.evaluateVariable(condition.source.value.value)) : 
            this.pNumber(0.0);

        let targetValue = condition.target ? 
            (condition.target.constant ? condition.target.value : 
             await evaluator.evaluateVariable(condition.target.value.value)) : 
            this.pNumber(0.0);

        // Convert to numbers for comparison
        const sourceNum = this.primitiveAsNumber(sourceValue);
        const targetNum = this.primitiveAsNumber(targetValue);

        let result = false;
        switch (condition.operator) {
            case this.ComparisonOperator.EQUAL:
                result = sourceNum === targetNum;
                break;
            case this.ComparisonOperator.NOT_EQUAL:
                result = sourceNum !== targetNum;
                break;
            case this.ComparisonOperator.GREATER_THAN:
                result = sourceNum > targetNum;
                break;
            case this.ComparisonOperator.GREATER_THAN_EQUAL:
                result = sourceNum >= targetNum;
                break;
            case this.ComparisonOperator.LESS_THAN:
                result = sourceNum < targetNum;
                break;
            case this.ComparisonOperator.LESS_THAN_EQUAL:
                result = sourceNum <= targetNum;
                break;
        }

        return this.pComparisonResult(sourceValue, targetValue, result);
    },

    // Evaluate a goal-met condition
    async evaluateGoalMetCondition(condition, evaluator) {
        let value = await evaluator.evaluateVariable(condition.goalVariableId);

        if (value.type !== this.PrimitiveValueType.MAP) {
            return this.pBoolean(false);
        }

        // Check if all conditions in the map are met
        for (let result of Object.values(value.value)) {
            let bool = false;
            switch (result.type) {
                case this.PrimitiveValueType.BOOLEAN:
                    bool = result.value;
                    break;
                case this.PrimitiveValueType.COMPARISON_RESULT:
                    bool = result.value.met;
                    break;
            }

            if (!bool) return this.pBoolean(false);
        }

        return this.pBoolean(true);
    },

    // Convert primitive to number
    primitiveAsNumber(value) {
        if (value.type === this.PrimitiveValueType.STRING) {
            const num = parseFloat(value.value);
            return isFinite(num) ? num : 0;
        }
        if (value.type === this.PrimitiveValueType.NUMBER) {
            return value.value;
        }
        return 0;
    },

    // Evaluate a goal variable
    async evaluateGoalVariable(goalVariable, evaluator) {
        const result = {};
        for (const condition of goalVariable.conditions) {
            switch (condition.type) {
                case this.GoalConditionType.COMPARISON:
                    result[condition.id] = await this.evaluateComparisonCondition(condition.value, evaluator);
                    break;
                case this.GoalConditionType.GOAL_MET:
                    result[condition.id] = await this.evaluateGoalMetCondition(condition.value, evaluator);
                    break;
            }
        }

        return this.pMap(result);
    },

    // Check if all goal conditions are met
    areAllConditionsMet(conditionResults) {
        for (const primitive of Object.values(conditionResults)) {
            switch (primitive.type) {
                case this.PrimitiveValueType.BOOLEAN:
                    if (!primitive.value) return false;
                    break;
                case this.PrimitiveValueType.COMPARISON_RESULT:
                    if (!primitive.value.met) return false;
                    break;
            }
        }
        return true;
    },

    // Calculate goal streak
    async calculateGoalStreak(goalVariableId, evaluator) {
        // Get the goal variable
        const goalVariable = evaluator.getVariableById(goalVariableId);
        if (!goalVariable || goalVariable.type !== this.VariableType.GOAL) {
            return this.pNumber(0.0);
        }

        // If no conditions, return 0
        if (goalVariable.conditions.length === 0) {
            return this.pNumber(0.0);
        }

        let streak = 0;
        // Look back up to 100 days to calculate streak
        for (let i = 0; i < 100; i++) {
            // Don't include the current date for checking streak
            const offsetDate = new Date();
            offsetDate.setDate(offsetDate.getDate() - (i + 1));

            // Evaluate the goal for the past date
            const value = await evaluator.overrideTimeScope(offsetDate).evaluateVariable(goalVariableId);

            if (value.type !== this.PrimitiveValueType.MAP) {
                break; // Can't evaluate, so streak ends
            }

            if (!this.areAllConditionsMet(value.value)) {
                break; // Condition not met, so streak ends
            }

            streak++;
        }

        return this.pNumber(streak);
    },

    // Create a variable evaluator
    createEvaluator(variables, timeScope = null) {
        return {
            variables,
            timeScope,

            getVariableById(id) {
                return this.variables.find(v => v.id === id);
            },

            async evaluateVariable(variableId) {
                const variable = this.getVariableById(variableId);
                if (!variable) {
                    return VariableGoalTracker.pNumber(0.0);
                }

                switch (variable.type) {
                    case VariableGoalTracker.VariableType.GOAL:
                        return VariableGoalTracker.evaluateGoalVariable(variable, this);
                    case VariableGoalTracker.VariableType.GOAL_STREAK:
                        return VariableGoalTracker.calculateGoalStreak(variable.goalVariableId, this);
                    default:
                        // For other types, return the stored value or a default
                        return variable.value || VariableGoalTracker.pNumber(0.0);
                }
            },

            overrideTimeScope(newTimeScope) {
                return VariableGoalTracker.createEvaluator(this.variables, newTimeScope);
            },

            getTimeScope() {
                return this.timeScope;
            }
        };
    },

    // Create a goal variable
    createGoalVariable(id, name, conditions = [], color = '#6366f1') {
        return {
            id: id || 'goal_' + Date.now(),
            name,
            color,
            type: this.VariableType.GOAL,
            conditions,
            variableId: id || 'var_' + Date.now(), // The variable that tracks the goal
            streakVariableId: 'streak_' + Date.now() // The variable that tracks the streak
        };
    },

    // Add a condition to a goal
    addConditionToGoal(goal, conditionType, conditionValue) {
        const condition = this.createGoalCondition(conditionType, conditionValue);
        goal.conditions = goal.conditions || [];
        goal.conditions.push(condition);
        return goal;
    },

    // Evaluate if a goal is met based on its conditions
    async isGoalMet(goal, evaluator) {
        if (!goal.conditions || goal.conditions.length === 0) {
            // If no conditions, check if progress is at 100%
            return goal.progress >= 100;
        }

        // Evaluate the goal variable
        const result = await evaluator.evaluateVariable(goal.variableId);
        
        if (result.type === this.PrimitiveValueType.MAP) {
            return this.areAllConditionsMet(result.value);
        }

        return false;
    }
};

// Export for use in other modules
window.VariableGoalTracker = VariableGoalTracker;