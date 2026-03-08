"""
Verify indexes on user_badge table for performance optimization.

This script checks that the user_badge table has the necessary indexes
for efficient badge unlock queries as specified in Requirement 17.4.

Expected indexes:
1. Index on user_id (for queries filtering by user)
2. Compound index on (user_id, badge_id) via unique constraint
"""

import sys
from sqlalchemy import inspect, text
from app.db.session import SessionLocal
from app.models.models import UserBadge


def verify_user_badge_indexes():
    """Verify that user_badge table has proper indexes."""
    db = SessionLocal()
    
    try:
        # Get table name
        table_name = UserBadge.__tablename__
        
        print(f"Checking indexes on '{table_name}' table...\n")
        
        # Query PostgreSQL system catalog for indexes
        query = text("""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND t.relname = :table_name
            ORDER BY
                i.relname,
                a.attnum;
        """)
        
        result = db.execute(query, {"table_name": table_name})
        
        # Group indexes by name
        indexes = {}
        for row in result:
            index_name = row.index_name
            if index_name not in indexes:
                indexes[index_name] = {
                    "columns": [],
                    "is_unique": row.is_unique,
                    "is_primary": row.is_primary
                }
            indexes[index_name]["columns"].append(row.column_name)
        
        # Display results
        print("Found indexes:")
        print("-" * 80)
        
        for index_name, info in indexes.items():
            index_type = []
            if info["is_primary"]:
                index_type.append("PRIMARY KEY")
            if info["is_unique"]:
                index_type.append("UNIQUE")
            
            type_str = f" ({', '.join(index_type)})" if index_type else ""
            columns_str = ", ".join(info["columns"])
            
            print(f"  {index_name}{type_str}")
            print(f"    Columns: {columns_str}")
            print()
        
        # Verify required indexes
        print("\nVerification:")
        print("-" * 80)
        
        # Check for user_id index
        has_user_id_index = any(
            "user_id" in info["columns"] and len(info["columns"]) == 1
            for name, info in indexes.items()
            if not info["is_primary"]
        )
        
        # Check for compound (user_id, badge_id) index
        has_compound_index = any(
            info["columns"] == ["user_id", "badge_id"]
            for info in indexes.values()
        )
        
        print(f"✓ Index on user_id: {'FOUND' if has_user_id_index else 'MISSING'}")
        print(f"✓ Compound index on (user_id, badge_id): {'FOUND' if has_compound_index else 'MISSING'}")
        
        # Performance analysis
        print("\nPerformance Analysis:")
        print("-" * 80)
        
        if has_compound_index:
            print("✓ Compound index on (user_id, badge_id) exists.")
            print("  This index efficiently supports:")
            print("  - Queries filtering by user_id only (leftmost column)")
            print("  - Queries filtering by both user_id AND badge_id")
            
            if has_user_id_index:
                print("\nNote: Separate user_id index exists but may be redundant.")
                print("      The compound index already covers user_id queries.")
        else:
            print("⚠ Compound index on (user_id, badge_id) is MISSING!")
            print("  This index is required for optimal badge unlock query performance.")
        
        # Query pattern analysis
        print("\nQuery Patterns:")
        print("-" * 80)
        print("1. is_badge_unlocked(user_id, badge_id)")
        print("   SELECT * FROM user_badge WHERE user_id = ? AND badge_id = ?")
        print(f"   Index used: {'Compound index' if has_compound_index else 'user_id index + filter'}")
        print()
        print("2. get_user_badges(user_id)")
        print("   SELECT badge_id FROM user_badge WHERE user_id = ?")
        print(f"   Index used: {'Compound index (leftmost)' if has_compound_index else 'user_id index'}")
        print()
        print("3. Badge unlock count")
        print("   SELECT COUNT(*) FROM user_badge WHERE user_id = ?")
        print(f"   Index used: {'Compound index (leftmost)' if has_compound_index else 'user_id index'}")
        
        # Summary
        print("\n" + "=" * 80)
        if has_compound_index:
            print("✓ All required indexes are present for optimal performance!")
            print("  Requirement 17.4 is satisfied.")
            return True
        else:
            print("⚠ Missing required indexes. A migration is needed.")
            return False
            
    except Exception as e:
        print(f"Error verifying indexes: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = verify_user_badge_indexes()
    sys.exit(0 if success else 1)
