"""
Connection abstraction so the same code runs against SQLite locally
(zero setup) and Postgres in production (Vercel has no persistent
filesystem, so SQLite can't survive there).

Controlled by the DATABASE_URL environment variable: set it (a
Postgres connection string) in production; leave it unset locally
and a SQLite file is used instead.
"""
import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    import psycopg2


def get_connection(sqlite_path: str = "telemetry_grid.db"):
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(sqlite_path, check_same_thread=False)


def adapt_query(query: str) -> str:
    """We write queries using SQLite's `?` placeholder style everywhere;
    translate to Postgres's `%s` style when running against Postgres."""
    return query.replace("?", "%s") if IS_POSTGRES else query
