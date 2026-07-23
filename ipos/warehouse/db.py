"""DuckDB warehouse access: connect, migrate, sync ``dim_series`` from the
registry.

DuckDB is single-writer: the weekly job is the only writer; the report and any
UI open read-only (A1). Migrations are plain numbered SQL files applied in
order and recorded in ``meta`` so ``ipos-init`` re-runs are no-ops.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import duckdb

from ipos.config.load import REPO_ROOT
from ipos.config.models import Registry

DEFAULT_DB_PATH = REPO_ROOT / "data" / "warehouse.duckdb"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def connect(
    db_path: Path | str | None = None, *, read_only: bool = False
) -> duckdb.DuckDBPyConnection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not read_only:
        path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path), read_only=read_only)


def _applied_migrations(con: duckdb.DuckDBPyConnection) -> set[str]:
    exists = con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'meta'"
    ).fetchone()
    if not exists:
        return set()
    rows = con.execute(
        "SELECT value FROM meta WHERE key LIKE 'migration:%'"
    ).fetchall()
    return {r[0] for r in rows}


def apply_migrations(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Apply every not-yet-applied migration in filename order. Returns the
    list of filenames applied this call (empty on a no-op re-run)."""
    applied = _applied_migrations(con)
    files = sorted(MIGRATIONS_DIR.glob("[0-9]*.sql"))
    newly: list[str] = []
    for f in files:
        if f.name in applied:
            continue
        con.execute(f.read_text(encoding="utf-8"))
        con.execute(
            "INSERT OR REPLACE INTO meta(key, value, updated_at) VALUES (?, ?, ?)",
            [f"migration:{f.name}", f.name, datetime.now(timezone.utc)],
        )
        newly.append(f.name)
    # stamp schema version = highest migration number applied so far
    all_migs = sorted(_applied_migrations(con) | set(newly))
    if all_migs:
        con.execute(
            "INSERT OR REPLACE INTO meta(key, value, updated_at) VALUES (?, ?, ?)",
            ["schema_version", all_migs[-1], datetime.now(timezone.utc)],
        )
    return newly


def sync_dim_series(con: duckdb.DuckDBPyConnection, registry: Registry) -> int:
    """Upsert active registry entries into ``dim_series``; disable rows that
    are no longer active (never delete — facts must stay joinable)."""
    active = registry.active()
    active_ids = {e.series_id for e in active}

    for e in active:
        primary = e.sources[0]
        con.execute(
            """
            INSERT OR REPLACE INTO dim_series
              (series_id, name, asset_class, region, frequency, unit,
               source_type, source_locator, higher_is_better, scoring_method,
               module_id, critical, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, now())
            """,
            [
                e.series_id, e.name, e.asset_class, e.region, e.frequency, e.unit,
                primary.type, primary.locator, e.higher_is_better,
                e.scoring_method, e.module_id, e.critical,
            ],
        )

    # disable rows that dropped out of the active set
    existing = {r[0] for r in con.execute("SELECT series_id FROM dim_series").fetchall()}
    for sid in existing - active_ids:
        con.execute("UPDATE dim_series SET enabled = FALSE WHERE series_id = ?", [sid])

    return len(active)


def init_db(
    registry: Registry, db_path: Path | str | None = None
) -> dict:
    """Create/upgrade the DB and sync ``dim_series``. Returns a small report."""
    with connect(db_path) as con:
        newly = apply_migrations(con)
        n = sync_dim_series(con, registry)
        schema_version = con.execute(
            "SELECT value FROM meta WHERE key = 'schema_version'"
        ).fetchone()
    return {
        "migrations_applied": newly,
        "dim_series_synced": n,
        "schema_version": schema_version[0] if schema_version else None,
    }
