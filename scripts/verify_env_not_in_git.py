#!/usr/bin/env python3
"""
Verify that .env is not tracked by Git
"""
import subprocess
import sys

def check_env_in_git():
    """Check if .env is tracked by Git"""
    try:
        # Check if .env is in Git index
        result = subprocess.run(
            ["git", "ls-files", ".env"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout.strip():
            print("❌ ERROR: .env is still tracked by Git!")
            print("\nTo fix this, run:")
            print("  git rm --cached .env")
            print("  git commit -m 'Remove .env from repository'")
            print("  git push origin main")
            return False
        else:
            print("✅ SUCCESS: .env is NOT tracked by Git")
            print("\nYour .env file will not be deployed to Railway.")
            print("Railway will use the environment variables you set in the dashboard.")
            return True
            
    except FileNotFoundError:
        print("❌ ERROR: Git is not installed or not in PATH")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = check_env_in_git()
    sys.exit(0 if success else 1)
