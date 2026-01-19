#!/usr/bin/env python3
"""
CreditX Database Migration Runner
Applies SQL migrations to PostgreSQL in order
"""
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

import asyncpg

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def get_connection():
    """Get database connection from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable required")
    return await asyncpg.connect(database_url)


async def ensure_migrations_table(conn):
    """Create migrations tracking table if not exists."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)


async def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    rows = await conn.fetch("SELECT filename FROM _migrations ORDER BY filename")
    return {row['filename'] for row in rows}


async def apply_migration(conn, filepath: Path):
    """Apply a single migration file."""
    sql = filepath.read_text()
    filename = filepath.name
    
    print(f"  Applying {filename}...")
    
    try:
        await conn.execute(sql)
        await conn.execute(
            "INSERT INTO _migrations (filename) VALUES ($1)",
            filename
        )
        print(f"  ✓ {filename} applied successfully")
        return True
    except Exception as e:
        print(f"  ✗ {filename} failed: {e}")
        return False


async def run_migrations():
    """Run all pending migrations."""
    print("=" * 60)
    print("CreditX Database Migration Runner")
    print("=" * 60)
    
    conn = await get_connection()
    
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        
        # Get migration files in order
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        
        if not migration_files:
            print("No migration files found in", MIGRATIONS_DIR)
            return
        
        pending = [f for f in migration_files if f.name not in applied]
        
        if not pending:
            print("✓ All migrations already applied")
            return
        
        print(f"\nFound {len(pending)} pending migration(s):\n")
        
        for filepath in pending:
            success = await apply_migration(conn, filepath)
            if not success:
                print("\n✗ Migration failed. Stopping.")
                sys.exit(1)
        
        print("\n" + "=" * 60)
        print("✓ All migrations applied successfully")
        print("=" * 60)
        
    finally:
        await conn.close()


async def rollback_last():
    """Rollback the last applied migration (manual SQL required)."""
    conn = await get_connection()
    
    try:
        last = await conn.fetchrow(
            "SELECT filename FROM _migrations ORDER BY applied_at DESC LIMIT 1"
        )
        if last:
            print(f"Last migration: {last['filename']}")
            print("Manual rollback required - review the migration file")
        else:
            print("No migrations to rollback")
    finally:
        await conn.close()


async def status():
    """Show migration status."""
    conn = await get_connection()
    
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        
        print("\nMigration Status:")
        print("-" * 50)
        
        for filepath in migration_files:
            status = "✓ Applied" if filepath.name in applied else "○ Pending"
            print(f"  {status}  {filepath.name}")
        
        print("-" * 50)
        print(f"Total: {len(migration_files)} | Applied: {len(applied)} | Pending: {len(migration_files) - len(applied)}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "migrate"
    
    if command == "migrate":
        asyncio.run(run_migrations())
    elif command == "status":
        asyncio.run(status())
    elif command == "rollback":
        asyncio.run(rollback_last())
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrate.py [migrate|status|rollback]")
        sys.exit(1)
