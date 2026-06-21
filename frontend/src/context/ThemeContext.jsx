/**
 * ThemeContext — global light/dark mode management
 * Persists user preference to localStorage as 'elevate_theme'.
 * Applies a `data-theme` attribute on <body> so CSS variables work globally.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext({ theme: 'dark', toggleTheme: () => {} });

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('elevate_theme') || 'dark';
    } catch {
      return 'dark';
    }
  });

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('elevate_theme', theme);
    } catch { /* ignore quota errors */ }
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext);
