// Application Configuration
// Update these values to match your environment

export const config = {
  // Backend API URL - change this to point to your actual backend
  apiUrl: 'http://localhost:8000/api/v1',
  
  // Application settings
  app: {
    name: 'Financial Management System',
    version: '1.0.0',
  },
  
  // API timeouts (in milliseconds)
  api: {
    timeout: 10000, // 10 seconds
    retries: 3,
  },
  
  // Local storage keys
  storage: {
    userKey: 'financialApp_user',
    settingsKey: 'financialApp_settings',
  },
} as const;

export default config;