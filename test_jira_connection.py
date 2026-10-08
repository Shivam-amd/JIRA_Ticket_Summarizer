"""Test JIRA Connection"""
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()

JIRA_URL = os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

print("=" * 70)
print("JIRA CONNECTION TEST")
print("=" * 70)
print(f"\nURL: {JIRA_URL}")
print(f"Email: {JIRA_EMAIL}")
print(f"API Token: {JIRA_API_TOKEN[:20]}...")

# Test 1: Direct REST API call
print("\n" + "=" * 70)
print("TEST 1: Direct REST API Call (Basic Auth)")
print("=" * 70)

try:
    url = f"{JIRA_URL}/rest/api/2/serverInfo"
    print(f"Endpoint: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Authentication successful!")
        data = response.json()
        print(f"JIRA Version: {data.get('version', 'N/A')}")
    elif response.status_code == 401:
        print("[FAILED] Authentication failed (401 Unauthorized)")
        print("Possible issues:")
        print("  1. Email address is incorrect")
        print("  2. API token is invalid or expired")
        print("  3. This JIRA instance uses a different auth method")
    else:
        print(f"[FAILED] Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"[ERROR] Connection error: {e}")

# Test 2: Try with different endpoint
print("\n" + "=" * 70)
print("TEST 2: Try Cloud API Endpoint")
print("=" * 70)

try:
    url = f"{JIRA_URL}/rest/api/3/myself"
    print(f"Endpoint: {url}")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Cloud API authentication successful!")
        data = response.json()
        print(f"Account ID: {data.get('accountId', 'N/A')}")
        print(f"Display Name: {data.get('displayName', 'N/A')}")
    else:
        print(f"[FAILED] Status: {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] Connection error: {e}")

# Test 3: Check URL connectivity
print("\n" + "=" * 70)
print("TEST 3: Basic URL Connectivity (No Auth)")
print("=" * 70)

try:
    response = requests.head(JIRA_URL, timeout=10, allow_redirects=True)
    print(f"Status Code: {response.status_code}")
    print(f"[SUCCESS] URL is reachable")
except Exception as e:
    print(f"[ERROR] URL unreachable: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)

print("""
If you see:
  [FAILED] 401 Unauthorized on all tests
    -> Verify API token is correct and not expired
    -> Check if token has proper permissions
    -> Verify email address is exactly correct
    
  [FAILED] 404 Not Found
    -> URL might be incorrect
    -> Endpoint might be at a different path
    
  [SUCCESS] on TEST 2 but [FAILED] on TEST 1
    -> Your JIRA uses Cloud API (v3) not Server API (v2)
    -> Update code to use /rest/api/3/ endpoints

  [ERROR] URL unreachable
    -> Network/firewall issue
    -> JIRA server might be down
    -> VPN connection needed
""")

print("=" * 70)
