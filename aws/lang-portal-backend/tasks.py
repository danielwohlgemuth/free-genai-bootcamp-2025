import asyncio
import sqlite3
from handlers.system import full_reset
from db import get_db
from invoke import task
from pathlib import Path

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

@task
def run_server(ctx):
    """Run the production server"""
    ctx.run("python main.py")

@task
def dev_server(ctx):
    """Run the development server with auto-reload"""
    ctx.run("uvicorn main:app --reload") 