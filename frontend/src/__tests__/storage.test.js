/**
 * BUG-C2: Frontend unit tests — storage utilities
 * Tests the core localStorage wrapper in utils/storage.js
 *
 * Run: npm run test:unit
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { setToStorage, getFromStorage, StorageKeys } from '../utils/storage';

describe('storage utilities', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('setToStorage / getFromStorage', () => {
    it('stores and retrieves a plain string', () => {
      setToStorage(StorageKeys.TOKEN, 'abc123');
      expect(getFromStorage(StorageKeys.TOKEN)).toBe('abc123');
    });

    it('stores and retrieves a JSON-serialisable object', () => {
      const profile = { name: 'Alice', age: 28 };
      setToStorage('user_profile', profile);
      expect(getFromStorage('user_profile')).toEqual(profile);
    });

    it('returns null for a key that has never been set', () => {
      expect(getFromStorage('nonexistent_key')).toBeNull();
    });

    it('overwrites an existing value', () => {
      setToStorage(StorageKeys.TOKEN, 'first');
      setToStorage(StorageKeys.TOKEN, 'second');
      expect(getFromStorage(StorageKeys.TOKEN)).toBe('second');
    });
  });

  describe('StorageKeys', () => {
    it('exports TOKEN key', () => {
      expect(typeof StorageKeys.TOKEN).toBe('string');
      expect(StorageKeys.TOKEN.length).toBeGreaterThan(0);
    });
  });
});
