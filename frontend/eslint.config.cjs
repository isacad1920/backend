// ESLint Flat Config (ESLint v9) for frontend (React + TS + Vite)
// Explicit globals listed to avoid relying on deprecated env merging.

const js = require('@eslint/js');
const reactPlugin = require('eslint-plugin-react');
const tsParser = require('@typescript-eslint/parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');
const reactRefresh = require('eslint-plugin-react-refresh');

/** Shared rules composition */
const reactHooks = require('eslint-plugin-react-hooks');

const baseRules = {
  ...js.configs.recommended.rules,
  ...tsPlugin.configs.recommended.rules,
  ...reactPlugin.configs.recommended.rules,
  ...reactHooks.configs.recommended.rules,
  'react/react-in-jsx-scope': 'off',
  'react/prop-types': 'off'
};

/** Browser + Node globals actually used in code */
const fullStackGlobals = {
  window: 'readonly',
  document: 'readonly',
  navigator: 'readonly',
  localStorage: 'readonly',
  sessionStorage: 'readonly',
  fetch: 'readonly',
  URLSearchParams: 'readonly',
  AbortController: 'readonly',
  console: 'readonly',
  process: 'readonly',
  setTimeout: 'readonly',
  clearTimeout: 'readonly',
  setInterval: 'readonly',
  clearInterval: 'readonly'
};

/** Node-only script globals */
const nodeScriptGlobals = {
  module: 'readonly',
  require: 'readonly',
  __dirname: 'readonly',
  process: 'readonly',
  console: 'readonly'
};

module.exports = [
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    ignores: ['dist/**', 'node_modules/**'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { ecmaVersion: 2022, sourceType: 'module' },
      globals: fullStackGlobals
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      react: reactPlugin,
      'react-refresh': reactRefresh,
      'react-hooks': reactHooks
    },
    linterOptions: { reportUnusedDisableDirectives: true },
    rules: { 
      ...baseRules,
      // TypeScript handles undefined variables, prevent false positives for DOM lib types
      'no-undef': 'off',
      // Phased strictness: reduce noise, we'll migrate away from any gradually
      '@typescript-eslint/no-explicit-any': ['warn', { ignoreRestArgs: true }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      // Encourage safer hooks usage (already included via recommended, but can elevate specifics later)
      'react-hooks/exhaustive-deps': 'warn'
    },
    settings: { react: { version: 'detect' } }
  },
  {
    files: ['scripts/**/*.{js,ts}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { ecmaVersion: 2022, sourceType: 'module' },
      globals: nodeScriptGlobals
    },
    rules: {
      ...baseRules,
      'no-console': 'off',
      '@typescript-eslint/no-var-requires': 'off',
      '@typescript-eslint/no-explicit-any': ['warn', { ignoreRestArgs: true }]
    }
  }
];