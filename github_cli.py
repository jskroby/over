
#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from github_upload import upload_to_github

# Load environment variables
load_dotenv()

def main():
    """
    Command-line interface for GitHub operations
    """
    print("GitHub CLI Tool")
    print("==============")
    
    # Check if token is provided as argument or in environment
    github_token = os.getenv('GITHUB_TOKEN')
    
    if len(sys.argv) > 1 and sys.argv[1].startswith('ghp_'):
        github_token = sys.argv[1]
        os.environ['GITHUB_TOKEN'] = github_token
        print("Token provided via command line")
        
        # Save token to .env if it doesn't exist
        try:
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write(f"GITHUB_TOKEN='{github_token}'")
                print("Token saved to .env file")
            else:
                with open('.env', 'r') as f:
                    if 'GITHUB_TOKEN' not in f.read():
                        with open('.env', 'a') as f:
                            f.write(f"\nGITHUB_TOKEN='{github_token}'")
                        print("Token saved to .env file")
        except Exception as e:
            print(f"Warning: Could not save token to .env file: {e}")
    
    if not github_token:
        print("No GitHub token found. Please provide a token using:")
        print("  python github_cli.py YOUR_TOKEN")
        print("Or set the GITHUB_TOKEN environment variable")
        return
    
    # Run the upload function
    upload_to_github()

if __name__ == "__main__":
    main()
