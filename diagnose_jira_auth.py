"""Diagnostic tool to test JIRA authentication and API token validity"""
import os
from dotenv import load_dotenv
import requests
from jira import JIRA

load_dotenv()

jira_url = os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_api_token = os.getenv("JIRA_API_TOKEN")

print("=" * 70)
print("JIRA AUTHENTICATION DIAGNOSTIC")
print("=" * 70)

print(f"\nConfiguration:")
print(f"  JIRA URL: {jira_url}")
print(f"  Email: {jira_email}")
print(f"  API Token (last 10 chars): ...{jira_api_token[-10:]}")

# Test 1: Direct HTTP request to JIRA REST API
print("\n" + "=" * 70)
print("TEST 1: Direct HTTP Request to JIRA REST API")
print("=" * 70)

try:
    auth = (jira_email, jira_api_token)
    url = f"{jira_url}/rest/api/3/myself"
    
    print(f"\nTesting endpoint: {url}")
    response = requests.get(url, auth=auth)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Authentication works!")
        print(f"  User: {data.get('displayName', 'Unknown')}")
        print(f"  Email: {data.get('emailAddress', 'Unknown')}")
    elif response.status_code == 401:
        print(f"[FAILED] Unauthorized (401)")
        print(f"Response: {response.text[:500]}")
    else:
        print(f"[WARNING] Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"[FAILED] Error: {e}")

# Test 2: Try to fetch a specific ticket
print("\n" + "=" * 70)
print("TEST 2: Fetch Specific Ticket (FWDEV-209037)")
print("=" * 70)

try:
    jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_api_token))
    
    print(f"\nAttempting to fetch: FWDEV-209037")
    issue = jira.issue("FWDEV-209037")
    
    print(f"[SUCCESS] Ticket found!")
    print(f"  Key: {issue.key}")
    print(f"  Title: {issue.fields.summary}")
    print(f"  Status: {issue.fields.status.name}")
    
except Exception as e:
    error_str = str(e)
    print(f"[FAILED] Error: {e}")
    
    if "401" in error_str:
        print("\n  -> This is an AUTHENTICATION issue")
        print("  -> Your API token may be:")
        print("     1. Expired - generate a new one")
        print("     2. Revoked - check in Atlassian settings")
        print("     3. Invalid - verify you copied it correctly")
    elif "404" in error_str:
        print("\n  -> This is a NOT FOUND issue")
        print("  -> The ticket might not exist or you don't have access")
    else:
        print(f"\n  -> Different error type: {type(e).__name__}")

# Test 3: List projects to verify access
print("\n" + "=" * 70)
print("TEST 3: List Available Projects")
print("=" * 70)

try:
    jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_api_token))
    projects = jira.projects()
    
    print(f"\n[SUCCESS] Found {len(projects)} projects")
    print("Available projects:")
    for project in projects[:10]:  # Show first 10
        print(f"  - {project.key}: {project.name}")
    
    if len(projects) > 10:
        print(f"  ... and {len(projects) - 10} more")
    
    # Check if FWDEV project exists
    fwdev_found = any(p.key == 'FWDEV' for p in projects)
    if fwdev_found:
        print(f"\n[SUCCESS] FWDEV project is accessible!")
    else:
        print(f"\n[WARNING] FWDEV project not found in your accessible projects")
        
except Exception as e:
    print(f"[FAILED] Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)

print("""
If TEST 1 fails (401):
  -> Your API token is invalid/expired
  -> Generate a new one: https://id.atlassian.com/manage-profile/security/api-tokens

If TEST 2 fails with 404:
  -> Ticket doesn't exist or you don't have access
  -> Check in browser: https://amd.atlassian.net/browse/FWDEV-209037

If TEST 3 shows no FWDEV project:
  -> You don't have access to that project
  -> Ask your admin to add you to the project
""")
