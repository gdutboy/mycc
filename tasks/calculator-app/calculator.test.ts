import { describe, it, expect } from 'vitest';
import { Calculator } from './calculator';

describe('Calculator', () => {
  const calc = new Calculator();

  describe('add', () => {
    it('should add two numbers', () => {
      expect(calc.add(2, 3)).toBe(5);
    });

    it('should handle negative numbers', () => {
      expect(calc.add(-1, -2)).toBe(-3);
    });

    it('should handle decimals', () => {
      expect(calc.add(0.1, 0.2)).toBeCloseTo(0.3);
    });
  });

  describe('subtract', () => {
    it('should subtract two numbers', () => {
      expect(calc.subtract(5, 3)).toBe(2);
    });

    it('should handle negative results', () => {
      expect(calc.subtract(2, 5)).toBe(-3);
    });
  });

  describe('multiply', () => {
    it('should multiply two numbers', () => {
      expect(calc.multiply(3, 4)).toBe(12);
    });

    it('should handle zero', () => {
      expect(calc.multiply(5, 0)).toBe(0);
    });
  });

  describe('divide', () => {
    it('should divide two numbers', () => {
      expect(calc.divide(10, 2)).toBe(5);
    });

    it('should throw error when dividing by zero', () => {
      expect(() => calc.divide(10, 0)).toThrow('Cannot divide by zero');
    });
  });
});
