#!/usr/bin/env python3
"""
Simple Command Runner - Natural Language Terminal Helper

A user-friendly command runner that understands common developer commands
without requiring flags or complex syntax. Just type what you want to do!

Usage:
    python command_runner.py "git push"
    python command_runner.py "run app.py"
    python command_runner.py "list files"
"""

import subprocess
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Command history file
HISTORY_FILE = Path.home() / ".cmd_history"

# Common command mappings
COMMAND_PATTERNS = {
    # Git commands
    r"^git\s+push": ("git push", "Push changes to remote"),
    r"^git\s+pull": ("git pull", "Pull changes from remote"),
    r"^git\s+commit": ("git commit -m", "Commit changes (add message)"),
    r"^git\s+add": ("git add", "Stage files for commit"),
    r"^git\s+status": ("git status", "Show working tree status"),
    r"^git\s+log": ("git log --oneline -10", "Show recent commits"),
    r"^git\s+branch": ("git branch -a", "List all branches"),
    r"^git\s+checkout": ("git checkout", "Switch branches"),
    r"^git\s+merge": ("git merge", "Merge branches"),
    r"^git\s+stash": ("git stash", "Stash changes"),
    r"^git\s+diff": ("git diff", "Show changes"),
    
    # Python commands
    r"^run\s+(.+\.py)$": ("python {0}", "Run Python file"),
    r"^python\s+(.+\.py)$": ("python {0}", "Run Python file"),
    r"^pip\s+install": ("pip install", "Install Python package"),
    r"^pip\s+list": ("pip list", "List installed packages"),
    r"^pip\s+freeze": ("pip freeze", "Show installed packages"),
    
    # Node commands
    r"^npm\s+start": ("npm start", "Start Node app"),
    r"^npm\s+run\s+(\w+)$": ("npm run {0}", "Run npm script"),
    r"^npm\s+install": ("npm install", "Install npm packages"),
    r"^node\s+(.+)$": ("node {0}", "Run Node file"),
    
    # File operations
    r"^list\s+(files|dir|directory)$": ("ls -la", "List files in detail"),
    r"^list$": ("ls -la", "List files"),
    r"^ls$": ("ls -la", "List files"),
    r"^dir$": ("ls -la", "List files"),
    r"^show\s+(files|dir)$": ("ls -la", "List files"),
    r"^what\s+files$": ("ls -la", "List files"),
    r"^ls\s+(.+)$": ("ls -la {0}", "List files in directory"),
    
    # Directory navigation
    r"^cd\s+(.+)$": ("cd {0}", "Change directory"),
    r"^go\s+to\s+(.+)$": ("cd {0}", "Change directory"),
    r"^change\s+dir.*\s+(.+)$": ("cd {0}", "Change directory"),
    r"^home$": ("cd ~", "Go to home directory"),
    r"^back$": ("cd -", "Go to previous directory"),
    
    # File viewing
    r"^cat\s+(.+)$": ("cat {0}", "Display file contents"),
    r"^show\s+(.+)$": ("cat {0}", "Display file contents"),
    r"^view\s+(.+)$": ("cat {0}", "Display file contents"),
    r"^read\s+(.+)$": ("cat {0}", "Display file contents"),
    
    # Search
    r"^find\s+(.+)$": ("find . -name '{0}'", "Find files"),
    r"^search\s+(.+)$": ("grep -r '{0}' .", "Search in files"),
    r"^grep\s+(.+)$": ("grep -r '{0}' .", "Search in files"),
    
    # Process management
    r"^ps$": ("ps aux", "Show running processes"),
    r"^top$": ("htop", "Show system monitor"),
    r"^kill\s+(\d+)$": ("kill {0}", "Kill process"),
    
    # System info
    r"^whoami$": ("whoami", "Show current user"),
    r"^pwd$": ("pwd", "Show current directory"),
    r"^where\s+am\s+i$": ("pwd", "Show current directory"),
    r"^date$": ("date", "Show current date/time"),
    r"^uptime$": ("uptime", "Show system uptime"),
    
    # Utility
    r"^clear$": ("clear", "Clear terminal"),
    r"^help$": ("help", "Show help"),
    r"^history$": ("history", "Show command history"),
    
    # Docker
    r"^docker\s+ps$": ("docker ps", "List running containers"),
    r"^docker\s+logs\s+(\w+)$": ("docker logs {0}", "Show container logs"),
    r"^docker\s+stop\s+(\w+)$": ("docker stop {0}", "Stop container"),
    r"^docker\s+start\s+(\w+)$": ("docker start {0}", "Start container"),
    
    # Skills commands
    r"^skills\s+list$": ("python -m skills.cli list", "List all available skills"),
    r"^skills\s+list\s+([\w-]+)$": ("python -m skills.cli list -c {0}", "List skills in category"),
    r"^skills\s+search\s+(.+)$": ("python -m skills.cli search '{0}'", "Search skills"),
    r"^skills\s+show\s+([\w-]+)$": ("python -m skills.cli show {0}", "Show skill details"),
    r"^skills\s+content\s+([\w-]+)$": ("python -m skills.cli content {0}", "Show skill SKILL.md content"),
    r"^skills\s+content\s+([\w-]+)\s+(\w+)$": ("python -m skills.cli content {0} {1}", "Show skill file content"),
    r"^skills\s+categories$": ("python -m skills.cli categories", "List all skill categories"),
    r"^skills\s+in-category\s+([\w-]+)$": ("python -m skills.cli in-category {0}", "List skills in category"),
    r"^skills\s+reload$": ("python -m skills.cli reload", "Reload skills from disk"),
}

