"""Setup script for JIRA Ticket Summarizer Agent"""
import os
import sys
from pathlib import Path

def setup_project():
    """Setup the project environment"""
    print("🚀 JIRA Ticket Summarizer - Setup Wizard\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected\n")
    
    # Create .env if it doesn't exist
    env_path = Path(".env")
    if not env_path.exists():
        print("📝 Creating .env file...")
        jira_url = input("Enter your JIRA URL (e.g., https://company.atlassian.net): ").strip()
        jira_email = input("Enter your JIRA email: ").strip()
        jira_token = input("Enter your JIRA API token: ").strip()
        anthropic_key = input("Enter your Anthropic API key: ").strip()
        
        env_content = f"""# JIRA Configuration
JIRA_URL={jira_url}
JIRA_EMAIL={jira_email}
JIRA_API_TOKEN={jira_token}

# Anthropic API
ANTHROPIC_API_KEY={anthropic_key}
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ .env file created\n")
    else:
        print("✓ .env file already exists\n")
    
    # Create output directory
    output_dir = Path(r"C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready: {output_dir}\n")
    
    # Check input file
    input_file = r"C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx"
    if Path(input_file).exists():
        print(f"✓ Input file found: {input_file}\n")
    else:
        print(f"⚠️  Input file not found: {input_file}")
        print("Please create the Excel file with ticket IDs before running the agent.\n")
    
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Ensure your input Excel file exists at:")
    print(f"   {input_file}")
    print("2. Run the agent with: python jira_agent.py")
    print("3. Check the output at:")
    print(f"   {output_dir}\\ticket_summary.xlsx")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)
