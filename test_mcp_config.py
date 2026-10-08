"""Test MCP JIRA Configuration"""
import json
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("MCP JIRA CONFIGURATION TEST")
print("=" * 70)

# Load environment variables
load_dotenv()

print("\n[TEST 1] Environment Variables")
print("=" * 70)

jira_base_url = os.getenv("JIRA_BASE_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_api_token = os.getenv("JIRA_API_TOKEN")

if jira_base_url:
    print(f"[SUCCESS] JIRA_BASE_URL: {jira_base_url}")
else:
    print(f"[FAILED] JIRA_BASE_URL: NOT SET")

if jira_email:
    print(f"[SUCCESS] JIRA_EMAIL: {jira_email}")
else:
    print(f"[FAILED] JIRA_EMAIL: NOT SET")

if jira_api_token:
    print(f"[SUCCESS] JIRA_API_TOKEN: {jira_api_token[:30]}...")
else:
    print(f"[FAILED] JIRA_API_TOKEN: NOT SET")

# Check MCP configuration file
print("\n[TEST 2] MCP Configuration File")
print("=" * 70)

mcp_file = Path("mcp.json")
if mcp_file.exists():
    print(f"[SUCCESS] mcp.json found")
    try:
        with open(mcp_file, 'r') as f:
            mcp_config = json.load(f)
        print(f"[SUCCESS] mcp.json is valid JSON")
        print(f"[SUCCESS] Configured servers: {list(mcp_config.get('mcpServers', {}).keys())}")
        
        jira_server = mcp_config.get('mcpServers', {}).get('jira', {})
        print(f"\nJIRA Server Configuration:")
        print(f"  Command: {jira_server.get('command')}")
        print(f"  Args: {jira_server.get('args')}")
        print(f"  Environment variables: {list(jira_server.get('env', {}).keys())}")
    except json.JSONDecodeError as e:
        print(f"[FAILED] mcp.json is NOT valid JSON: {e}")
else:
    print(f"[FAILED] mcp.json NOT found")

# Check Node.js
print("\n[TEST 3] Node.js Installation")
print("=" * 70)

try:
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"[SUCCESS] Node.js installed: {result.stdout.strip()}")
    else:
        print(f"[FAILED] Node.js check failed: {result.stderr}")
except FileNotFoundError:
    print(f"[FAILED] Node.js NOT installed or not in PATH")
except Exception as e:
    print(f"[FAILED] Error checking Node.js: {e}")

try:
    result = subprocess.run(
        ["npm", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"[SUCCESS] npm installed: {result.stdout.strip()}")
    else:
        print(f"[FAILED] npm check failed: {result.stderr}")
except FileNotFoundError:
    print(f"[FAILED] npm NOT installed or not in PATH")
except Exception as e:
    print(f"[FAILED] Error checking npm: {e}")

# Check if MCP JIRA server is available
print("\n[TEST 4] MCP JIRA Server Availability")
print("=" * 70)

print("Note: This test requires internet connection to check npm registry")
print("\nAttempting to check if @modelcontextprotocol/server-jira is available...")

try:
    # Try to run npm search (this may fail without internet)
    result = subprocess.run(
        ["npm", "search", "@modelcontextprotocol/server-jira", "--json"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        try:
            packages = json.loads(result.stdout)
            if packages and len(packages) > 0:
                print(f"[SUCCESS] MCP JIRA server is available on npm")
                print(f"  Package: {packages[0].get('name')}")
                print(f"  Version: {packages[0].get('version')}")
            else:
                print(f"[FAILED] MCP JIRA server NOT found on npm")
        except json.JSONDecodeError:
            print(f"[WARNING] Could not parse npm response (this is normal if npm search is disabled)")
    else:
        print(f"[WARNING] npm search command failed (may require configuration)")
        print(f"  Hint: Run: npm install -g @modelcontextprotocol/server-jira")
except FileNotFoundError:
    print(f"[FAILED] npm NOT found in PATH")
except subprocess.TimeoutExpired:
    print(f"[WARNING] npm search timed out")
except Exception as e:
    print(f"[WARNING] Error checking MCP server: {e}")

# Test JIRA connectivity
print("\n[TEST 5] JIRA API Connectivity")
print("=" * 70)

try:
    import requests
    import base64
    
    print("Testing JIRA API connection...")
    
    # Create basic auth header
    auth_string = f"{jira_email}:{jira_api_token}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    headers = {'Authorization': f'Basic {auth_b64}'}
    
    # Try to connect to JIRA
    test_url = f"{jira_base_url}/rest/api/3/myself"
    print(f"Endpoint: {test_url}")
    
    response = requests.get(test_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print(f"[SUCCESS] JIRA API Authentication: SUCCESS")
        data = response.json()
        print(f"  User: {data.get('displayName', 'Unknown')}")
        print(f"  Email: {data.get('emailAddress', 'Unknown')}")
    elif response.status_code == 401:
        print(f"[FAILED] JIRA API Authentication: FAILED (401)")
        print(f"  Issue: Authentication failed - check token/email")
    elif response.status_code == 404:
        print(f"[FAILED] JIRA API: NOT FOUND (404)")
        print(f"  Issue: Endpoint not available - may need different API version")
    else:
        print(f"[WARNING] JIRA API: Status {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except ImportError:
    print(f"[FAILED] requests library NOT installed")
    print(f"  Install with: pip install requests")
except Exception as e:
    print(f"[FAILED] JIRA connectivity test failed: {e}")

# Summary
print("\n[TEST SUMMARY]")
print("=" * 70)

all_pass = all([
    jira_base_url,
    jira_email,
    jira_api_token,
    mcp_file.exists()
])

if all_pass:
    print("[SUCCESS] Configuration looks good!")
    print("\nNext steps:")
    print("1. Install MCP JIRA server: npm install -g @modelcontextprotocol/server-jira")
    print("2. Configure VS Code or Claude with mcp.json")
    print("3. Test JIRA queries through the MCP interface")
else:
    print("[FAILED] Some configuration checks failed")
    print("\nFix the following issues:")
    if not jira_base_url:
        print("- Set JIRA_BASE_URL in .env")
    if not jira_email:
        print("- Set JIRA_EMAIL in .env")
    if not jira_api_token:
        print("- Set JIRA_API_TOKEN in .env")
    if not mcp_file.exists():
        print("- Ensure mcp.json exists in current directory")

print("\n" + "=" * 70)
