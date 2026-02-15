/**
 * Tests for timer persistence functionality in Time module
 */
describe('Timer Persistence', () => {
  const TIMER_STATE_KEY = 'tracklife_timer_state';
  
  // Mock localStorage for testing
  const mockLocalStorage = {
    setItem: jest.fn(),
    getItem: jest.fn(),
    removeItem: jest.fn()
  };
  
  beforeEach(() => {
    // Clear real localStorage
    global.localStorage = mockLocalStorage;
    // Reset timer state
    window.Time.timerSeconds = 0;
    window.Time.timerRunning = false;
    window.Time.timerCategory = 'work';
  });

  it('should save timer state correctly', () => {
    // Arrange
    window.Time.timerSeconds = 120;
    window.Time.timerRunning = true;
    window.Time.timerCategory = 'study';
    
    // Act
    window.Time.saveTimerState();
    
    // Assert
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      TIMER_STATE_KEY,
      JSON.stringify({
        seconds: 120,
        running: true,
        category: 'study',
        timestamp: expect.any(Number)
      })
    );
  });

  it('should restore timer state from localStorage', () => {
    // Arrange
    const mockState = {
      seconds: 300,
      running: true,
      category: 'exercise',
      timestamp: Date.now() - 60000 // 1 minute ago
    };
    
    mockLocalStorage.getItem.mockImplementation(key => 
      key === TIMER_STATE_KEY ? JSON.stringify(mockState) : null
    );
    
    // Act
    window.Time.restoreTimerState();
    
    // Assert
    expect(window.Time.timerSeconds).toBe(300);
    expect(window.Time.timerRunning).toBe(true);
    expect(window.Time.timerCategory).toBe('exercise');
  });

  it('should handle missing timer state gracefully', () => {
    // Arrange
    mockLocalStorage.getItem.mockImplementation(key => null);
    
    // Act & Assert
    expect(() => {
      window.Time.restoreTimerState();
    }).not.toThrow();
    
    expect(window.Time.timerSeconds).toBe(0);
    expect(window.Time.timerRunning).toBe(false);
  });
});