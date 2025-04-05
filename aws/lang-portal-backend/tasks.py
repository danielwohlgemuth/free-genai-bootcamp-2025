import asyncio
from handlers.system import full_reset
from db import get_db, engine, Base
from invoke import task
from pathlib import Path
from sqlalchemy.sql import text
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_db_context():
    """Context manager for database connection"""
    async for db in get_db():
        try:
            yield db
        finally:
            break

async def _run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    migrations_dir = Path('db/migrations')
    
    async with get_db_context() as db:
        for migration_file in sorted(migrations_dir.glob('*.sql')):
            print(f"Running migration: {migration_file}")
            with open(migration_file) as f:
                sql = f.read()
                await db.execute(text(sql))
        await db.commit()

@task
def run_migrations(ctx):
    """Run database migrations"""
    asyncio.run(_run_migrations())

async def _seed_data():
    """Seed the database with initial data"""
    print("Seeding database...")
    async with get_db_context() as db:
        await full_reset(db)

@task(run_migrations)
def seed_data(ctx):
    """Seed the database with initial data"""
    asyncio.run(_seed_data())

async def _setup():
    """Run all setup tasks in sequence"""
    print("Setup complete!")

@task(seed_data)
def setup(ctx):
    """Run all setup tasks in sequence"""
    asyncio.run(_setup())

@task
def run_server(ctx):
    """Run the production server"""
    ctx.run("python main.py")

@task
def dev_server(ctx):
    """Run the development server with auto-reload"""
    ctx.run("uvicorn main:app --reload")