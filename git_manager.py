import subprocess
import sys
import os
from typing import Optional

class GitHubManager:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        
    def run_git_command(self, command: list) -> tuple[bool, str]:
        """Execute a git command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
    
    def check_git_status(self) -> tuple[bool, str]:
        """Check the current git status."""
        return self.run_git_command(["git", "status", "--porcelain"])
    
    def add_all_changes(self) -> tuple[bool, str]:
        """Add all changes to staging area."""
        return self.run_git_command(["git", "add", "."])
    
    def commit_changes(self, message: str) -> tuple[bool, str]:
        """Commit staged changes with a message."""
        return self.run_git_command(["git", "commit", "-m", message])
    
    def push_to_remote(self, branch: str = "main") -> tuple[bool, str]:
        """Push changes to remote repository."""
        return self.run_git_command(["git", "push", "origin", branch])
    
    def pull_from_remote(self, branch: str = "main") -> tuple[bool, str]:
        """Pull changes from remote repository."""
        return self.run_git_command(["git", "pull", "origin", branch])
    
    def get_current_branch(self) -> tuple[bool, str]:
        """Get the current branch name."""
        return self.run_git_command(["git", "branch", "--show-current"])
    
    def push_workflow(self, commit_message: str, branch: Optional[str] = None) -> bool:
        """Complete push workflow: add, commit, and push."""
        if not branch:
            success, branch = self.get_current_branch()
            if not success:
                print(f"Error getting current branch: {branch}")
                return False
        
        # Check if there are changes
        success, status = self.check_git_status()
        if not success:
            print(f"Error checking git status: {status}")
            return False
        
        if not status:
            print("No changes to commit.")
            return True
        
        # Add all changes
        success, output = self.add_all_changes()
        if not success:
            print(f"Error adding changes: {output}")
            return False
        
        # Commit changes
        success, output = self.commit_changes(commit_message)
        if not success:
            print(f"Error committing changes: {output}")
            return False
        
        # Push to remote
        success, output = self.push_to_remote(branch)
        if not success:
            print(f"Error pushing to remote: {output}")
            return False
        
        print(f"Successfully pushed changes to {branch}")
        return True
    
    def pull_workflow(self, branch: Optional[str] = None) -> bool:
        """Complete pull workflow."""
        if not branch:
            success, branch = self.get_current_branch()
            if not success:
                print(f"Error getting current branch: {branch}")
                return False
        
        success, output = self.pull_from_remote(branch)
        if not success:
            print(f"Error pulling from remote: {output}")
            return False
        
        print(f"Successfully pulled changes from {branch}")
        return True

def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python git_manager.py [push|pull] [options]")
        print("  push <commit_message> [branch]")
        print("  pull [branch]")
        return
    
    manager = GitHubManager()
    command = sys.argv[1].lower()
    
    if command == "push":
        if len(sys.argv) < 3:
            print("Error: Commit message required for push")
            return
        
        commit_message = sys.argv[2]
        branch = sys.argv[3] if len(sys.argv) > 3 else None
        manager.push_workflow(commit_message, branch)
    
    elif command == "pull":
        branch = sys.argv[2] if len(sys.argv) > 2 else None
        manager.pull_workflow(branch)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()