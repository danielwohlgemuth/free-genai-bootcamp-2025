import asyncio
from contextlib import asynccontextmanager
from db import get_db, engine, Base
from invoke import task
from pathlib import Path
from sqlalchemy.sql import text


@asynccontextmanager
async def get_db_context():
    """Context manager for database connection"""
    async for db in get_db():
        try:
            yield db
        finally:
            break

async def _setup():
    """Run database migrations"""
    print("Running migrations...")
    migrations_dir = Path('db/migrations')

    async with get_db_context() as db:
        try:
            # Drop all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            # Run migrations
            for migration_file in sorted(migrations_dir.glob('*.sql')):
                print(f"Running migration: {migration_file}")
                with open(migration_file) as f:
                    sql = f.read()
                await db.execute(text(sql))

            await db.commit()
        except Exception as e:
            print(f"Failed to run migrations: {e}")
            raise

@task
def setup(ctx):
    """Run all setup tasks in sequence"""
    asyncio.run(_setup())

@task
def dev(ctx):
    """Run the development server with auto-reload"""
    ctx.run("uvicorn main:app --reload")