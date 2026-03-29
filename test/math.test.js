import { multiply } from '../src/math.js';
import { strict as assert } from 'assert';

describe('multiply', () => {
  it('should multiply two positive numbers', () => {
    assert.equal(multiply(2, 3), 6);
  });

  it('should return 0 when multiplying by 0', () => {
    assert.equal(multiply(0, 5), 0);
    assert.equal(multiply(5, 0), 0);
    assert.equal(multiply(0, 0), 0);
  });

  it('should handle negative numbers', () => {
    assert.equal(multiply(-2, 3), -6);
    assert.equal(multiply(2, -3), -6);
    assert.equal(multiply(-2, -3), 6);
  });

  it('should handle range 0-100', () => {
    assert.equal(multiply(0, 100), 0);
    assert.equal(multiply(100, 0), 0);
    assert.equal(multiply(50, 2), 100);
    assert.equal(multiply(10, 10), 100);
  });
});
