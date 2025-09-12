import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from app.core.config import settings
from app.core.db import Base

# 🚀 Import all models so Alembic sees them
from app import models

# Alembic Config object
config = context.config
fileConfig(config.config_file_name)

# Database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(connection=conn, target_metadata=target_metadata)
        )
        async with connection.begin():
            await connection.run_sync(lambda conn: context.run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
