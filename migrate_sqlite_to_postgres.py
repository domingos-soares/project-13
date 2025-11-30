"""
Migration script to copy data from SQLite to PostgreSQL
"""
import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from database import Base, PersonDB

# SQLite connection
SQLITE_DB = "persons.db"

# PostgreSQL connection
POSTGRES_URL = "postgresql+asyncpg://domingossoares@localhost:5432/persons_db"


async def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Create PostgreSQL engine
    pg_engine = create_async_engine(POSTGRES_URL, echo=True)
    pg_session_maker = async_sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Clean start
        await conn.run_sync(Base.metadata.create_all)
    
    # Read data from SQLite
    print("\nReading data from SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, name, age, email FROM persons")
    rows = cursor.fetchall()
    
    print(f"Found {len(rows)} records in SQLite")
    
    # Insert data into PostgreSQL
    print("\nMigrating data to PostgreSQL...")
    async with pg_session_maker() as session:
        migrated_count = 0
        for row in rows:
            person = PersonDB(
                id=row['id'],
                name=row['name'],
                age=row['age'],
                email=row['email']
            )
            session.add(person)
            migrated_count += 1
            
            # Commit in batches of 50
            if migrated_count % 50 == 0:
                await session.commit()
                print(f"  Migrated {migrated_count} records...")
        
        # Commit remaining records
        await session.commit()
        print(f"\n✅ Successfully migrated {migrated_count} records!")
    
    # Verify migration
    print("\nVerifying migration...")
    async with pg_session_maker() as session:
        result = await session.execute(select(PersonDB))
        pg_count = len(result.scalars().all())
        print(f"PostgreSQL now has {pg_count} records")
    
    sqlite_conn.close()
    await pg_engine.dispose()
    
    print("\n🎉 Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate_data())
