/**
 * Purpose: Configure the SPFx project's flat ESLint profile and TypeScript project parsing.
 * Key Input Dependencies: @microsoft/eslint-config-spfx and the project's tsconfig.json.
 * Key Functions: spfxProfile; module.exports.
 */
const spfxProfile = require('@microsoft/eslint-config-spfx/lib/flat-profiles/default');

module.exports = [
  ...spfxProfile,
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parserOptions: {
        tsconfigRootDir: __dirname,
        project: './tsconfig.json'
      }
    }
  }
];
