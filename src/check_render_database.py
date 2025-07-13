from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from utils.db_handler import DatabaseHandler
import pandas as pd
import uuid
import sys
from sqlalchemy.exc import OperationalError
import psycopg2

# Load environment variables from .env file (override=True reloads changed values)
load_dotenv(override=True)

# Debug: Print loaded environment variables
database_url = os.environ.get("External_Database_Url")

if not database_url:
    print("❌ External_Database_Url not found in environment variables")
    print("Please check your .env file contains: External_Database_Url=your_render_postgres_url")
    sys.exit(1)

print(f"Database URL loaded: {database_url[:50]}...")

# Parse the database URL to extract components for testing
from urllib.parse import urlparse
import socket

def parse_database_url(url):
    """Parse database URL to extract connection components"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'username': parsed.username,
        'password': parsed.password
    }

db_params = parse_database_url(database_url)

def test_network_connectivity():
    """Test network connectivity to Render PostgreSQL endpoint"""
    print("\n=== Network Connectivity Tests ===")

    # 1. Test DNS resolution
    try:
        ip_address = socket.gethostbyname(db_params['host'])
        print(f"✅ DNS Resolution successful: {db_params['host']} → {ip_address}")
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # 2. Test port connectivity
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((db_params['host'], int(db_params['port'])))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {db_params['port']} is accessible on {db_params['host']}")
            return True
        else:
            print(f"❌ Port {db_params['port']} is NOT accessible on {db_params['host']}")
            print("   This might indicate a network connectivity issue")
            return False
    except Exception as e:
        print(f"❌ Port connectivity test failed: {e}")
        return False

# Run connectivity tests
network_ok = test_network_connectivity()

if not network_ok:
    print("\n🔍 TROUBLESHOOTING STEPS:")
    print("1. Check your internet connection")
    print("2. Verify the Render PostgreSQL URL is correct")
    print("3. Ensure your Render PostgreSQL instance is active")
    print("4. Check if there are any Render service outages")
    sys.exit(1)

print("\n=== Attempting Database Connection ===")

# connect to the database using psycopg2
try:
    conn = psycopg2.connect(
            host=db_params['host'],
            database=db_params['database'],
            user=db_params['username'],
            password=db_params['password'],
            port=db_params['port'],
            connect_timeout=30  # 30 second timeout
        )
    
    # If the connection is successful, you can perform database operations
    cursor = conn.cursor()
    
    # Example: Execute a simple query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ PostgreSQL Database Version: {db_version[0]}")
    
    # Test creating a simple table to verify permissions
    cursor.execute("CREATE TABLE IF NOT EXISTS connection_test (id SERIAL PRIMARY KEY, test_time TIMESTAMP DEFAULT NOW());")
    conn.commit()
    print("✅ Database permissions verified - can create tables")
    
    cursor.close()
    conn.close()
    print("✅ psycopg2 connection successful!")
    
except psycopg2.OperationalError as e:
    print(f"❌ Database connection failed: {e}")
    if "timeout" in str(e).lower():
        print("\n🔍 TIMEOUT TROUBLESHOOTING:")
        print("- Check your internet connection")
        print("- Verify the Render PostgreSQL URL is correct")
        print("- Check if Render service is experiencing issues")
    elif "authentication" in str(e).lower():
        print("\n🔍 AUTHENTICATION TROUBLESHOOTING:")
        print("- Verify the database URL contains correct credentials")
        print("- Check if your Render PostgreSQL service is active")
        print("- Ensure the database URL hasn't expired or changed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

# If we get here, connection was successful, so exit the test
print(f"\n✅ All tests passed! Render PostgreSQL connection is working.")
print(f"✅ Connected to database: {db_params['database']} on {db_params['host']}")
print("✅ Ready for use in your application!")