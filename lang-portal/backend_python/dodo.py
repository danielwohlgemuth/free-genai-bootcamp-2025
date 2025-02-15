from doit.tools import run_once
import json
import sqlite3
from pathlib import Path
import asyncio
from internal.models.base import get_db
from internal.handlers.system import full_reset

DOIT_CONFIG = {'default_tasks': ['init_db']}

def task_init_db():
    """Initialize the SQLite database"""
    return {
        'actions': [
            'sqlite3 words.db ".databases"',
        ],
        'targets': ['words.db'],
        'uptodate': [run_once]
    }

def task_run_migrations():
    """Run database migrations"""
    def run_migrations():
        conn = sqlite3.connect('words.db')
        migrations_dir = Path('db/migrations')
        
        for migration_file in sorted(migrations_dir.glob('*.sql')):
            with open(migration_file) as f:
                conn.executescript(f.read())
        
        conn.close()
    
    return {
        'actions': [run_migrations],
        'file_dep': ['words.db'],
        'task_dep': ['init_db']
    }

def task_seed_data():
    """Seed the database with initial data"""
    def seed_database():
        async def run_reset():
            async for db in get_db():
                await full_reset(db)
                break  # We only need to run once
        
        asyncio.run(run_reset())
    
    return {
        'actions': [seed_database],
        'task_dep': ['run_migrations']
    }