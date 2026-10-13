# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version, and dependencies.
    - `.python-version`: pins the python version uv uses.
    - `run.py`: starts the flask dev server on port 5000.
- **base**: database layer and wiring the application together
    - `constants.py`: password and name length rules.
    - `validation.py`: password length check, and a name check that strips, lowercases, rejects empty or too long.
    - `db.py`: the single way to open a database session anywhere in the codebase.
    - `models.py`: every database table as a python class, plus `AuthAdmin`, the detached copy flask-login holds.
    - `__init__.py`: `create_app()`: logging, migrations, default admin, cookie policy, auth, errors, blueprints.
- **domain logic**: the business rules, no flask involved, tested standalone
    - `admin.py`: `create_admin()`, shared by the startup default admin and `create_admin.py`.
    - `scoring.py`: set and super-tiebreak validity, match winner, points, and the standings tie-break sort.
    - `pairing.py`: the pairing algorithm, picks each round's opponents.
    - `stats.py`: computes a ranking's standings and match history from the database.
- **route helpers**: shared utilities used by blueprints
    - `routes/helpers/decorators.py`: `require_admin()`, the decorator used by admin-only routes.
    - `routes/helpers/payload.py`: typed readers for json request fields, 400 on a wrong type.
- **routes**: one blueprint per resource
    - `routes/auth.py`: login, logout, session check.
    - `routes/players.py`: list, create, and rename players.
    - `routes/rankings.py`: create/list rankings, start and close rounds.
    - `routes/participants.py`: list, add, and remove a ranking's participants.
    - `routes/matches.py`: list a ranking's matches, enter or clear a match result.
    - `routes/standings.py`: computes and returns a ranking's current standings.
- **tests**: lives under `backend/tests/`, mirroring the `app/` structure
    - `tests/conftest.py`: fixtures (clients, 2 admins, 4 players, started ranking), db cleanup, request helpers.
    - `tests/test_scoring.py`: scoring rule tests, set/tiebreak validity, match winner, points, tie-break chain.
    - `tests/test_pairing.py`: pairing algorithm tests, window/tiering, construction, repair passes.
    - `tests/test_stats.py`: direct database tests for `compute_history` and `compute_standings`.
    - `tests/test_auth.py`: login, logout, session, cookie, bad input, `create_admin()` tests.
    - `tests/test_players.py`: player creation, renaming, listing, and ownership tests.
    - `tests/test_rankings.py`: ranking, round, and cross-admin ownership tests.
    - `tests/test_participants.py`: participant add/remove/reactivate and cross-admin ownership tests.
    - `tests/test_matches.py`: match endpoint tests, results, ownership, editing locked after close.
    - `tests/test_standings.py`: standings endpoint tests, points, tie order, not-found.
- **dev tools**
    - `create_admin.py`: creates a new admin account directly in the db, run by hand, no in-app route for it.
