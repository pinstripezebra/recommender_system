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
print("=== Environment Variables ===")
print(f"db_instance_identifier: {os.environ.get('db_instance_identifier')}")
print(f"master_username: {os.environ.get('master_username')}")
print(f"password: {'*' * len(os.environ.get('password', '')) if os.environ.get('password') else 'NOT SET'}")
print(f"RDS_ENDPOINT: {os.environ.get('RDS_ENDPOINT')}")
print(f"RDS_PORT: {os.environ.get('RDS_PORT', '5432')}")
print(f"RDS_DATABASE: {os.environ.get('RDS_DATABASE', 'postgres')}")
print("============================")

# Get AWS RDS connection details from environment variables
db_identifier = os.environ.get("db_instance_identifier")
master_username = os.environ.get("master_username")
password = os.environ.get("password")
rds_endpoint = os.environ.get("RDS_ENDPOINT")
rds_port = os.environ.get("RDS_PORT", "5432")
rds_database = os.environ.get("RDS_DATABASE", "postgres")

# Troubleshooting: Check if we can reach the RDS endpoint
import socket

def test_network_connectivity():
    """Test network connectivity to RDS endpoint"""
    print("\n=== Network Connectivity Tests ===")
    
    # 1. Get your current public IP
    try:
        import urllib.request
        with urllib.request.urlopen('https://api.ipify.org', timeout=10) as response:
            current_ip = response.read().decode('utf-8')
        print(f"Your current public IP: {current_ip}")
        print(f"Expected IP in security group: 76.115.67.71")
        if current_ip != "76.115.67.71":
            print("⚠️  WARNING: Your current IP doesn't match the security group rule!")
    except Exception as e:
        print(f"Could not get public IP: {e}")
    
    # 2. Test DNS resolution
    try:
        ip_address = socket.gethostbyname(rds_endpoint)
        print(f"✅ DNS Resolution successful: {rds_endpoint} → {ip_address}")
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # 3. Test port connectivity
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((rds_endpoint, int(rds_port)))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {rds_port} is accessible on {rds_endpoint}")
            return True
        else:
            print(f"❌ Port {rds_port} is NOT accessible on {rds_endpoint}")
            print("   This suggests a security group or network ACL issue")
            return False
    except Exception as e:
        print(f"❌ Port connectivity test failed: {e}")
        return False

# Run connectivity tests
network_ok = test_network_connectivity()

if not network_ok:
    print("\n🔍 TROUBLESHOOTING STEPS:")
    print("1. Verify your current IP matches the security group rule")
    print("2. Check RDS security group allows inbound on port 5432")
    print("3. Verify RDS is in a public subnet (if connecting from internet)")
    print("4. Check VPC route tables and NACLs")
    print("5. Ensure RDS instance is in 'Available' state")
    sys.exit(1)

print("\n=== Attempting Database Connection ===")

# Construct database URL for AWS RDS
try:
    conn = psycopg2.connect(
            host=rds_endpoint,
            database=rds_database,
            user=master_username,
            password=password,
            port=rds_port,
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
    print("✅ Database connection successful!")
    
except psycopg2.OperationalError as e:
    print(f"❌ Database connection failed: {e}")
    if "timeout" in str(e).lower():
        print("\n🔍 TIMEOUT TROUBLESHOOTING:")
        print("- Check if your IP address has changed")
        print("- Verify security group allows your current IP")
        print("- Check if RDS is publicly accessible")
        print("- Verify subnet route tables")
    elif "authentication" in str(e).lower():
        print("\n🔍 AUTHENTICATION TROUBLESHOOTING:")
        print("- Verify username and password are correct")
        print("- Check if master username is correct")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

# If we get here, connection was successful, so exit the test
print("\n✅ All tests passed! RDS connection is working.")