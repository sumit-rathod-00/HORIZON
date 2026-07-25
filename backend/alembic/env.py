"""
Alembic environment configuration for SQLAlchemy 2.x Async.

This file configures Alembic to run migrations using an async SQLAlchemy
engine, sourcing the database URL from the application's settings object
and the target metadata from the application's declarative Base.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Application imports
# ---------------------------------------------------------------------------
# Import the application settings (holds DATABASE_URL) and the declarative
# Base (holds metadata for all ORM models) so Alembic can autogenerate
# migrations correctly.
from app.core.config import settings
from app.db.base import Base

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
# This gives access to the values within the .ini file in use.
config = context.config

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Inject the application's DATABASE_URL into Alembic's config
# ---------------------------------------------------------------------------
# We override the sqlalchemy.url value from alembic.ini with the URL coming
# from our application settings, ensuring a single source of truth for the
# database connection string. This URL must be an async-compatible DSN,
# e.g. "postgresql+asyncpg://user:password@host:port/dbname".
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%")
)

# ---------------------------------------------------------------------------
# Target metadata
# ---------------------------------------------------------------------------
# This is used by 'autogenerate' support to compare the models' metadata
# against the current state of the database. All models must be imported
# somewhere so their tables are registered on Base.metadata before this
# point (typically via app.db.base importing all model modules).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Compare column types when autogenerating migrations.
        compare_type=True,
        # Detect changes to server defaults when autogenerating migrations.
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Configure the migration context with a live synchronous connection
    (provided via run_sync from the async engine) and run migrations.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an async Engine and associate a connection with the context.

    This is the async equivalent of the standard 'run_migrations_online'
    flow. We build the engine from the Alembic config section, connect
    asynchronously, then delegate the actual synchronous-style migration
    logic to `do_run_migrations` via `run_sync`.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    # Dispose of the engine's connection pool cleanly.
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Entry point used by Alembic for online migrations. Since Alembic's
    core migration runner is synchronous, we bridge to it by running our
    async migration coroutine to completion with asyncio.run().
    """
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()