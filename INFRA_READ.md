# infrastructure reading order

a beginner's guide to the infrastructure codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- `.gitignore`: keeps os, ide, auto-generated, tooling, local data and secrets files out of version control.
- `backend/.dockerignore`: same idea as `.gitignore` for the backend build context, `app.db` and `.env` stay out.
- `frontend/.dockerignore`: same for the frontend build context, `dist` and `node_modules` stay out.
- `.env.example`: env vars docker compose reads from `.env`, copy it and edit, see `README.md`.
- `frontend/nginx.conf`: serves the built vue app, proxies `/api/` to flask, rate and connection limits, json errors.
- `backend/Dockerfile`: multi-stage build: base, test (ruff, pytest) and runtime, runs as a non root user.
- `frontend/Dockerfile`: multi-stage build: base, test (eslint, prettier, vitest), build and nginx runtime.
- `docker-compose.yml`: exposes nginx on port 80, flask stays internal, named sqlite volume, limits, log rotation.
- `docker-compose.cloudflare.yml`: pi-only overlay, drops nginx's host port and joins it to cloudflared's edge-network.
