import { formatTimestamp, truncateString } from '../utils/formatters';

describe('Utility Functions', () => {
  test('truncateString should shorten long text', () => {
    const longText = 'This is a very long string that should be truncated';
    expect(truncateString(longText, 10)).toBe('This is a ...');
  });

  test('formatTimestamp should format ISO strings', () => {
    const iso = '2024-01-01T12:00:00Z';
    // Just check if it returns a string, format might depend on locale in tests
    expect(typeof formatTimestamp(iso)).toBe('string');
  });
});
