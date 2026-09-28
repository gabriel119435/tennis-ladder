# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version, and dependencies.
    - `run.py`: starts the flask dev server on port 5000.
- **base**: database layer and wiring the application together
    - `db.py`: the single way to open a database session anywhere in the codebase.
    - `models.py`: every database table as a python class.
    - `app/__init__.py`: wires the database, auth, error handling and blueprints into one flask app.
- **domain logic**: the business rules, no flask involved, tested standalone
    - `admin.py`: `create_admin()`, shared by the boot-time seed and `create_admin.py`.
    - `scoring.py`: set and super-tiebreak validity, match winner, points, and the standings tie-break sort.
    - `pairing.py`: the pairing algorithm, picks each round's opponents.
    - `stats.py`: the one domain file that touches the database, computes a ranking's standings and match history.
- **route helpers**: shared utilities used by blueprints
    - `routes/helpers/annotations.py`: `require_admin()`, the decorator used by admin-only routes.
- **routes**: one blueprint per resource
    - `routes/auth.py`: login, logout, session check, admin password change.
    - `routes/players.py`: list, create, and rename players.
    - `routes/rankings.py`: create/list rankings, start and close rounds.
    - `routes/participants.py`: list, add, and remove a ranking's participants.
    - `routes/matches.py`: list a ranking's matches, enter or edit a match result.
    - `routes/standings.py`: computes and returns a ranking's current standings.
- **tests**: lives under `backend/tests/`, mirroring the `app/` structure
    - `tests/conftest.py`: pytest fixtures, the flask test client, seeded players and admins.
    - `tests/test_scoring.py`: scoring rule tests, set/tiebreak validity, match winner, points, tie-break chain.
    - `tests/test_pairing.py`: pairing algorithm tests, window/tiering, construction, repair passes.
    - `tests/test_stats.py`: direct database tests for `compute_history` and `compute_standings`.
    - `tests/test_auth.py`: login, logout, session check, password change tests.
    - `tests/test_players.py`: player creation, renaming, listing, and ownership tests.
    - `tests/test_rankings.py`: ranking, round, and cross-admin ownership tests.
    - `tests/test_participants.py`: participant add/remove/reactivate and cross-admin ownership tests.
    - `tests/test_matches.py`: match endpoint tests, results, ownership, editing locked after close.
    - `tests/test_standings.py`: standings endpoint tests, points, tie order, not-found.
- **dev tools**
    - `create_admin.py`: creates a new admin account directly in the db, run by hand, no in-app route for it.
