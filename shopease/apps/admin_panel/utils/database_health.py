"""
========================================
DATABASE HEALTH MONITORING UTILITY
========================================

Utilities for checking database connection status, performance metrics,
and database statistics.
"""

from django.db import connection
import time


def get_db_status():
    """
    Test database connection and return status information.

    Returns:
        dict: Connection status with response time, engine info, etc.
    """
    try:
        start = time.time()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        response_time = (time.time() - start) * 1000  # Convert to milliseconds
        cursor.close()

        return {
            'connected': True,
            'response_time': round(response_time, 2),
            'engine': connection.settings_dict['ENGINE'].split('.')[-1],  # e.g., 'mysql'
            'name': connection.settings_dict['NAME'],
            'host': connection.settings_dict['HOST'],
            'port': connection.settings_dict['PORT'],
        }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
            'engine': connection.settings_dict.get('ENGINE', 'Unknown'),
            'name': connection.settings_dict.get('NAME', 'Unknown'),
        }


def get_db_statistics():
    """
    Get database size and table count statistics (MySQL specific).

    Returns:
        dict: Database statistics including size and table count
    """
    try:
        with connection.cursor() as cursor:
            # Get database size in MB
            cursor.execute("""
                SELECT
                    table_schema as db_name,
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as db_size_mb
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                GROUP BY table_schema
            """)
            db_info = cursor.fetchone()

            # Get table count
            cursor.execute("""
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
            """)
            table_count_result = cursor.fetchone()

            # Get total rows across all tables
            cursor.execute("""
                SELECT SUM(table_rows) as total_rows
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
            """)
            total_rows_result = cursor.fetchone()

            return {
                'db_size_mb': db_info[1] if db_info else 0,
                'table_count': table_count_result[0] if table_count_result else 0,
                'total_rows': total_rows_result[0] if total_rows_result else 0,
            }
    except Exception as e:
        return {
            'db_size_mb': 0,
            'table_count': 0,
            'total_rows': 0,
            'error': str(e),
        }


def test_db_connection():
    """
    Simple connection test that returns boolean.

    Returns:
        bool: True if connected, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except:
        return False
