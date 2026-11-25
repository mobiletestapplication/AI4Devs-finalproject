import js from '@eslint/js';
import { createNodeResolver, importX } from 'eslint-plugin-import-x';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

// Fronteras del frontend (sección 2.3 del readme, design O4): una feature no importa otra;
// lo común pasa por src/shared/.
const FEATURES = ['cartera', 'rentabilidad', 'estrategias', 'backtesting', 'recomendaciones'];

const zonasPorFeature = FEATURES.map((feature) => ({
  target: `./src/features/${feature}`,
  from: FEATURES.filter((otra) => otra !== feature).map((otra) => `./src/features/${otra}`),
  message: 'Una feature no importa otra: mueve lo común a src/shared/.',
}));

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'node_modules'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.strict],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      // Registrado como "import" para que la regla se llame import/no-restricted-paths.
      import: importX,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    settings: {
      'import-x/resolver-next': [
        createNodeResolver({ extensions: ['.ts', '.tsx', '.js', '.jsx'] }),
      ],
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'import/no-restricted-paths': ['error', { zones: zonasPorFeature }],
    },
  },
);
