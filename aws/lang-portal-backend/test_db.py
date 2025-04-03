import asyncio
from db import get_db, engine
from sqlalchemy.sql import text

async def test_connection():
    print("Testing database connection...")
    try:
        async for db in get_db():
            print("Successfully connected to the database!")
            # Test a simple query
            result = await db.execute(text("SELECT 1"))
            print("Test query successful!")
            break
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())