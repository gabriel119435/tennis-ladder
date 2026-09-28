# this file is going to be rewritten, edited, changed, nothing here should be taken as final

# grade-tracker frontend reference

read fully once, kept here so future frontend work has a fixed reference without re-reading grade-tracker.

- stack: vue 3 (composition api, `<script setup>` only), vite, vue-router, vue-i18n, vitest. no state library.
- dirs: `src/api/routes/` (one file per backend resource), `src/components/` (shared, `App`-prefixed), `src/composables/`
  (`generic/` app-wide, `<domain>/` feature-specific), `src/directives/`, `src/locales/`, `src/router/`, `src/styles/`
  (itcss layers), `src/utils/` (pure functions), `src/views/` (one subfolder per role, plus shared layouts).
- naming: `.vue` files PascalCase, everything else camelCase, composables prefixed `use*`, css classes kebab-case.
- state: a single `reactive()` object in `store.js` for cross-cutting session state only (user, sessionLoaded,
  locales). no pinia. everything else lives local to the component or composable that needs it.
- routing: one `beforeEach` guard (`navigationGuard`, exported for testing) does role-based redirects via a
  `HOME_URL` map and each route's `meta.allowed_role`. session loads once per app load (`sessionLoaded` flag),
  `getMe()` + a second parallel call resolved together.
- layouts: `BaseLayout` (topbar + `RouterView` + toast, no nav) vs `TabLayout` (same, plus a nav slot of
  `RouterLink` tabs). reused by composition across roles, never duplicated per role.
- api layer: one `request.js` wraps `fetch` (`credentials: include`, json header only when a body is sent,
  every failure normalized to `{error: code}`, auto-redirect to `/login` on a 401 except the login call itself).
  each `api/routes/*.js` file is a flat list of thin exported async functions calling `request(...)`, no classes.
- errors: backend always returns `{error: "some_code"}`. frontend never hardcodes an error string, always
  `translateError(code)` through `backend_errors.*` in the locale files, then toasted or shown inline.
- composables worth reusing as-is: `useLoading` (per-call guard against concurrent submits, drives `:disabled`),
  `useToast` (module-level singleton, any component can toast), `useConfirm` (module-level singleton pendingId,
  first click arms a delete, second click within a timeout confirms it; prefix ids like `'cat-'`/`'sub-'` when one
  confirm instance is shared across multiple lists).
- css: pure itcss, global styles only, `<style scoped>` deliberately never used (conflicts with the cascade).
  everything imported once from `style.css` in strict layer order: settings (design tokens as css custom
  properties, numeric scales not semantic-per-component) -> generic (reset) -> elements (buttons/inputs) ->
  layout (structural classes shared across views) -> components -> views -> overrides (a single mobile
  `@media` file last). one file per component/view under `styles/components/` and `styles/views/`.
- i18n: `vue-i18n` with `legacy: false`, flat per-locale message objects, a custom `missing` handler.
- tests: vitest, colocated `*.test.js` next to the file under test. covers the router guard and pure utils, not
  full component rendering.

# current tasks

build order, in this sequence:

1. frontend: grade-tracker as the base, same dir architecture and layout pattern.
   blue palette instead of brown, same darker-inward and darker-text-than-background rules.
   i18n: reuse vue-i18n exactly as grade-tracker sets it up (legacy: false, flat per-locale message files,
   same missing handler for backend_errors passthrough). locales: pt-br and en-us, pt-br is the default.
   public, 1 tab: StandingsView, rankings search box on top, below the standings list sided by pending games list.
   click a player in StandingsView leads to RoundsView:
   ranking + user dropdowns, a stats banner, pending games, round-by-round match and position history.
   admin, 4 tabs in this order: rankings (create/start/pause), players (create/rename/add/remove),
   matches (input results), standings (StandingsView read only as described before).
   top bar: login button replaces the username when logged out.
2. infra: docker-compose + nginx.
   reverse proxy, rate limiting, static file serving.
3. README.md last.

# future tasks

- FRONT_READ.md / INFRA_READ.md: file-by-file reading-order guides, deferred until each codebase exists.
- `Player.email`: unique, required, with real validation, all at once.
