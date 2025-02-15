from doit.tools import run_once
import os
import json
import sqlite3
from pathlib import Path

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
        conn = sqlite3.connect('words.db')
        seeds_dir = Path('db/seeds')
        
        for seed_file in seeds_dir.glob('*.json'):
            with open(seed_file) as f:
                data = json.load(f)
                # Implementation depends on your seed file structure
                # Add logic here to insert data into appropriate tables
        
        conn.close()
    
    return {
        'actions': [seed_database],
        'task_dep': ['run_migrations']
    } 