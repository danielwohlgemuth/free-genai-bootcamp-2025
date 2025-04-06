import asyncio
from contextlib import asynccontextmanager
from db import get_db, engine, Base
from invoke import task
from pathlib import Path
from sqlalchemy.sql import text
import psycopg
import os
import dotenv


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
            await db.execute(text("DROP SCHEMA public CASCADE;"))
            await db.execute(text("CREATE SCHEMA public;"))
            await db.commit()

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

@task
def create_db(ctx):
    """Create the database specified in DB_NAME environment variable"""
    # Get database connection details from environment
    dotenv.load_dotenv()
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'user')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_name = os.getenv('DB_NAME', 'dbname')

    try:
        # Connect to default postgres database
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create the database
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully")

        # Create the schema
        cursor.execute(f"""
            CREATE SCHEMA IF NOT EXISTS public;
            GRANT ALL ON SCHEMA public TO {db_user};
        """)
        print(f"Schema 'public' created successfully")

    except psycopg.Error as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()