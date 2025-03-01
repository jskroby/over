
import os
import sys
import requests
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_to_github():
    """Upload the entire repository to GitHub"""
    
    # Get GitHub token from environment variables or prompt user
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        github_token = input("Enter your GitHub personal access token: ")
        
        # Save token to .env file if provided
        if github_token:
            save_token = input("Would you like to save this token for future use? (y/n): ")
            if save_token.lower() == 'y':
                try:
                    with open('.env', 'a+') as env_file:
                        env_file.seek(0)
                        content = env_file.read()
                        if 'GITHUB_TOKEN' not in content:
                            env_file.write(f"\nGITHUB_TOKEN='{github_token}'")
                            print("Token saved to .env file")
                except Exception as e:
                    print(f"Warning: Could not save token to .env file: {e}")
        
    if not github_token:
        print("Error: GitHub token is required")
        return False
        
    # Get repository name from user
    repo_name = input("Enter the repository name to create or use: ")
    if not repo_name:
        print("Error: Repository name is required")
        return False
    
    try:
        # Initialize GitHub client
        g = Github(github_token)
        user = g.get_user()
        
        # Check if repo exists, create if not
        try:
            repo = user.get_repo(repo_name)
            print(f"Repository '{repo_name}' already exists. Will push to existing repository.")
        except:
            repo = user.create_repo(
                repo_name, 
                description="AI Agent System - Multiple agents working together",
                private=False  # Set to True if you want a private repository
            )
            print(f"Created new repository: {repo_name}")
        
        # Get remote URL
        remote_url = f"https://{github_token}@github.com/{user.login}/{repo_name}.git"
        
        # Initialize git repository and push
        commands = [
            "git init",
            "git add .",
            "git config --local user.email 'agent@example.com'",
            "git config --local user.name 'AI Agent'",
            f'git commit -m "Initial commit: AI Agent System"',
            f"git remote add origin {remote_url}",
            "git push -u origin master --force"  # Using --force to overwrite if needed
        ]
        
        for cmd in commands:
            result = os.system(cmd)
            if result != 0:
                if "git push" in cmd:  # Try with main branch if master fails
                    os.system("git push -u origin main --force")
                else:
                    print(f"Error executing: {cmd}")
                    return False
        
        print(f"\nSuccess! Repository uploaded to: https://github.com/{user.login}/{repo_name}")
        return True
        
    except Exception as e:
        print(f"Error uploading to GitHub: {e}")
        return False

if __name__ == "__main__":
    upload_to_github()
