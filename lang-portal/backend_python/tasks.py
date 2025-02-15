from invoke import task
import sqlite3
from pathlib import Path
import asyncio
from internal.models.base import get_db
from internal.handlers.system import full_reset

@task
def init_db(ctx):
    """Initialize the SQLite database"""
    print("Initializing database...")
    sqlite3.connect('words.db').close()

@task(init_db)
def run_migrations(ctx):
    """Run database migrations"""
    print("Running migrations...")
    conn = sqlite3.connect('words.db')
    migrations_dir = Path('db/migrations')
    
    for migration_file in sorted(migrations_dir.glob('*.sql')):
        print(f"Running migration: {migration_file}")
        with open(migration_file) as f:
            conn.executescript(f.read())
    
    conn.close()

@task(run_migrations)
def seed_data(ctx):
    """Seed the database with initial data"""
    print("Seeding database...")
    async def run_reset():
        async for db in get_db():
            await full_reset(db)
            break
    
    asyncio.run(run_reset())

@task(seed_data)
def setup(ctx):
    """Run all setup tasks in sequence"""
    print("Setup complete!") 