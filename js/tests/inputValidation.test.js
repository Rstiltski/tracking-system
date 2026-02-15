/**
 * Tests for input validation functionality
 */
describe('Input Validation', () => {
  describe('Validation Rules', () => {
    describe('required', () => {
      it('should return error for empty value', () => {
        const result = window.Validation.rules.required('');
        expect(result).toBe('This field is required');
      });

      it('should return error for null value', () => {
        const result = window.Validation.rules.required(null);
        expect(result).toBe('This field is required');
      });

      it('should return null for valid value', () => {
        const result = window.Validation.rules.required('test');
        expect(result).toBeNull();
      });
    });

    describe('minLength', () => {
      it('should return error for value shorter than minimum', () => {
        const rule = window.Validation.rules.minLength(5);
        const result = rule('test');
        expect(result).toBe('Must be at least 5 characters');
      });

      it('should return null for value meeting minimum', () => {
        const rule = window.Validation.rules.minLength(5);
        const result = rule('testing');
        expect(result).toBeNull();
      });
    });

    describe('maxLength', () => {
      it('should return error for value longer than maximum', () => {
        const rule = window.Validation.rules.maxLength(5);
        const result = rule('testing');
        expect(result).toBe('Must be no more than 5 characters');
      });

      it('should return null for value within maximum', () => {
        const rule = window.Validation.rules.maxLength(5);
        const result = rule('test');
        expect(result).toBeNull();
      });
    });

    describe('min', () => {
      it('should return error for value less than minimum', () => {
        const rule = window.Validation.rules.min(10);
        const result = rule(5);
        expect(result).toBe('Must be at least 10');
      });

      it('should return null for value meeting minimum', () => {
        const rule = window.Validation.rules.min(10);
        const result = rule(15);
        expect(result).toBeNull();
      });
    });

    describe('max', () => {
      it('should return error for value greater than maximum', () => {
        const rule = window.Validation.rules.max(100);
        const result = rule(150);
        expect(result).toBe('Must be no more than 100');
      });

      it('should return null for value within maximum', () => {
        const rule = window.Validation.rules.max(100);
        const result = rule(50);
        expect(result).toBeNull();
      });
    });

    describe('positiveNumber', () => {
      it('should return error for negative number', () => {
        const result = window.Validation.rules.positiveNumber(-5);
        expect(result).toBe('Must be a positive number');
      });

      it('should return null for positive number', () => {
        const result = window.Validation.rules.positiveNumber(5);
        expect(result).toBeNull();
      });
    });

    describe('number', () => {
      it('should return error for non-numeric value', () => {
        const result = window.Validation.rules.number('abc');
        expect(result).toBe('Must be a valid number');
      });

      it('should return null for numeric value', () => {
        const result = window.Validation.rules.number('123');
        expect(result).toBeNull();
      });
    });

    describe('email', () => {
      it('should return error for invalid email', () => {
        const result = window.Validation.rules.email('invalid-email');
        expect(result).toBe('Must be a valid email address');
      });

      it('should return null for valid email', () => {
        const result = window.Validation.rules.email('test@example.com');
        expect(result).toBeNull();
      });
    });

    describe('date', () => {
      it('should return error for invalid date', () => {
        const result = window.Validation.rules.date('invalid-date');
        expect(result).toBe('Must be a valid date');
      });

      it('should return null for valid date', () => {
        const result = window.Validation.rules.date('2026-02-14');
        expect(result).toBeNull();
      });
    });

    describe('futureDate', () => {
      it('should return error for past date', () => {
        const pastDate = new Date();
        pastDate.setDate(pastDate.getDate() - 1);
        const result = window.Validation.rules.futureDate(pastDate.toISOString());
        expect(result).toBe('Date must be in the future');
      });

      it('should return null for future date', () => {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + 1);
        const result = window.Validation.rules.futureDate(futureDate.toISOString());
        expect(result).toBeNull();
      });
    });

    describe('percentage', () => {
      it('should return error for value outside 0-100', () => {
        const result = window.Validation.rules.percentage(150);
        expect(result).toBe('Must be between 0 and 100');
      });

      it('should return null for valid percentage', () => {
        const result = window.Validation.rules.percentage(50);
        expect(result).toBeNull();
      });
    });

    describe('habitName', () => {
      it('should return error for empty habit name', () => {
        const result = window.Validation.rules.habitName('');
        expect(result).toBe('Habit name is required');
      });

      it('should return error for habit name too long', () => {
        const result = window.Validation.rules.habitName('a'.repeat(51));
        expect(result).toBe('Habit name must be 50 characters or less');
      });

      it('should return null for valid habit name', () => {
        const result = window.Validation.rules.habitName('Exercise');
        expect(result).toBeNull();
      });
    });

    describe('taskTitle', () => {
      it('should return error for empty task title', () => {
        const result = window.Validation.rules.taskTitle('');
        expect(result).toBe('Task title is required');
      });

      it('should return error for task title too long', () => {
        const result = window.Validation.rules.taskTitle('a'.repeat(101));
        expect(result).toBe('Task title must be 100 characters or less');
      });

      it('should return null for valid task title', () => {
        const result = window.Validation.rules.taskTitle('Complete project');
        expect(result).toBeNull();
      });
    });

    describe('transactionAmount', () => {
      it('should return error for empty amount', () => {
        const result = window.Validation.rules.transactionAmount('');
        expect(result).toBe('Amount is required');
      });

      it('should return error for non-numeric amount', () => {
        const result = window.Validation.rules.transactionAmount('abc');
        expect(result).toBe('Must be a valid number');
      });

      it('should return error for zero or negative amount', () => {
        const result = window.Validation.rules.transactionAmount(0);
        expect(result).toBe('Amount must be greater than 0');
      });

      it('should return null for valid amount', () => {
        const result = window.Validation.rules.transactionAmount(100);
        expect(result).toBeNull();
      });
    });

    describe('weight', () => {
      it('should return error for empty weight', () => {
        const result = window.Validation.rules.weight('');
        expect(result).toBe('Weight is required');
      });

      it('should return error for weight out of range', () => {
        const result = window.Validation.rules.weight(10);
        expect(result).toBe('Weight must be between 20 and 500 kg');
      });

      it('should return null for valid weight', () => {
        const result = window.Validation.rules.weight(70);
        expect(result).toBeNull();
      });
    });

    describe('sleep', () => {
      it('should return error for empty sleep', () => {
        const result = window.Validation.rules.sleep('');
        expect(result).toBe('Sleep hours is required');
      });

      it('should return error for sleep out of range', () => {
        const result = window.Validation.rules.sleep(25);
        expect(result).toBe('Sleep must be between 0 and 24 hours');
      });

      it('should return null for valid sleep', () => {
        const result = window.Validation.rules.sleep(8);
        expect(result).toBeNull();
      });
    });

    describe('timeDuration', () => {
      it('should return error for empty duration', () => {
        const result = window.Validation.rules.timeDuration('');
        expect(result).toBe('Duration is required');
      });

      it('should return error for duration too long', () => {
        const result = window.Validation.rules.timeDuration(1500);
        expect(result).toBe('Duration cannot exceed 24 hours (1440 minutes)');
      });

      it('should return null for valid duration', () => {
        const result = window.Validation.rules.timeDuration(60);
        expect(result).toBeNull();
      });
    });
  });

  describe('validateField', () => {
    it('should return first error found', () => {
      const rules = [
        window.Validation.rules.required,
        window.Validation.rules.minLength(5)
      ];
      const result = window.Validation.validateField('', rules);
      expect(result).toBe('This field is required');
    });

    it('should return null when all rules pass', () => {
      const rules = [
        window.Validation.rules.required,
        window.Validation.rules.minLength(3)
      ];
      const result = window.Validation.validateField('test', rules);
      expect(result).toBeNull();
    });
  });

  describe('validate', () => {
    it('should validate multiple fields', () => {
      const fields = {
        name: {
          value: '',
          rules: [window.Validation.rules.required]
        },
        email: {
          value: 'invalid',
          rules: [window.Validation.rules.email]
        }
      };

      const result = window.Validation.validate(fields);

      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('This field is required');
      expect(result.errors.email).toBe('Must be a valid email address');
    });

    it('should return valid when all fields pass', () => {
      const fields = {
        name: {
          value: 'Test',
          rules: [window.Validation.rules.required]
        }
      };

      const result = window.Validation.validate(fields);

      expect(result.isValid).toBe(true);
      expect(Object.keys(result.errors)).toHaveLength(0);
    });
  });

  describe('showFieldError', () => {
    it('should add error class and message to input', () => {
      // Arrange
      const input = document.createElement('input');
      const parent = document.createElement('div');
      parent.appendChild(input);
      
      // Act
      window.Validation.showFieldError(input, 'Test error message');
      
      // Assert
      expect(input.classList.contains('input-error')).toBe(true);
      const errorEl = parent.querySelector('.validation-error');
      expect(errorEl).not.toBeNull();
      expect(errorEl.textContent).toBe('Test error message');
    });

    it('should replace existing error message', () => {
      // Arrange
      const input = document.createElement('input');
      const parent = document.createElement('div');
      parent.appendChild(input);
      
      // Act
      window.Validation.showFieldError(input, 'First error');
      window.Validation.showFieldError(input, 'Second error');
      
      // Assert
      const errorElements = parent.querySelectorAll('.validation-error');
      expect(errorElements).toHaveLength(1);
      expect(errorElements[0].textContent).toBe('Second error');
    });
  });

  describe('clearFieldError', () => {
    it('should remove error class and message from input', () => {
      // Arrange
      const input = document.createElement('input');
      const parent = document.createElement('div');
      parent.appendChild(input);
      window.Validation.showFieldError(input, 'Test error');
      
      // Act
      window.Validation.clearFieldError(input);
      
      // Assert
      expect(input.classList.contains('input-error')).toBe(false);
      const errorEl = parent.querySelector('.validation-error');
      expect(errorEl).toBeNull();
    });
  });

  describe('showFieldSuccess', () => {
    it('should add success class to input', () => {
      // Arrange
      const input = document.createElement('input');
      
      // Act
      window.Validation.showFieldSuccess(input);
      
      // Assert
      expect(input.classList.contains('input-valid')).toBe(true);
      expect(input.classList.contains('input-error')).toBe(false);
    });
  });
});