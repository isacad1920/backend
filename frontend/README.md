# SOFinance Frontend

Vite + React + TypeScript frontend for the SOFinance backend.

## Features
- React 18 + TypeScript
- TailwindCSS
- Radix UI primitives & Lucide icons
- Modular service layer (see `services/`)
- Environment config via `config/index.ts`

## Getting Started

```bash
cd frontend
npm install
npm run dev
```
Dev server: http://localhost:5173 (API proxied to http://localhost:8000)

## Build
```bash
npm run build
npm run preview
```

## Lint & Type Check
```bash
npm run lint
npm run typecheck
```

## Regenerating Full API Docs
Backend: `python scripts/generate_full_api_reference.py`

## Next Improvements
- Add React Router for URL-based navigation
- Introduce query caching (React Query / TanStack Query)
- Add authentication refresh flow in interceptor
- Extract design tokens from Tailwind config
- Add unit tests (Vitest + Testing Library)
