// Owns every `enforcement: lint` rule in rules/typescript.md, react.md and
// next.md. Run with --max-warnings=0: a warning that never fails CI is noise.
import js from '@eslint/js'
import nextVitals from 'eslint-config-next/core-web-vitals'
import { defineConfig, globalIgnores } from 'eslint/config'
import tseslint from 'typescript-eslint'

export default defineConfig([
  globalIgnores(['**/.next/**', '**/dist/**', '**/coverage/**', '**/next-env.d.ts']),
  js.configs.recommended,
  ...nextVitals,
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    settings: {
      'jsx-a11y': { components: { Button: 'button', Input: 'input', Textarea: 'textarea', Link: 'a' } },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      '@typescript-eslint/switch-exhaustiveness-check': ['error', { considerDefaultExhaustiveForUnions: true }],
      'jsx-a11y/control-has-associated-label': 'error',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/anchor-has-content': 'error',
      '@next/next/no-html-link-for-pages': 'off',
      'no-restricted-imports': ['error', {
        patterns: [{ group: ['@*/*/src/**'], message: 'Import through the package exports map (pkg-exports-map).' }],
      }],
      'no-restricted-syntax': ['error', {
        selector: "JSXOpeningElement[name.name='a'] > JSXAttribute[name.name='href'][value.value=/^\\//]",
        message: 'Use the router Link for internal navigation (lint-router-link).',
      }],
    },
  },
  {
    files: ['**/*.{js,mjs,cjs}'],
    extends: [tseslint.configs.disableTypeChecked],
  },
])
