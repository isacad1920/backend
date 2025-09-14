import '@testing-library/jest-dom';

// Global test setup (e.g., mock matchMedia if needed)
if (typeof window !== 'undefined' && !window.matchMedia) {
  // rudimentary matchMedia mock
  // @ts-ignore
  window.matchMedia = () => ({ matches: false, addEventListener: () => {}, removeEventListener: () => {} });
}
