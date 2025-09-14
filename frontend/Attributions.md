# Attributions

This project incorporates third-party software and assets. Below is a list of notable libraries, UI primitives, icons, and media along with their respective licenses.

## Design & UI Component Sources
- [shadcn/ui](https://ui.shadcn.com/) – MIT License (component patterns & styling primitives)
- [Radix UI Primitives](https://www.radix-ui.com/primitives) – MIT License (accessible unstyled components)
- [Lucide Icons](https://lucide.dev/) – ISC License (icon set)

## Frontend Framework & Tooling
- [React](https://react.dev/) – MIT License
- [Vite](https://vitejs.dev/) – MIT License
- [TypeScript](https://www.typescriptlang.org/) – Apache 2.0 License
- [Tailwind CSS](https://tailwindcss.com/) – MIT License
- [PostCSS](https://postcss.org/) – MIT License
- [Autoprefixer](https://github.com/postcss/autoprefixer) – MIT License

## Styling & Utilities
- [class-variance-authority](https://github.com/joe-bell/cva) – MIT License
- [tailwind-merge](https://github.com/dcastil/tailwind-merge) – MIT License

## Icons & Media
- [Lucide](https://lucide.dev/) – ISC License
- Photos from [Unsplash](https://unsplash.com) – [Unsplash License](https://unsplash.com/license)

## Backend & Integration (Referenced by Frontend)
- SOFinance Backend (FastAPI + Prisma) – Internal project (see repository license)

## Authentication & Security Patterns
- OAuth2 / JWT implementation patterns informed by FastAPI documentation (FastAPI – MIT License)

## How to Regenerate This List
Run `npm ls --json > deps.json` (after installing dependencies) and map the top-level packages to their repository/license metadata (manual curation recommended for clarity).

## Notices
All third-party libraries retain their original licenses. Components adapted or composed from shadcn/ui remain under MIT. Icon usage must retain attribution if required by upstream (Lucide does not require but attribution is appreciated).

---
Original credits:

> This Figma Make file includes components from [shadcn/ui](https://ui.shadcn.com/) used under [MIT license](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md).
>
> This Figma Make file includes photos from [Unsplash](https://unsplash.com) used under [license](https://unsplash.com/license).