# Common workflows with multiple commands
WORKFLOWS = {
    "new feature": [
        ("git checkout -b feature/new", "Create new branch"),
        ("git add .", "Stage all changes"),
        ("git commit -m 'Add new feature'", "Commit changes"),
    ],
    "save work": [
        ("git add .", "Stage all changes"),
        ("git commit -m 'Save work'", "Commit changes"),
    ],
    "update": [
        ("git pull origin main", "Pull latest changes"),
    ],
    "deploy": [
        ("git add .", "Stage all changes"),
        ("git commit -m 'Deploy'", "Commit changes"),
        ("git push origin main", "Push to remote"),
    ],
}


class CommandRunner:
    """Natural language command runner."""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.load_history()
    
    def load_history(self) -> None:
        """Load command history from file."""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.history = eval(f.read())
            except:
                self.history = []
    
    def save_history(self) -> None:
        """Save command history to file."""
        try:
            with open(HISTORY_FILE, 'w') as f:
                f.write(str(self.history))
        except:
            pass
    
    def add_to_history(self, command: str, success: bool, output: str = "") -> None:
        """Add command to history."""
        self.history.append({
            "command": command,
            "success": success,
            "output": output[:200] if output else "",  # Truncate long output
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 100 commands
        self.history = self.history[-100:]
        self.save_history()
    
    def parse_command(self, user_input: str) -> Tuple[Optional[str], str, Optional[str]]:
        """
        Parse natural language input into an actual command.
        
        Returns:
            Tuple of (command, description, error_message)
        """
        user_input = user_input.strip()
        
        # Direct command match
        for pattern, (cmd, desc) in COMMAND_PATTERNS.items():
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    command = cmd.format(*groups) if groups else cmd
                except IndexError:
                    command = cmd
                return command, desc, None
        
        # Check for workflows
        if user_input.lower() in WORKFLOWS:
            return None, f"Workflow: {user_input}", "WORKFLOW"
        
        # Try as a direct shell command
        if self.is_safe_command(user_input):
            return user_input, "Direct command", None
        
        # No match found
        return None, "", "UNKNOWN"
    
    def is_safe_command(self, cmd: str) -> bool:
        """Check if command is safe to run."""
        dangerous = ["rm -rf", "mkfs", "dd if=", "> /dev/sd", "chmod 777"]
        cmd_lower = cmd.lower()
        return not any(d in cmd_lower for d in dangerous)
    
    def find_git_root(self) -> Optional[str]:
        """Find the nearest git repository parent directory."""
        # Start from script location AND current working directory
        search_paths = [Path.cwd()]
        
        # Try to find script location
        import sys
        if sys.argv and sys.argv[0]:
            script_path = Path(sys.argv[0]).resolve()
            search_paths.insert(0, script_path.parent)
        
        for start_path in search_paths:
            current = start_path
            # Limit search to prevent infinite loops
            for _ in range(10):
                if (current / '.git').exists():
                    return str(current)
                if current == current.parent:
                    break
                current = current.parent
        
        return None
    
    def run_workflow(self, workflow_name: str) -> List[Dict]:
        """Run a multi-command workflow."""
        results = []
        commands = WORKFLOWS.get(workflow_name.lower(), [])
        
        for cmd, desc in commands:
            result = self.execute(cmd, desc)
            results.append(result)
            if not result["success"]:
                break  # Stop on first failure
        
        return results
    
    def execute(self, command: str, description: str = "") -> Dict:
        """Execute a command and return the result."""
        print(f"\n▶ {command}")
        if description:
            print(f"  └─ {description}")
        
        try:
            # Auto-detect git directory for git commands
            cwd = os.getcwd()
            if command.strip().startswith('git '):
                git_root = self.find_git_root()
                if git_root and git_root != cwd:
                    print(f"  └─ 📁 Switching to git repo: {git_root}")
                    cwd = git_root
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd
            )
            
            output = result.stdout + result.stderr
            
            success = result.returncode == 0
            
            self.add_to_history(command, success, output)
            
            return {
                "command": command,
                "description": description,
                "success": success,
                "output": output,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            error = "Command timed out after 60 seconds"
            self.add_to_history(command, False, error)
            return {
                "command": command,
                "description": description,
                "success": False,
                "output": error,
                "returncode": -1
            }
        except Exception as e:
            error = f"Error: {str(e)}"
            self.add_to_history(command, False, error)
            return {
                "command": command,
                "description": description,
                "success": False,
                "output": error,
                "returncode": -1
            }
    
    def format_result(self, result: Dict) -> str:
        """Format command result for display."""
        output = result["output"]
        
        if not output:
            return "✓ Command completed successfully (no output)"
        
        # Truncate long output
        if len(output) > 2000:
            output = output[:2000] + f"\n... [output truncated, {len(result['output'])} total chars]"
        
        if result["success"]:
            return output
        else:
            return f"✗ Error (exit code {result['returncode']}):\n{output}"
    
    def get_suggestions(self, partial: str) -> List[str]:
        """Get command suggestions based on partial input."""
        suggestions = []
        
        # From patterns
        for pattern in COMMAND_PATTERNS.keys():
            # Extract example from pattern
            example = pattern.replace("^", "").replace(r"\s+", " ").replace(r"\w+", "xxx")
            if partial.lower() in example.lower():
                suggestions.append(example)
        
        # From workflows
        for workflow in WORKFLOWS.keys():
            if partial.lower() in workflow:
                suggestions.append(f"workflow: {workflow}")
        
        return suggestions[:5]
    
    def run_interactive(self) -> None:
        """Run interactive command loop."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║           🖥️  Simple Command Runner                          ║
║                                                              ║
║  Just type what you want to do! Examples:                   ║
║    • "git push"                                              ║
║    • "run app.py"                                            ║
║    • "list files"                                            ║
║    • "go to src"                                             ║
║    • "workflow: save work"                                  ║
║                                                              ║
║  Type "help" for more options or "quit" to exit            ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        while True:
            try:
                user_input = input("\n💬 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == "help":
                    self.show_help()
                    continue
                
                if user_input.lower() == "history":
                    self.show_history()
                    continue
                
                # Parse the command
                command, description, error = self.parse_command(user_input)
                
                if error == "WORKFLOW":
                    print(f"\n📋 Running workflow: {description}")
                    results = self.run_workflow(user_input)
                    for r in results:
                        print(self.format_result(r))
                    continue
                
                if error == "UNKNOWN":
                    suggestions = self.get_suggestions(user_input)
                    print(f"\n❓ I didn't understand: '{user_input}'")
                    if suggestions:
                        print("Did you mean:")
                        for s in suggestions:
                            print(f"  • {s}")
                    else:
                        print("Try commands like: git push, run app.py, list files, go to folder")
                    continue
                
                # Execute the command
                result = self.execute(command, description)
                print(self.format_result(result))
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def show_help(self) -> None:
        """Show help information."""
        print("""
📖 AVAILABLE COMMANDS:

Git:
  • git push          → Push to remote
  • git pull          → Pull from remote  
  • git commit        → Commit changes
  • git status        → Check status
  • git log           → View recent commits

Python:
  • run app.py        → Run a Python file
  • pip install xyz   → Install package

Files:
  • list / ls         → List files
  • cd folder         → Change directory
  • cat file.txt      → View file

Workflows:
  • workflow: save work     → git add, commit
  • workflow: new feature   → create branch, work, commit
  • workflow: deploy        → add, commit, push

Tips:
  • Type naturally - I'll figure it out!
  • Use "history" to see past commands
  • Use "quit" to exit
        """)
    
    def show_history(self) -> None:
        """Show command history."""
        if not self.history:
            print("No command history yet.")
            return
        
        print("\n📜 Command History:")
        for i, item in enumerate(reversed(self.history[-10:]), 1):
            status = "✓" if item["success"] else "✗"
            print(f"  {i}. {status} {item['command']}")
            print(f"     {item['timestamp'][:19]}")


def main():
    """Main entry point."""
    import sys
    
    runner = CommandRunner()
    
    if len(sys.argv) > 1:
        # Command line mode
        user_input = " ".join(sys.argv[1:])
        
        # Check for workflow prefix
        if user_input.startswith("workflow:"):
            workflow_name = user_input.replace("workflow:", "").strip()
            results = runner.run_workflow(workflow_name)
            for r in results:
                print(runner.format_result(r))
        else:
            # Parse and execute single command
            command, description, error = runner.parse_command(user_input)
            
            if error == "UNKNOWN":
                suggestions = runner.get_suggestions(user_input)
                print(f"❓ Unknown command: '{user_input}'")
                if suggestions:
                    print("Suggestions:")
                    for s in suggestions:
                        print(f"  • {s}")
                sys.exit(1)
            elif error == "WORKFLOW":
                print(f"📋 Running workflow: {description}")
                results = runner.run_workflow(user_input)
                for r in results:
                    print(runner.format_result(r))
            else:
                result = runner.execute(command, description)
                print(runner.format_result(result))
                sys.exit(0 if result["success"] else 1)
    else:
        # Interactive mode
        runner.run_interactive()


if __name__ == "__main__":
    main()
