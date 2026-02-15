/**
 * Validation Module - Handles form input validation
 */

const Validation = {
    // Validation rules
    rules: {
        required: (value) => {
            if (value === null || value === undefined || value === '') {
                return 'This field is required';
            }
            return null;
        },
        
        minLength: (min) => (value) => {
            if (value && value.length < min) {
                return `Must be at least ${min} characters`;
            }
            return null;
        },
        
        maxLength: (max) => (value) => {
            if (value && value.length > max) {
                return `Must be no more than ${max} characters`;
            }
            return null;
        },
        
        min: (minVal) => (value) => {
            const num = parseFloat(value);
            if (!isNaN(num) && num < minVal) {
                return `Must be at least ${minVal}`;
            }
            return null;
        },
        
        max: (maxVal) => (value) => {
            const num = parseFloat(value);
            if (!isNaN(num) && num > maxVal) {
                return `Must be no more than ${maxVal}`;
            }
            return null;
        },
        
        positiveNumber: (value) => {
            const num = parseFloat(value);
            if (!isNaN(num) && num < 0) {
                return 'Must be a positive number';
            }
            return null;
        },
        
        number: (value) => {
            if (value && isNaN(parseFloat(value))) {
                return 'Must be a valid number';
            }
            return null;
        },
        
        email: (value) => {
            if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                return 'Must be a valid email address';
            }
            return null;
        },
        
        date: (value) => {
            if (value && isNaN(Date.parse(value))) {
                return 'Must be a valid date';
            }
            return null;
        },
        
        futureDate: (value) => {
            if (value) {
                const date = new Date(value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                if (date < today) {
                    return 'Date must be in the future';
                }
            }
            return null;
        },
        
        pastDate: (value) => {
            if (value) {
                const date = new Date(value);
                const today = new Date();
                today.setHours(23, 59, 59, 999);
                if (date > today) {
                    return 'Date cannot be in the future';
                }
            }
            return null;
        },
        
        currency: (value) => {
            if (value && !/^\d+(\.\d{1,2})?$/.test(value.toString())) {
                return 'Must be a valid currency amount';
            }
            return null;
        },
        
        percentage: (value) => {
            const num = parseFloat(value);
            if (!isNaN(num) && (num < 0 || num > 100)) {
                return 'Must be between 0 and 100';
            }
            return null;
        },
        
        habitName: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Habit name is required';
            }
            if (value.length > 50) {
                return 'Habit name must be 50 characters or less';
            }
            return null;
        },
        
        taskTitle: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Task title is required';
            }
            if (value.length > 100) {
                return 'Task title must be 100 characters or less';
            }
            return null;
        },
        
        goalTitle: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Goal title is required';
            }
            if (value.length > 100) {
                return 'Goal title must be 100 characters or less';
            }
            return null;
        },
        
        transactionAmount: (value) => {
            if (!value) {
                return 'Amount is required';
            }
            const num = parseFloat(value);
            if (isNaN(num)) {
                return 'Must be a valid number';
            }
            if (num <= 0) {
                return 'Amount must be greater than 0';
            }
            if (num > 999999999) {
                return 'Amount is too large';
            }
            return null;
        },
        
        weight: (value) => {
            if (!value) {
                return 'Weight is required';
            }
            const num = parseFloat(value);
            if (isNaN(num)) {
                return 'Must be a valid number';
            }
            if (num < 20 || num > 500) {
                return 'Weight must be between 20 and 500 kg';
            }
            return null;
        },
        
        sleep: (value) => {
            if (!value) {
                return 'Sleep hours is required';
            }
            const num = parseFloat(value);
            if (isNaN(num)) {
                return 'Must be a valid number';
            }
            if (num < 0 || num > 24) {
                return 'Sleep must be between 0 and 24 hours';
            }
            return null;
        },
        
        timeDuration: (value) => {
            if (!value) {
                return 'Duration is required';
            }
            const num = parseInt(value);
            if (isNaN(num)) {
                return 'Must be a valid number';
            }
            if (num < 1) {
                return 'Duration must be at least 1 minute';
            }
            if (num > 1440) {
                return 'Duration cannot exceed 24 hours (1440 minutes)';
            }
            return null;
        }
    },
    
    // Validate a single field
    validateField(value, rules) {
        for (const rule of rules) {
            const error = rule(value);
            if (error) {
                return error;
            }
        }
        return null;
    },
    
    // Validate multiple fields
    validate(fields) {
        const errors = {};
        let isValid = true;
        
        for (const [fieldName, config] of Object.entries(fields)) {
            const error = this.validateField(config.value, config.rules);
            if (error) {
                errors[fieldName] = error;
                isValid = false;
            }
        }
        
        return { isValid, errors };
    },
    
    // Show validation error on input
    showFieldError(input, message) {
        input.classList.add('input-error');
        input.classList.remove('input-valid');
        
        // Remove existing error message
        const existingError = input.parentElement.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message using CSS class
        const errorEl = document.createElement('div');
        errorEl.className = 'validation-error';
        errorEl.textContent = message;
        input.parentElement.appendChild(errorEl);
    },
    
    // Clear validation error from input
    clearFieldError(input) {
        input.classList.remove('input-error');
        input.classList.remove('input-valid');
        
        const existingError = input.parentElement.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
    },
    
    // Show success state on input
    showFieldSuccess(input) {
        input.classList.remove('input-error');
        input.classList.add('input-valid');
        
        const existingError = input.parentElement.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
    },
    
    // Validate form in real-time
    setupRealTimeValidation(formId, validationConfig) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        for (const [fieldName, config] of Object.entries(validationConfig)) {
            const input = form.querySelector(`[name="${fieldName}"]`) || 
                          form.querySelector(`#${fieldName}`);
            
            if (input) {
                // Validate on blur
                input.addEventListener('blur', () => {
                    const error = this.validateField(input.value, config.rules);
                    if (error) {
                        this.showFieldError(input, error);
                    } else {
                        this.showFieldSuccess(input);
                    }
                });
                
                // Clear error on focus
                input.addEventListener('focus', () => {
                    this.clearFieldError(input);
                });
                
                // Validate on input (optional, for immediate feedback)
                if (config.validateOnInput) {
                    input.addEventListener('input', () => {
                        const error = this.validateField(input.value, config.rules);
                        if (error) {
                            this.showFieldError(input, error);
                        } else {
                            this.showFieldSuccess(input);
                        }
                    });
                }
            }
        }
    },
    
    // Validate form on submit
    validateForm(formId, validationConfig) {
        const form = document.getElementById(formId);
        if (!form) return { isValid: false, errors: { form: 'Form not found' } };
        
        const fields = {};
        
        for (const [fieldName, config] of Object.entries(validationConfig)) {
            const input = form.querySelector(`[name="${fieldName}"]`) || 
                          form.querySelector(`#${fieldName}`);
            
            if (input) {
                fields[fieldName] = {
                    value: input.value,
                    rules: config.rules
                };
            }
        }
        
        const result = this.validate(fields);
        
        // Show errors on fields
        for (const [fieldName, error] of Object.entries(result.errors)) {
            const input = form.querySelector(`[name="${fieldName}"]`) || 
                          form.querySelector(`#${fieldName}`);
            if (input) {
                this.showFieldError(input, error);
            }
        }
        
        return result;
    },
    
    // Common validation presets
    presets: {
        habit: {
            name: {
                rules: [Validation.rules.habitName],
                validateOnInput: true
            }
        },
        
        task: {
            title: {
                rules: [Validation.rules.taskTitle],
                validateOnInput: true
            },
            dueDate: {
                rules: [Validation.rules.date, Validation.rules.futureDate]
            }
        },
        
        transaction: {
            amount: {
                rules: [Validation.rules.transactionAmount],
                validateOnInput: true
            },
            description: {
                rules: [Validation.rules.maxLength(100)]
            }
        },
        
        goal: {
            title: {
                rules: [Validation.rules.goalTitle],
                validateOnInput: true
            },
            target: {
                rules: [Validation.rules.required, Validation.rules.positiveNumber]
            },
            deadline: {
                rules: [Validation.rules.date, Validation.rules.futureDate]
            }
        },
        
        health: {
            weight: {
                rules: [Validation.rules.weight],
                validateOnInput: true
            },
            sleep: {
                rules: [Validation.rules.sleep],
                validateOnInput: true
            }
        },
        
        timeEntry: {
            duration: {
                rules: [Validation.rules.timeDuration],
                validateOnInput: true
            }
        }
    }
};

// Export for use in other modules
window.Validation = Validation;