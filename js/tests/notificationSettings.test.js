/**
 * Tests for notification settings functionality
 */
describe('Notification Settings', () => {
  const SETTINGS_KEY = 'tracklife_notification_settings';
  
  // Mock localStorage
  const mockLocalStorage = {
    store: {},
    setItem: jest.fn((key, value) => {
      mockLocalStorage.store[key] = value;
    }),
    getItem: jest.fn((key) => mockLocalStorage.store[key] || null),
    removeItem: jest.fn((key) => {
      delete mockLocalStorage.store[key];
    })
  };
  
  // Mock Notification API
  const mockNotification = {
    permission: 'default',
    requestPermission: jest.fn(() => Promise.resolve('granted'))
  };
  
  beforeEach(() => {
    global.localStorage = mockLocalStorage;
    global.Notification = mockNotification;
    mockLocalStorage.store = {};
    mockNotification.permission = 'default';
  });

  describe('getSettings', () => {
    it('should return default settings when no settings are saved', () => {
      // Arrange
      mockLocalStorage.getItem.mockReturnValue(null);
      
      // Act
      const settings = window.Notifications.getSettings();
      
      // Assert
      expect(settings.enabled).toBe(false);
      expect(settings.sound).toBe('default');
      expect(settings.style).toBe('default');
      expect(settings.habitReminders).toBe(true);
      expect(settings.taskReminders).toBe(true);
      expect(settings.goalReminders).toBe(true);
    });

    it('should return saved settings merged with defaults', () => {
      // Arrange
      const savedSettings = { enabled: true, sound: 'chime' };
      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(savedSettings));
      
      // Act
      const settings = window.Notifications.getSettings();
      
      // Assert
      expect(settings.enabled).toBe(true);
      expect(settings.sound).toBe('chime');
      expect(settings.style).toBe('default'); // Should have default value
    });
  });

  describe('saveSettings', () => {
    it('should save settings to localStorage', () => {
      // Arrange
      const settings = { enabled: true, sound: 'bell', style: 'urgent' };
      
      // Act
      const result = window.Notifications.saveSettings(settings);
      
      // Assert
      expect(result).toBe(true);
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        SETTINGS_KEY,
        expect.any(String)
      );
    });

    it('should merge new settings with existing settings', () => {
      // Arrange
      mockLocalStorage.store[SETTINGS_KEY] = JSON.stringify({
        enabled: true,
        sound: 'default',
        style: 'default'
      });
      
      // Act
      window.Notifications.saveSettings({ sound: 'chime' });
      
      // Assert
      const savedCall = mockLocalStorage.setItem.mock.calls[mockLocalStorage.setItem.mock.calls.length - 1];
      const savedSettings = JSON.parse(savedCall[1]);
      expect(savedSettings.enabled).toBe(true); // Should preserve existing
      expect(savedSettings.sound).toBe('chime'); // Should update
    });
  });

  describe('isSupported', () => {
    it('should return true when Notification API is available', () => {
      // Act & Assert
      expect(window.Notifications.isSupported()).toBe(true);
    });

    it('should return false when Notification API is not available', () => {
      // Arrange
      delete global.Notification;
      
      // Act & Assert
      expect(window.Notifications.isSupported()).toBe(false);
      
      // Cleanup
      global.Notification = mockNotification;
    });
  });

  describe('requestPermission', () => {
    it('should return true if permission already granted', async () => {
      // Arrange
      mockNotification.permission = 'granted';
      
      // Act
      const result = await window.Notifications.requestPermission();
      
      // Assert
      expect(result).toBe(true);
    });

    it('should request permission if not yet decided', async () => {
      // Arrange
      mockNotification.permission = 'default';
      
      // Act
      await window.Notifications.requestPermission();
      
      // Assert
      expect(mockNotification.requestPermission).toHaveBeenCalled();
    });

    it('should return false if permission denied', async () => {
      // Arrange
      mockNotification.permission = 'denied';
      
      // Act
      const result = await window.Notifications.requestPermission();
      
      // Assert
      expect(result).toBe(false);
    });
  });

  describe('show', () => {
    it('should not show notification if not enabled in settings', () => {
      // Arrange
      mockLocalStorage.store[SETTINGS_KEY] = JSON.stringify({ enabled: false });
      mockNotification.permission = 'granted';
      
      // Act
      const result = window.Notifications.show('Test', { body: 'Test body' });
      
      // Assert
      expect(result).toBeUndefined();
    });

    it('should show notification if enabled and permitted', () => {
      // Arrange
      mockLocalStorage.store[SETTINGS_KEY] = JSON.stringify({ enabled: true });
      mockNotification.permission = 'granted';
      
      // Mock Notification constructor
      const mockNotificationInstance = { close: jest.fn() };
      global.Notification = jest.fn(() => mockNotificationInstance);
      global.Notification.permission = 'granted';
      
      // Act
      const result = window.Notifications.show('Test Title', { body: 'Test body' });
      
      // Assert
      expect(result).toBe(mockNotificationInstance);
    });
  });
});