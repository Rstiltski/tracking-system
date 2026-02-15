/**
 * Tests for real-time chart updates functionality
 */
describe('Real-Time Chart Updates', () => {
  // Mock Chart.js
  const mockChart = {
    destroy: jest.fn(),
    update: jest.fn()
  };
  
  // Mock Chart constructor
  global.Chart = jest.fn(() => mockChart);
  
  // Mock localStorage
  const mockLocalStorage = {
    store: {},
    setItem: jest.fn((key, value) => {
      mockLocalStorage.store[key] = value;
    }),
    getItem: jest.fn((key) => mockLocalStorage.store[key] || null)
  };
  
  // Mock document elements
  const mockCanvas = {
    getContext: jest.fn(() => ({
      createLinearGradient: jest.fn(() => ({
        addColorStop: jest.fn()
      }))
    }))
  };
  
  beforeEach(() => {
    global.localStorage = mockLocalStorage;
    mockLocalStorage.store = {};
    mockChart.destroy.mockClear();
    mockChart.update.mockClear();
    global.Chart.mockClear();
    
    // Reset Charts instance
    window.Charts.instances = {};
    window.Charts.updateInterval = null;
    window.Charts.lastDataState = null;
    
    // Mock document.getElementById
    document.getElementById = jest.fn((id) => {
      if (['weeklyChart', 'expensesChart', 'weightChart', 'sleepChart', 'moodChart', 'timeChart', 'financialTrendsChart'].includes(id)) {
        return mockCanvas;
      }
      return null;
    });
    
    // Mock Storage module
    window.Storage = {
      getHabits: jest.fn(() => []),
      getTasks: jest.fn(() => []),
      getTransactions: jest.fn(() => []),
      getHealthData: jest.fn(() => ({ weight: [], sleep: [], mood: [] })),
      getTimeEntries: jest.fn(() => []),
      getHabitLogs: jest.fn(() => ({})),
      getTodayString: jest.fn(() => '2026-02-14'),
      getDateString: jest.fn((date) => new Date(date).toISOString().split('T')[0])
    };
  });

  afterEach(() => {
    // Stop any running intervals
    window.Charts.stopRealTimeUpdates();
  });

  describe('startRealTimeUpdates', () => {
    it('should start an update interval', () => {
      // Act
      window.Charts.startRealTimeUpdates();
      
      // Assert
      expect(window.Charts.updateInterval).not.toBeNull();
    });

    it('should not start multiple intervals', () => {
      // Act
      window.Charts.startRealTimeUpdates();
      const firstInterval = window.Charts.updateInterval;
      window.Charts.startRealTimeUpdates();
      
      // Assert
      expect(window.Charts.updateInterval).toBe(firstInterval);
    });

    it('should initialize lastDataState', () => {
      // Act
      window.Charts.startRealTimeUpdates();
      
      // Assert
      expect(window.Charts.lastDataState).not.toBeNull();
    });
  });

  describe('stopRealTimeUpdates', () => {
    it('should stop the update interval', () => {
      // Arrange
      window.Charts.startRealTimeUpdates();
      
      // Act
      window.Charts.stopRealTimeUpdates();
      
      // Assert
      expect(window.Charts.updateInterval).toBeNull();
    });

    it('should handle being called when not running', () => {
      // Act & Assert - should not throw
      expect(() => window.Charts.stopRealTimeUpdates()).not.toThrow();
    });
  });

  describe('getCurrentDataState', () => {
    it('should return a JSON string with data counts', () => {
      // Arrange
      window.Storage.getHabits.mockReturnValue([{ id: 1 }, { id: 2 }]);
      window.Storage.getTasks.mockReturnValue([{ id: 1, completed: true }]);
      
      // Act
      const state = window.Charts.getCurrentDataState();
      
      // Assert
      const parsed = JSON.parse(state);
      expect(parsed.habitsCount).toBe(2);
      expect(parsed.tasksCount).toBe(1);
      expect(parsed.completedTasks).toBe(1);
    });

    it('should handle errors gracefully', () => {
      // Arrange
      window.Storage.getHabits.mockImplementation(() => {
        throw new Error('Test error');
      });
      
      // Act
      const state = window.Charts.getCurrentDataState();
      
      // Assert
      expect(state).toBeNull();
    });
  });

  describe('hasDataChanged', () => {
    it('should return false on first call', () => {
      // Act
      const changed = window.Charts.hasDataChanged();
      
      // Assert
      expect(changed).toBe(false);
    });

    it('should return true when data changes', () => {
      // Arrange
      window.Charts.getCurrentDataState(); // Initialize
      window.Storage.getHabits.mockReturnValue([{ id: 1 }]); // Change data
      
      // Act
      const changed = window.Charts.hasDataChanged();
      
      // Assert
      expect(changed).toBe(true);
    });

    it('should return false when data has not changed', () => {
      // Arrange
      window.Charts.getCurrentDataState(); // Initialize
      
      // Act
      const changed = window.Charts.hasDataChanged();
      
      // Assert
      expect(changed).toBe(false);
    });
  });

  describe('forceUpdate', () => {
    it('should update lastDataState', () => {
      // Arrange
      window.Charts.lastDataState = null;
      
      // Act
      window.Charts.forceUpdate();
      
      // Assert
      expect(window.Charts.lastDataState).not.toBeNull();
    });

    it('should call updateAll', () => {
      // Arrange
      const updateAllSpy = jest.spyOn(window.Charts, 'updateAll');
      
      // Act
      window.Charts.forceUpdate();
      
      // Assert
      expect(updateAllSpy).toHaveBeenCalled();
    });
  });

  describe('initWithRealTime', () => {
    it('should initialize charts and start real-time updates', () => {
      // Act
      window.Charts.initWithRealTime();
      
      // Assert
      expect(window.Charts.updateInterval).not.toBeNull();
    });
  });

  describe('updateAll', () => {
    it('should initialize all charts', () => {
      // Act
      window.Charts.updateAll();
      
      // Assert
      expect(document.getElementById).toHaveBeenCalledWith('weeklyChart');
      expect(document.getElementById).toHaveBeenCalledWith('expensesChart');
      expect(document.getElementById).toHaveBeenCalledWith('weightChart');
      expect(document.getElementById).toHaveBeenCalledWith('sleepChart');
      expect(document.getElementById).toHaveBeenCalledWith('moodChart');
      expect(document.getElementById).toHaveBeenCalledWith('timeChart');
      expect(document.getElementById).toHaveBeenCalledWith('financialTrendsChart');
    });
  });

  describe('destroyAll', () => {
    it('should destroy all chart instances', () => {
      // Arrange
      window.Charts.instances = {
        weekly: mockChart,
        expenses: mockChart
      };
      
      // Act
      window.Charts.destroyAll();
      
      // Assert
      expect(mockChart.destroy).toHaveBeenCalledTimes(2);
      expect(window.Charts.instances).toEqual({});
    });
  });
});