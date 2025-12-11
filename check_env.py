#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add project root to path for decouple to work
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from decouple import config 
    import smtplib
    import ssl
    print("Dependencies loaded successfully.")
except ImportError as e:
    print(f"Error loading dependencies. Ensure 'python-decouple', 'smtplib', and 'ssl' are installed. Error: {e}")
    sys.exit(1)


print("\n🔍 Checking Email Configuration from .env...")
print("=" * 60)

# Configuration must be read here, NOT from settings.py
try:
    host = config('EMAIL_HOST', default='smtp.gmail.com')
    port = config('EMAIL_PORT', cast=int, default=465)
    username = config('EMAIL_HOST_USER')
    password = config('EMAIL_HOST_PASSWORD')
    use_ssl = config('EMAIL_USE_SSL', cast=bool, default=True)

    print(f"EMAIL_HOST:         {host}")
    print(f"EMAIL_PORT:         {port}")
    print(f"EMAIL_HOST_USER:    {username}")
    print(f"EMAIL_HOST_PASSWORD: {'✅ SET (hidden)' if password else '❌ NOT SET'}")
    print(f"EMAIL_USE_SSL:      {use_ssl}")
except Exception as e:
    print(f"❌ Error reading .env configuration: {e}")
    sys.exit(1)

print("=" * 60)

# Test connection
if username and password:
    print(f"\n🔗 Testing connection to {host}:{port} using SSL...")
    try:
        context = ssl.create_default_context()
        
        # Use a timeout shorter than the worker timeout
        server = smtplib.SMTP_SSL(host, port, context=context, timeout=25) 
        print("✅ Connected to SMTP server.")
        
        server.login(username, password)
        print("✅ Authentication successful! The connection issue is resolved.")
        
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed: Invalid username or App Password.")
        print("ACTION: Ensure App Password is correct and has NO SPACES.")
    except smtplib.SMTPConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("ACTION: Google may be blocking the connection, or firewall rules are active.")
    except Exception as e:
        print(f"❌ General SMTP Error: {e}")
        
else:
    print("❌ Cannot test: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set.")

print("\n✅ Environment check completed.")